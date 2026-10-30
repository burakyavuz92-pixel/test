using System.Text.Json;
using System.Text.Json.Nodes;

// Public semantic contract -> private dependency compiler. The model never writes target/tool/passThrough.
public static class CadRecipeV7
{
    static JsonNode Copy(JsonNode? node)=>node?.DeepClone()??throw new Exception("Sözleşme alanı eksik.");
    public static JsonElement Compile(JsonElement recipe)
    {
        var root=JsonNode.Parse(recipe.GetRawText())!;
        if(root["schemaVersion"]?.GetValue<int>()!=7)throw new Exception("CAD sözleşmesi v7 gerekli.");
        if(root["questions"] is not null)throw new Exception("Soru yerine kısa hata yanıtı gerekli.");
        var geometry=root["geometry"]!;var drawing=root["drawing"]!;
        var parameters=Copy(geometry["parameters"]).AsArray();
        var features=geometry["features"]!.AsArray();var ops=new JsonArray();
        foreach(var f in features)
        {
            string kind=f!["kind"]!.GetValue<string>();
            var uses=f["uses"]!.AsArray().Select(n=>n!.GetValue<string>()).ToArray();
            if(kind=="join")throw new Exception("join yalnız iç derleyici işlemidir; fuse kullanın.");
            if(kind=="fuse"&&uses.Length<2)throw new Exception("Birleşim ana gövde ve en az bir ek gövde ister.");
            bool modifier=kind is "hole" or "fillet" or "chamfer" or "cut";
            if(modifier&&uses.Length!=(kind=="cut"?2:1))throw new Exception("Özellik bağımlılığı: "+f["id"]);
            if(kind is "fillet" or "chamfer")
                foreach(var selector in f["args"]!["selectors"]!.AsArray())
                    if(selector!["near"]?.AsArray().Count!=3||selector["direction"]?.AsArray().Count!=3)
                        throw new Exception("Kenar seçimi geometrik near/direction gerektirir: "+f["id"]);
            ops.Add(new JsonObject{
                ["id"]=Copy(f["id"]),["op"]=kind=="fuse"?"join":kind,["frame"]=Copy(f["frame"]),
                ["target"]=modifier||kind=="fuse"?uses[0]:null,["tool"]=kind=="cut"?uses[1]:null,
                ["inputs"]=JsonSerializer.SerializeToNode(modifier?Array.Empty<string>():kind=="fuse"?uses.Skip(1).ToArray():uses),
                ["optionalInputs"]=new JsonArray(),
                ["when"]=f["presence"]?.DeepClone()??new JsonObject{["kind"]="always"},
                ["args"]=Copy(f["args"])});
        }
        var dimensions=new JsonArray();
        foreach(var d in drawing["dimensions"]!.AsArray())
        {
            var copy=Copy(d);var source=d!["valueSource"]!;
            string kind=source["kind"]!.GetValue<string>();string param;
            if(kind=="column")
            {
                string column=source["column"]!.GetValue<string>();
                var p=parameters.FirstOrDefault(p=>p!["source"]?["kind"]?.GetValue<string>()=="column"&&p["source"]?["column"]?.GetValue<string>()==column);
                if(p is null)throw new Exception("Ölçü kaynak sütunu geometriye bağlanmadı: "+column);
                param=p["id"]!.GetValue<string>();
            }
            else if(kind=="parameter")param=source["parameter"]!.GetValue<string>();
            else throw new Exception("Bilinmeyen ölçü kaynağı.");
            copy["sourceColor"]??=JsonValue.Create("black");
            copy["quantity"]??=JsonValue.Create(1);
            copy["visible"]??=JsonValue.Create(true);
            copy["hideIf"]??=new JsonObject{["kind"]="never"};
            copy["parameter"]=param;copy.AsObject().Remove("valueSource");dimensions.Add(copy);
        }
        var sectionData=Copy(drawing["sections"]).AsArray();
        foreach(var section in sectionData)
            if(section!["kind"]!.GetValue<string>()=="featureTrace")
            {
                var ids=section["through"]!.AsArray().Select(a=>a!["feature"]!.GetValue<string>()).Prepend(section["main"]!["feature"]!.GetValue<string>()).Distinct();
                section["targets"]=JsonSerializer.SerializeToNode(ids.ToArray());
            }
        var compiled=new JsonObject{["schemaVersion"]=6,["parameters"]=parameters,["frames"]=Copy(geometry["frames"]),["operations"]=ops,["result"]=Copy(geometry["result"]),["dimensions"]=dimensions,["views"]=Copy(drawing["views"]),["sections"]=sectionData,["geometricTolerances"]=Copy(drawing["geometricTolerances"]),["issues"]=root["issues"]?.DeepClone()??new JsonArray()};
        ValidatePresentation(compiled);
        return JsonSerializer.SerializeToElement(compiled);
    }
    static void ValidatePresentation(JsonObject plan)
    {
        var frames=plan["frames"]!.AsArray().Select(f=>f!["id"]!.GetValue<string>()).ToHashSet();
        var views=plan["views"]!.AsArray().Select(v=>v!["id"]!.GetValue<string>()).ToHashSet();
        foreach(var view in plan["views"]!.AsArray())
        {
            double[] V(string k)=>view![k]!.AsArray().Select(n=>n!.GetValue<double>()).ToArray();
            var a=V("direction");var b=V("up");
            if(a.Length!=3||b.Length!=3||a.Concat(b).Any(v=>!double.IsFinite(v))||a.Sum(x=>x*x)<1e-12||b.Sum(x=>x*x)<1e-12)throw new Exception("Geçersiz görünüş vektörü.");
            double cosine=a.Zip(b).Sum(t=>t.First*t.Second)/Math.Sqrt(a.Sum(x=>x*x)*b.Sum(x=>x*x));
            if(Math.Abs(cosine)>.999)throw new Exception("Görünüş ve yukarı vektörü paralel.");
        }
        foreach(var s in plan["sections"]!.AsArray())
        {
            if(!views.Contains(s!["view"]!.GetValue<string>()))throw new Exception("Kesit görünüşü bilinmiyor.");
            if(s["kind"]!.GetValue<string>()=="planar"||s["sourceView"] is null)
                if(!frames.Contains(s["frame"]!.GetValue<string>()))throw new Exception("Kesit bazı bilinmiyor.");
        }
    }

