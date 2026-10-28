using System.Text.Json;
using System.Text.Json.Nodes;

public static class ColorVisibilityPolicy
{
    // Only local presentation is changed. Raw model response and geometry stay intact.
    public static JsonElement Apply(JsonElement plan)
    {
        var node=JsonNode.Parse(plan.GetRawText())!;
        var green=new HashSet<string>();
        if(plan.TryGetProperty("measurementSources",out var sources))
            foreach(var source in sources.EnumerateArray())
                if(source.GetProperty("color").GetString()=="green")green.Add(source.GetProperty("column").GetString()!);
        foreach(var dim in node["annotations"]!["dimensions"]!.AsArray())
            if(green.Contains(dim!["column"]!.GetValue<string>()))dim["visible"]=false;
        foreach(var dim in node["annotations"]!["fixedAnnotations"]!.AsArray())
            if(dim?["sourceColor"]?.GetValue<string>()=="green")dim["visible"]=false;
        return JsonSerializer.SerializeToElement(node);
    }
}
