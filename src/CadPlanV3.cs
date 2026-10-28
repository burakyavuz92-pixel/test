using System.Text.Json;
using System.Text.Json.Nodes;
using System.Globalization;

// Explicit relationships define nominal geometry. Annotation visibility cannot change it.
public static class CadPlanV3
{
    public static (JsonElement Plan,Dictionary<string,string> Row) Bind(JsonElement source,Dictionary<string,string> row)
    {
        if(source.GetProperty("schemaVersion").GetInt32()!=3)throw new Exception("Şema v3 gerekli.");
        var geometry=source.GetProperty("geometry");var annotation=source.GetProperty("annotations");
        var features=geometry.GetProperty("holes").EnumerateArray().ToDictionary(h=>h.GetProperty("id").GetString()!);
        var values=new Dictionary<string,string>(row,StringComparer.OrdinalIgnoreCase);var solved=new Dictionary<string,double>();var visiting=new HashSet<string>();
        double Solve(string id,string axis)
        {
            if(id=="origin")return 0;
            string key=id+":"+axis;if(solved.TryGetValue(key,out var result))return result;
            if(!visiting.Add(key))throw new Exception("Döngüsel geometri ilişkisi: "+key);
            if(!features.TryGetValue(id,out var hole))throw new Exception("Bilinmeyen özellik: "+id);
            var binding=hole.GetProperty("position").GetProperty(axis);string kind=binding.GetProperty("kind").GetString()!;
            result=kind switch {
                "origin"=>0,
                "offset"=>Offset(binding,axis),
                _=>throw new Exception("Desteklenmeyen konum ilişkisi: "+kind)
            };
            visiting.Remove(key);solved[key]=result;return result;
        }
        double Offset(JsonElement binding,string axis)
        {
            string reference=binding.GetProperty("reference").GetString()!,column=binding.GetProperty("column").GetString()!;
            int sign=binding.GetProperty("sign").GetInt32();if(sign is not (1 or -1))throw new Exception("Konum yönü +1/-1 olmalı.");
            if(reference!="origin"&&features.TryGetValue(reference,out var target)&&Absent(target))throw new Exception("Geometri olmayan özelliğe bağlı: "+reference);
            return Solve(reference,axis)+sign*GroupWorkflow.Value(row[column]);
        }
        bool Absent(JsonElement h)=>h.GetProperty("presentIfColumn").ValueKind==JsonValueKind.String&&row[h.GetProperty("presentIfColumn").GetString()!].Length==0;
        var holes=new List<object>();var active=new HashSet<string>();int n=0;
        foreach(var (id,hole) in features)
        {
            if(Absent(hole))continue;active.Add(id);
            string x="__x"+n,y="__y"+n;n++;
            values[x]=Solve(id,"x").ToString("R",CultureInfo.InvariantCulture);values[y]=Solve(id,"y").ToString("R",CultureInfo.InvariantCulture);
            // Signed solved coordinates use __n columns after moving sign outside the restricted evaluator.
            string Expr(string key){double v=double.Parse(values[key],CultureInfo.InvariantCulture);values[key]=Math.Abs(v).ToString("R",CultureInfo.InvariantCulture);return v<0?"-"+key:key;}
            holes.Add(new{id,diameterExpression=hole.GetProperty("diameterColumn").GetString(),xExpression=Expr(x),yExpression=Expr(y),presentIfColumn=(string?)null});
        }
        var dimensions=new List<object>();
        foreach(var dim in annotation.GetProperty("dimensions").EnumerateArray())
        {
            string feature=dim.GetProperty("feature").GetString()!,column=dim.GetProperty("column").GetString()!;
            if(feature!="body"&&feature.Split(':').Any(id=>!active.Contains(id)))continue;
            var condition=dim.GetProperty("hideIf");bool hidden=condition.GetProperty("kind").GetString() switch {
                "never"=>false,
                "zero"=>Math.Abs(GroupWorkflow.Value(row[column]))<1e-8,
                "equalsScaledColumn"=>Math.Abs(GroupWorkflow.Value(row[column])-GroupWorkflow.Value(row[condition.GetProperty("column").GetString()!])*condition.GetProperty("factor").GetDouble())<1e-8,
                _=>throw new Exception("Desteklenmeyen gösterim koşulu.")
            };
            dimensions.Add(new{id=dim.GetProperty("id").GetString(),kind=dim.GetProperty("kind").GetString(),feature,column,visible=dim.GetProperty("visible").GetBoolean()&&!hidden,hideWhen="never"});
        }
        var section=source.GetProperty("section");
        if(section.GetProperty("mode").GetString()!="parallel-through-features"||section.GetProperty("travelAxis").GetString()!="Y")throw new Exception("Bu kesit yolu desteklenmiyor; yalnızca Y boyunca paralel özellik kesitleri desteklenir.");
        var targets=section.GetProperty("featureIds").EnumerateArray().Select(x=>x.GetString()!).ToArray();
        if(targets.Any(id=>!features.ContainsKey(id)))throw new Exception("Bilinmeyen kesit hedefi.");
        var activeTargets=targets.Where(active.Contains).ToArray();
        if(activeTargets.Length==0)throw new Exception("Aktif kesit hedefi yok.");
        var normalized=new{schemaVersion=2,kind=geometry.GetProperty("kind").GetString(),parameters=new{outerDiameterExpression=geometry.GetProperty("outerDiameterColumn").GetString(),depthMm=geometry.GetProperty("depthMm").GetDouble(),thicknessMm=geometry.GetProperty("thicknessMm").GetDouble(),outerRadiusMm=geometry.GetProperty("outerRadiusMm").GetDouble()},holes,camera=source.GetProperty("camera"),section=new{mode="through-features",featureIds=activeTargets,label=section.TryGetProperty("label",out var label)?label.GetString():"A-A"},dimensions,fixedAnnotations=annotation.GetProperty("fixedAnnotations"),geometricTolerances=annotation.GetProperty("geometricTolerances"),issues=Array.Empty<object>()};
        return (JsonSerializer.SerializeToElement(normalized),values);
    }
    public static List<WorkflowIssue> Check(JsonElement plan,List<Dictionary<string,string>> rows)
    {
        var result=WorkflowReports.Inspect(plan).ToList();
        foreach(var row in rows)try{
            var bound=Bind(plan,row);result.AddRange(WorkflowReports.CheckMeasurements(bound.Plan,new(){bound.Row}));
            var measured=plan.GetProperty("annotations").GetProperty("dimensions").EnumerateArray().Select(d=>d.GetProperty("column").GetString()).ToHashSet();
            foreach(var (col,cell) in ExcelModelInput.Build(new[]{row}).rows[0].cells)
                if(cell.state=="number"&&!measured.Contains(col))result.Add(new("UNMAPPED_MEASUREMENT","model","error",$"{row["jpeg file name"]}: {col} ölçü eşleşmesi eksik.",[col],"Model planında ölçü bağlantısı tamamlanmalı."));
        }catch(Exception ex){result.Add(new("V3_VALIDATION","model","error",row["jpeg file name"]+": "+ex.Message,[],"İlişki veya destek kapsamı incelenmeli; doğru veri değiştirilmez."));}
        return result;
    }
    public static object Resolve(JsonElement plan,Dictionary<string,string> row,string image){var bound=Bind(plan,row);return CadGroupExecutor.Resolve(bound.Plan,bound.Row,image);}
}