    public static JsonElement Resolve(JsonElement recipe,Dictionary<string,string> row)
    {
        var compiled=Compile(recipe);var resolved=CadRecipe.Resolve(compiled,row);
        var node=JsonNode.Parse(resolved.GetRawText())!;
        foreach(var feature in node["operations"]!.AsArray())
        {
            string kind=feature!["op"]!.GetValue<string>();
            if(kind is "fillet" or "chamfer")
                foreach(var selector in feature["args"]!["selectors"]!.AsArray())
                {
                    string target=selector!["operation"]!.GetValue<string>();
                    if(node["featureApplied"]?[target]?.GetValue<bool>()!=true)throw new Exception("Kenar seçiminin hedef özelliği mevcut değil.");
                }
            if(kind=="sketch")ValidateProfiles(feature["args"]!["loops"]!.AsArray());
        }
        var parameterMetadata=new JsonObject();
        foreach(var p in compiled.GetProperty("parameters").EnumerateArray())
            parameterMetadata[p.GetProperty("id").GetString()!]=new JsonObject{["unit"]=p.GetProperty("unit").GetString(),["source"]=JsonNode.Parse(p.GetProperty("source").GetRawText())};
        var sourceCells=ExcelModelInput.Build(new[]{row}).rows[0].cells;
        var compiledParameters=compiled.GetProperty("parameters").EnumerateArray().ToDictionary(p=>p.GetProperty("id").GetString()!);
        foreach(var d in node["dimensions"]!.AsArray())
        {
            var parameter=compiledParameters[d!["parameter"]!.GetValue<string>()];
            d["unit"]=parameter.GetProperty("unit").GetString();
            var source=parameter.GetProperty("source");
            if(source.GetProperty("kind").GetString()=="column")
            {
                string column=source.GetProperty("column").GetString()!;
                d["valueSource"]=new JsonObject{["kind"]="column",["column"]=column};
                d["sourceMeasurement"]=JsonSerializer.SerializeToNode(sourceCells[column]);
            }
            else d["valueSource"]=new JsonObject{["kind"]="parameter",["parameter"]=d["parameter"]!.DeepClone()};
        }
        // Bind section coordinates, which remain symbolic in the public group recipe.
        JsonNode? Bind(JsonNode? n)
        {
            if(n is JsonObject o&&o.Count==1&&o["param"] is JsonValue id)
                return node["parameters"]![id.GetValue<string>()]?.DeepClone()??throw new Exception("Kesit boş/bilinmeyen parametre kullanıyor.");
            if(n is JsonObject obj){var copy=new JsonObject();foreach(var kv in obj)copy[kv.Key]=Bind(kv.Value);return copy;}
            if(n is JsonArray arr){var copy=new JsonArray();foreach(var x in arr)copy.Add(Bind(x));return copy;}
            return n?.DeepClone();
        }
        var expandedSections=FeatureSectionTrace.Expand(Bind(node["sections"])!.AsArray(),node);
        var sectionFrames=node["frames"]!.DeepClone().AsArray();
        if(sectionFrames.Any(f=>f!["id"]!.GetValue<string>()=="__sectionWorld"))throw new Exception("Ayrılmış kesit bazı adı kullanılamaz.");
        sectionFrames.Add(JsonNode.Parse("""{"id":"__sectionWorld","origin":[0,0,0],"xAxis":[1,0,0],"zAxis":[0,0,1]}"""));
        var sections=SectionGeometry.Resolve(expandedSections,sectionFrames,node["views"]!.AsArray());
        var details=new JsonArray();var detailIds=new HashSet<string>();
        var knownViews=node["views"]!.AsArray().Select(v=>v!["id"]!.GetValue<string>()).ToHashSet();
        if(recipe.TryGetProperty("drawing",out var drawing)&&drawing.TryGetProperty("details",out var definitions))
        foreach(var definition in definitions.EnumerateArray())
        {
            if(!detailIds.Add(definition.GetProperty("id").GetString()!))throw new Exception("Tekrarlı detay kimliği.");
            if(!knownViews.Contains(definition.GetProperty("sourceView").GetString()!))throw new Exception("Detay kaynak görünüşü bilinmiyor.");
            var box=definition.GetProperty("sheetBox").EnumerateArray().Select(x=>x.GetDouble()).ToArray();
            if(box.Length!=4||box.Any(x=>!double.IsFinite(x))||box[0]<0||box[1]<0||box[2]<=0||box[3]<=0||box[0]+box[2]>1.000001||box[1]+box[3]>1.000001)throw new Exception("Detay yerleşim kutusu 0..1 sayfa sınırlarında olmalı.");
            var ids=definition.GetProperty("features").EnumerateArray().Select(x=>x.GetString()!).ToArray();
            if(ids.Length==0||ids.Any(id=>node["featureApplied"]![id] is null))throw new Exception("Detay geometri referansı bilinmiyor/boş.");
            ids=ids.Where(id=>node["featureApplied"]![id]!.GetValue<bool>()).ToArray();if(ids.Length==0)continue;
            var detail=JsonNode.Parse(definition.GetRawText())!;detail["features"]=JsonSerializer.SerializeToNode(ids);details.Add(detail);
        }
        return JsonSerializer.SerializeToElement(new JsonObject{
            ["schemaVersion"]=7,["outputId"]=node["outputId"]!.DeepClone(),
            ["geometry"]=new JsonObject{["parameters"]=node["parameters"]!.DeepClone(),["parameterMetadata"]=parameterMetadata,["frames"]=sectionFrames.DeepClone(),["operations"]=node["operations"]!.DeepClone(),["result"]=node["result"]!.DeepClone(),["featureApplied"]=node["featureApplied"]!.DeepClone()},
            ["drawing"]=new JsonObject{["dimensions"]=Bind(node["dimensions"]),["views"]=node["views"]!.DeepClone(),["sections"]=sections,["details"]=details,["geometricTolerances"]=node["geometricTolerances"]!.DeepClone()},
            ["executionStatus"]="recipe-resolved-not-rendered"});
    }
    static void ValidateProfiles(JsonArray loops)
    {
        double[] Point(JsonNode? p)
        {
            var xy=p!.AsArray().Select(n=>n!.GetValue<double>()).ToArray();
            if(xy.Length!=2||xy.Any(v=>!double.IsFinite(v)))throw new Exception("Profil noktası iki sonlu koordinat ister.");
            return xy;
        }
        bool Same(double[] a,double[] b)=>a.Zip(b).All(t=>Math.Abs(t.First-t.Second)<1e-7);
        foreach(var loop in loops)
        {
            string kind=loop!["kind"]!.GetValue<string>();
            if(kind is not ("circle" or "polyline" or "roundedSlot" or "path"))throw new Exception("Bilinmeyen profil türü.");
            if(kind!="path")continue;
            var segments=loop["segments"]!.AsArray();if(segments.Count<2||loop["closed"]?.GetValue<bool>()!=true)throw new Exception("Kapalı profil yolu gerekli.");
            double[]? first=null,previous=null;
            foreach(var segment in segments)
            {
                var a=Point(segment!["start"]);var b=Point(segment["end"]);
                if(Same(a,b)||previous is not null&&!Same(previous,a))throw new Exception("Profil yolu kopuk veya sıfır uzunlukta.");
                string type=segment["kind"]!.GetValue<string>();
                if(type=="arc")
                {
                    var mid=Point(segment["mid"]);
                    double cross=(mid[0]-a[0])*(b[1]-a[1])-(mid[1]-a[1])*(b[0]-a[0]);
                    if(Math.Abs(cross)<1e-10)throw new Exception("Üç noktalı yay doğrusal olamaz.");
                }
                else if(type!="line")throw new Exception("Bilinmeyen profil segmenti.");
                first??=a;previous=b;
            }
            if(!Same(first!,previous!))throw new Exception("Profil yolu kapanmıyor.");
        }
    }
    public static List<WorkflowIssue> Check(JsonElement recipe,List<Dictionary<string,string>> rows)
    {
        var issues=new List<WorkflowIssue>();
        if(recipe.TryGetProperty("error",out var error))
        {
            if(recipe.EnumerateObject().Count()!=1||error.ValueKind!=JsonValueKind.String||string.IsNullOrWhiteSpace(error.GetString()))
                return new(){new("MODEL_ERROR_PROTOCOL","model","error","Geçersiz kısa hata yanıtı.",[],"")};
            return new(){new("MODEL_RECIPE_ERROR","model","error",error.GetString()!,[],"",Origin:"model")};
        }
        try
        {
            var compiled=Compile(recipe);issues.AddRange(CadRecipe.Check(compiled,rows));
            if(issues.All(i=>i.Severity!="error"))foreach(var row in rows)try{Resolve(recipe,row);}catch(Exception ex){issues.Add(new("RECIPE_V7_RESOLUTION","model","error",row["jpeg file name"]+": "+ex.Message,[],"Tarif incelenmeli."));}
        }
        catch(Exception ex){issues.Add(new("RECIPE_V7_CONTRACT","model","error",ex.Message,[],"Sözleşme kaydı incelenmeli."));}
        return issues;
    }
}
