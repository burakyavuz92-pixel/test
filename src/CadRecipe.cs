using System.Text.Json;
using System.Text.Json.Nodes;

// Unified, non-executable recipe; no product-family switch or formula strings.
public static class CadRecipe
{
    public static readonly HashSet<string> Operations=new(){"sketch","extrude","revolve","cylinder","cut","fuse","hole","circularPattern","linearPattern","fillet","chamfer","join"};
    public static JsonElement Resolve(JsonElement plan,Dictionary<string,string> row)
    {
        if(plan.GetProperty("schemaVersion").GetInt32()!=6)throw new Exception("CAD recipe v6 gerekli; önceki tarif sürümü otomatik dönüştürülmez.");
        var parameters=plan.GetProperty("parameters").EnumerateArray().ToDictionary(p=>p.GetProperty("id").GetString()!);
        var values=new Dictionary<string,double?>();var visiting=new HashSet<string>();
        double? Eval(string id)
        {
            if(values.TryGetValue(id,out var value))return value;
            if(!parameters.TryGetValue(id,out var p))throw new Exception("Bilinmeyen parametre: "+id);
            if(!visiting.Add(id))throw new Exception("Döngüsel parametre: "+id);
            var source=p.GetProperty("source");string kind=source.GetProperty("kind").GetString()!;
            value=kind switch {
                "column"=>row.TryGetValue(source.GetProperty("column").GetString()!,out var text)?text.Length==0?null:GroupWorkflow.Value(text):throw new Exception("Excel sütunu bulunamadı."),
                "constant"=>source.GetProperty("value").GetDouble(),
                "derived"=>Derived(p,source),
                _=>throw new Exception("Parametre kaynağı desteklenmiyor: "+kind)
            };
            if(value.HasValue&&p.GetProperty("unit").GetString()=="count"&&(value<0||value!=Math.Truncate(value.Value)))throw new Exception("Adet tam ve negatif olmayan sayı olmalı.");
            if(value.HasValue&&!double.IsFinite(value.Value))throw new Exception("Sonlu olmayan parametre: "+id);
            visiting.Remove(id);values[id]=value;return value;
        }
        double? Derived(JsonElement p,JsonElement source)
        {
            var args=source.GetProperty("args").EnumerateArray().Select(x=>x.GetString()!).ToArray();
            if(args.Length!=2)throw new Exception("Türetilmiş parametre iki girdi ister.");
            foreach(var id in args)if(!parameters.ContainsKey(id))throw new Exception("Bilinmeyen türetme girdisi: "+id);
            string op=source.GetProperty("op").GetString()!,unit=p.GetProperty("unit").GetString()!;
            string u0=parameters[args[0]].GetProperty("unit").GetString()!,u1=parameters[args[1]].GetProperty("unit").GetString()!;
            bool dimensionless(string u)=>u is "scalar" or "count";
            bool valid=op switch {"add" or "subtract"=>u0==u1&&unit==u0,"multiply"=>dimensionless(u0)&&unit==u1||dimensionless(u1)&&unit==u0,"divide"=>dimensionless(u1)&&unit==u0||u0==u1&&unit=="scalar",_=>false};
            if(!valid)throw new Exception("Geçersiz işlem/birim birleşimi: "+op);
            double? a=Eval(args[0]),b=Eval(args[1]);if(a is null||b is null)return null;
            return op switch {"add"=>a+b,"subtract"=>a-b,"multiply"=>a*b,"divide"=>b==0?throw new Exception("Sıfıra bölme."):a/b,_=>throw new Exception("Geçersiz türetme işlemi.")};
        }
        foreach(var p in parameters.Values)
        {
            string unit=p.GetProperty("unit").GetString()!;if(unit is not ("mm" or "deg" or "count" or "scalar"))throw new Exception("Geçersiz parametre birimi.");Eval(p.GetProperty("id").GetString()!);
        }
        JsonNode? Bind(JsonElement element)
        {
            if(element.ValueKind==JsonValueKind.Object)
            {
                if(element.TryGetProperty("param",out var reference))
                {
                    if(element.EnumerateObject().Count()!=1)throw new Exception("Parametre referansı ek alan içeremez.");
                    return JsonValue.Create(Eval(reference.GetString()!)??throw new Exception("Aktif işlem boş parametre kullanıyor: "+reference.GetString()));
                }
                var obj=new JsonObject();foreach(var kv in element.EnumerateObject())obj[kv.Name]=Bind(kv.Value);return obj;
            }
            if(element.ValueKind==JsonValueKind.Array){var a=new JsonArray();foreach(var x in element.EnumerateArray())a.Add(Bind(x));return a;}
            return JsonNode.Parse(element.GetRawText());
        }
        var frames=plan.GetProperty("frames").EnumerateArray().ToDictionary(f=>f.GetProperty("id").GetString()!);
        var resolvedFrames=new JsonArray();
        foreach(var f in frames.Values)
        {
            var bound=JsonSerializer.SerializeToElement(Bind(f));
            double[] Vector(string key)=>bound.GetProperty(key).EnumerateArray().Select(x=>x.GetDouble()).ToArray();
            double[] o=Vector("origin"),x=Vector("xAxis"),z=Vector("zAxis");
            if(o.Length!=3||x.Length!=3||z.Length!=3||o.Concat(x).Concat(z).Any(v=>!double.IsFinite(v))||Math.Abs(x.Sum(v=>v*v)-1)>1e-3||Math.Abs(z.Sum(v=>v*v)-1)>1e-3||Math.Abs(x.Zip(z).Sum(v=>v.First*v.Second))>1e-3)throw new Exception("Geçersiz referans bazı.");
            double nx=Math.Sqrt(x.Sum(v=>v*v));x=x.Select(v=>v/nx).ToArray();double dot=x.Zip(z).Sum(v=>v.First*v.Second);z=z.Select((v,i)=>v-dot*x[i]).ToArray();double nz=Math.Sqrt(z.Sum(v=>v*v));z=z.Select(v=>v/nz).ToArray();
            var normalized=JsonNode.Parse(bound.GetRawText())!;normalized["xAxis"]=JsonSerializer.SerializeToNode(x);normalized["zAxis"]=JsonSerializer.SerializeToNode(z);normalized["basisNormalizationApplied"]=Math.Abs(nx-1)>1e-12||Math.Abs(nz-1)>1e-12||Math.Abs(dot)>1e-12;resolvedFrames.Add(normalized);
        }
        var ops=plan.GetProperty("operations").EnumerateArray().ToDictionary(o=>o.GetProperty("id").GetString()!);var done=new HashSet<string>();var stack=new HashSet<string>();var resolved=new JsonArray();var active=new Dictionary<string,bool>();var featureApplied=new Dictionary<string,bool>();
        void Visit(string id)
        {
            if(done.Contains(id))return;
            if(!ops.TryGetValue(id,out var op))throw new Exception("Bilinmeyen işlem: "+id);
            if(!stack.Add(id))throw new Exception("Döngüsel işlem bağımlılığı.");
            string name=op.GetProperty("op").GetString()!;
            if(!Operations.Contains(name))throw new NotSupportedException("İşlem sözleşmede yok: "+name);
            if(!frames.ContainsKey(op.GetProperty("frame").GetString()!))throw new Exception("İşlem referans bazı bilinmiyor.");
            var condition=op.GetProperty("when");bool present=condition.GetProperty("kind").GetString() switch {"always"=>true,"columnPresent"=>row[condition.GetProperty("column").GetString()!].Length>0,"parameterPositive"=>Eval(condition.GetProperty("parameter").GetString()!) is double v&&v>1e-8,_=>throw new Exception("Geçersiz varlık koşulu.")};
            bool modifies=name is "hole" or "fillet" or "chamfer" or "cut" or "join";
            string? target=op.TryGetProperty("target",out var targetNode)&&targetNode.ValueKind==JsonValueKind.String?targetNode.GetString():null;
            string? tool=op.TryGetProperty("tool",out var toolNode)&&toolNode.ValueKind==JsonValueKind.String?toolNode.GetString():null;
            var inputs=op.GetProperty("inputs").EnumerateArray().Select(i=>i.GetString()!).ToArray();
            var optional=op.TryGetProperty("optionalInputs",out var optionalList)?optionalList.EnumerateArray().Select(x=>x.GetString()!).ToHashSet():new HashSet<string>();
            if(name=="join")
            {
                if(target is null||tool is not null||inputs.Length==0||optional.Count!=0)throw new Exception("İç birleşim ana gövde ve ek gövdeler ister.");
                Visit(target);foreach(var input in inputs)Visit(input);
                if(!active[target])throw new Exception("Birleşim ana gövdesi mevcut değil.");
                present=present&&inputs.Any(i=>active[i]);
            }
            else if(modifies)
            {
                if(target is null||inputs.Length!=0||optional.Count!=0||(name=="cut"?tool is null:tool is not null))throw new Exception("Gövde değiştirme işlemi tek target kullanmalı; inputs/optionalInputs boş olmalı: "+id);
                Visit(target);if(tool is not null)Visit(tool);
                if(!active[target])throw new Exception("Hedef gövde mevcut değil: "+target);
                if(present&&tool is not null&&!active[tool])throw new Exception("Aktif kesmenin aracı mevcut değil.");
            }
            else
            {
                if(target is not null||tool is not null)throw new Exception("Oluşturma/çoğaltma işlemi target/tool kullanamaz.");
                if(optional.Count>0&&name!="fuse"||optional.Any(i=>!inputs.Contains(i)))throw new Exception("Opsiyonel inputs yalnız fuse için geçerli.");
                foreach(var input in inputs)Visit(input);
                if(present&&inputs.Any(i=>!active[i]&&!optional.Contains(i)))throw new Exception("Aktif işlem olmayan girdiye bağlı: "+id);
                int arity=inputs.Length;
                if(name is "sketch" or "cylinder"?arity!=0:name=="fuse"?arity<1:arity!=1)throw new Exception("Geçersiz işlem girdi sayısı: "+id);
                if(name is "extrude" or "revolve"&&ops[inputs[0]].GetProperty("op").GetString()!="sketch")throw new Exception("Profil işlemi sketch girdisi bekler.");
                if(present&&name=="fuse"&&!inputs.Any(i=>active[i]))throw new Exception("Birleştirme için aktif girdi yok.");
            }
            string[] required=name switch {"sketch"=>["plane","loops"],"extrude"=>["length","direction"],"revolve"=>["axisOrigin","axisDirection","angleDeg"],"cylinder"=>["diameter","length","origin","direction"],"hole"=>["diameter","origin","direction","throughAll","depth"],"circularPattern"=>["count","pitchDiameter","startAngleDeg","totalAngleDeg","center","axis"],"linearPattern"=>["count","spacing","direction"],"fillet" or "chamfer"=>["size","selectors"],_=>[]};
            foreach(string field in required)if(!op.GetProperty("args").TryGetProperty(field,out _))throw new Exception(id+": işlem alanı eksik: "+field);
            active[id]=modifies||present;featureApplied[id]=present;
            if(modifies&&!present)
                resolved.Add(new JsonObject{["id"]=id,["op"]="passThrough",["target"]=target,["featureApplied"]=false});
            else if(present)
                resolved.Add(new JsonObject{["id"]=id,["op"]=name,["frame"]=op.GetProperty("frame").GetString(),["target"]=target,["tool"]=tool,["inputs"]=JsonSerializer.SerializeToNode(inputs.Where(i=>active[i]).ToArray()),["featureApplied"]=true,["args"]=Bind(op.GetProperty("args"))});
            done.Add(id);stack.Remove(id);
        }
        foreach(var id in ops.Keys)Visit(id);
        string output=plan.GetProperty("result").GetString()!;if(!active.TryGetValue(output,out var exists)||!exists)throw new Exception("Sonuç işlemi yok/aktif değil.");
        var dimensionIds=new HashSet<string>();var dimensions=new JsonArray();
        foreach(var d in plan.GetProperty("dimensions").EnumerateArray())
        {
            if(!dimensionIds.Add(d.GetProperty("id").GetString()!))throw new Exception("Tekrarlı ölçü kimliği.");
            var param=d.GetProperty("parameter").GetString()!;if(!parameters.ContainsKey(param))throw new Exception("Ölçü parametresi bilinmiyor.");
            foreach(var t in d.GetProperty("targets").EnumerateArray())if(!ops.ContainsKey(t.GetProperty("operation").GetString()!))throw new Exception("Ölçü hedefi bilinmiyor.");
            string color=d.GetProperty("sourceColor").GetString()!;if(color is not ("black" or "green"))throw new Exception("Geçersiz ölçü kaynak rengi.");
            var targets=d.GetProperty("targets").EnumerateArray().ToArray();if(targets.Any(t=>!featureApplied[t.GetProperty("operation").GetString()!]))continue;
            var copy=JsonNode.Parse(d.GetRawText())!;if(values[param] is null)throw new Exception("Aktif ölçü boş parametre kullanıyor.");
            var hide=d.GetProperty("hideIf");bool hidden=hide.GetProperty("kind").GetString() switch {"never"=>false,"zero"=>Math.Abs(values[param]!.Value)<1e-8,"equalsScaledParameter"=>values.TryGetValue(hide.GetProperty("parameter").GetString()!,out var other)&&other.HasValue?Math.Abs(values[param]!.Value-other.Value*hide.GetProperty("factor").GetDouble())<1e-8:throw new Exception("Gizleme parametresi yok/boş."),_=>throw new Exception("Geçersiz gizleme koşulu.")};
            copy["effectiveVisible"]=color!="green"&&d.GetProperty("visible").GetBoolean()&&!hidden;copy["nominal"]=values[param];dimensions.Add(copy);
        }
        foreach(var column in ExcelModelInput.Build(new[]{row}).rows[0].cells.Where(c=>c.Value.state=="number").Select(c=>c.Key))
            if(!parameters.Values.Any(p=>p.GetProperty("source").GetProperty("kind").GetString()=="column"&&p.GetProperty("source").GetProperty("column").GetString()==column))throw new Exception("Excel ölçüsü parametreye bağlanmadı: "+column);
        foreach(var section in plan.GetProperty("sections").EnumerateArray())foreach(var target in section.GetProperty("targets").EnumerateArray())if(!ops.ContainsKey(target.GetString()!))throw new Exception("Kesit hedefi bilinmiyor.");
        var sections=new JsonArray();
        foreach(var section in plan.GetProperty("sections").EnumerateArray())
        {
            var copy=JsonNode.Parse(section.GetRawText())!;copy["targets"]=JsonSerializer.SerializeToNode(section.GetProperty("targets").EnumerateArray().Select(t=>t.GetString()!).Where(id=>featureApplied[id]).ToArray());sections.Add(copy);
        }
        var tolerances=new JsonArray();
        foreach(var tol in plan.GetProperty("geometricTolerances").EnumerateArray())
        {
            var ids=tol.GetProperty("targets").EnumerateArray().Select(t=>t.GetProperty("operation").GetString()!).ToArray();
            if(ids.Any(id=>!ops.ContainsKey(id)))throw new Exception("Geometrik tolerans hedefi bilinmiyor.");
            if(ids.All(id=>featureApplied[id]))tolerances.Add(Bind(tol));
        }
        return JsonSerializer.SerializeToElement(new{schemaVersion=6,outputId=row["jpeg file name"],parameters=values,frames=resolvedFrames,operations=resolved,result=output,featureApplied,views=plan.GetProperty("views"),dimensions,sections,geometricTolerances=tolerances,executionStatus="recipe-resolved-not-rendered"});
    }
    public static List<WorkflowIssue> Check(JsonElement plan,List<Dictionary<string,string>> rows)
    {
        var issues=new List<WorkflowIssue>();
        if(plan.TryGetProperty("issues",out var reported))foreach(var item in reported.EnumerateArray())issues.Add((item.Deserialize<WorkflowIssue>(WorkflowReports.Json)??throw new Exception("Geçersiz sorun kaydı.")) with{Origin="model"});
        if(plan.TryGetProperty("questions",out _))issues.Add(new("QUESTION_PROTOCOL","protocol","error","Model soru alanı döndürdü.",[],"Soru yerine rapor gerekli."));
        foreach(var row in rows)try{Resolve(plan,row);}catch(Exception ex){issues.Add(new("RECIPE_VALIDATION",ex is NotSupportedException?"software":"model","error",row["jpeg file name"]+": "+ex.Message,[row["jpeg file name"]],"Tarif veya desteklenen işlem sözleşmesi incelenmeli."));}
        return issues;
    }
}
