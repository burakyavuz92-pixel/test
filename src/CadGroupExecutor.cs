using System.Text.Json;

public static class CadGroupExecutor
{
    public static object Resolve(JsonElement plan, Dictionary<string,string> row, string image)
    {
        if(plan.GetProperty("kind").GetString()!="revolved-plate")throw new Exception("Desteklenmeyen geometri ailesi.");
        var section=plan.GetProperty("section");
        if(section.GetProperty("mode").GetString()!="through-features")throw new Exception("Kesit özellik bağlantısı eksik.");
        var p=plan.GetProperty("parameters");
        double Eval(string name)=>CadPlanWorkflow.Expression(p.GetProperty(name).GetString()!,row);
        var holes=plan.GetProperty("holes").EnumerateArray().Where(h=>{
            var presence=h.GetProperty("presentIfColumn");
            return presence.ValueKind==JsonValueKind.Null||!string.IsNullOrEmpty(row[presence.GetString()!]);
        }).Select(h=>new{id=h.GetProperty("id").GetString()!,diameterMm=CadPlanWorkflow.Expression(h.GetProperty("diameterExpression").GetString()!,row),xMm=CadPlanWorkflow.Expression(h.GetProperty("xExpression").GetString()!,row),yMm=CadPlanWorkflow.Expression(h.GetProperty("yExpression").GetString()!,row)}).ToArray();
        var allIds=plan.GetProperty("holes").EnumerateArray().Select(h=>h.GetProperty("id").GetString()!).ToHashSet();
        var targetIds=section.GetProperty("featureIds").EnumerateArray().Select(x=>x.GetString()!).ToArray();
        if(targetIds.Length==0||targetIds.Any(id=>!allIds.Contains(id)))throw new Exception("Kesit bilinmeyen/boş özellik içeriyor.");
        var activeIds=holes.Select(h=>h.id).ToHashSet();
        var dims=new List<object>();
        foreach(var dim in plan.GetProperty("dimensions").EnumerateArray())
        {
            string column=dim.GetProperty("column").GetString()!,feature=dim.GetProperty("feature").GetString()!;
            if(feature!="body"&&feature.Split(':').Any(id=>!activeIds.Contains(id)))continue;
            if(row[column].Length==0)throw new Exception("Mevcut özellik için ölçü hücresi boş: "+column);
            var hide=dim.GetProperty("hideWhen").GetString();double value=GroupWorkflow.Value(row[column]);
            bool hidden=hide switch {"never"=>false,"zero"=>Math.Abs(value)<1e-8,"half:B"=>Math.Abs(value-GroupWorkflow.Value(row["B"])/2)<1e-8,_=>throw new Exception("Bilinmeyen ölçü görünürlük kuralı.")};
            dims.Add(new{id=dim.GetProperty("id").GetString(),kind=dim.GetProperty("kind").GetString(),feature,valueText=row[column],visible=dim.GetProperty("visible").GetBoolean()&&!hidden});
        }
        var camera=plan.GetProperty("camera").Deserialize<ViewCamera>(new JsonSerializerOptions{PropertyNameCaseInsensitive=true})??throw new Exception("Kamera eksik.");
        OcctSheetService.ValidateCamera(camera,true);
        string outputId=row["jpeg file name"];
        if(!System.Text.RegularExpressions.Regex.IsMatch(outputId,@"^[A-Za-z0-9_-]+$"))throw new Exception("Geçersiz çıktı kimliği.");
        return new{product=outputId,outerDiameterMm=Eval("outerDiameterExpression"),depthMm=p.GetProperty("depthMm").GetDouble(),thicknessMm=p.GetProperty("thicknessMm").GetDouble(),outerRadiusMm=p.GetProperty("outerRadiusMm").GetDouble(),holes,camera=new{direction=camera.Direction,up=camera.Up,projection=camera.Projection},drawing=new{source=Path.GetFullPath(image),fontPath=DrawingFonts.ArialPath(),dimensions=dims,fixedAnnotations=plan.GetProperty("fixedAnnotations").Clone(),geometricTolerances=plan.GetProperty("geometricTolerances").Clone(),section=new{mode="through-features",featureIds=targetIds},textScale=1.10}};
    }
}
