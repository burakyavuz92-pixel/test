using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Nodes;

public static class CadRecipeV9
{
    public static bool IsV9(JsonElement r)=>r.TryGetProperty("schemaVersion",out var v)&&v.GetInt32()==9;
    public static JsonElement Resolve(JsonElement recipe,Dictionary<string,string> row)
    {
        var local=LocalDrawingSettings.Read(row);
        if(local is not null)
        {
            var input=JsonNode.Parse(recipe.GetRawText())!;
            input["drawing"]!["views"]=new JsonArray();input["drawing"]!["sections"]=new JsonArray();
            recipe=JsonSerializer.SerializeToElement(input);
        }
        var p=new ProcessStartInfo(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python"){RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false};
        p.ArgumentList.Add(Path.GetFullPath("tools/cad_v9_compiler.py"));p.Environment.Remove("OPENROUTER_API_KEY");p.Environment.Remove("OPENROUTER_MODEL");
        using var process=Process.Start(p)??throw new Exception("v9 derleyici başlamadı.");
        var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();
        process.StandardInput.Write(JsonSerializer.Serialize(new{recipe,cells=ExcelModelInput.Build(new[]{row}).rows[0].cells,outputId=row["jpeg file name"]}));process.StandardInput.Close();
        if(!process.WaitForExit(30000)){process.Kill(true);throw new Exception("v9 çözümleme zaman aşımı.");}
        if(process.ExitCode!=0)throw new Exception(stderr.GetAwaiter().GetResult());
        var root=JsonNode.Parse(stdout.GetAwaiter().GetResult())!;var g=root["geometry"]!;var d=root["drawing"]!;
        if(local is not null)
        {
            local.Apply(root);
            return JsonSerializer.SerializeToElement(root);
        }
        var flat=new JsonObject{["operations"]=g["operations"]!.DeepClone(),["frames"]=g["frames"]!.DeepClone(),["views"]=d["views"]!.DeepClone(),["parameters"]=g["parameters"]!.DeepClone(),["featureApplied"]=g["featureApplied"]!.DeepClone()};
        foreach(var section in d["sections"]!.AsArray())
            if(section!["kind"]!.GetValue<string>()=="planar")section["plane"]=new JsonObject{["point"]=section["point"]!.DeepClone(),["normal"]=section["normal"]!.DeepClone()};
        var expanded=FeatureSectionTrace.Expand(d["sections"]!.AsArray(),flat);
        g["frames"]!.AsArray().Add(JsonNode.Parse("""{"id":"__sectionWorld","origin":[0,0,0],"xAxis":[1,0,0],"zAxis":[0,0,1]}"""));
        d["sections"]=SectionGeometry.Resolve(expanded,g["frames"]!.AsArray(),d["views"]!.AsArray());
        return JsonSerializer.SerializeToElement(root);
    }
    public static List<WorkflowIssue> Check(JsonElement recipe,List<Dictionary<string,string>> rows)
    {
        var issues=new List<WorkflowIssue>();foreach(var row in rows)try{Resolve(recipe,row);}catch(Exception ex){issues.Add(new("RECIPE_V9_RESOLUTION","software","error",row["jpeg file name"]+": "+ex.Message,[],""));}return issues;
    }
}
