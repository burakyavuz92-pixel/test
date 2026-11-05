using System.Text.Json;
using System.Text.Json.Nodes;

public static class CadQueryProducts
{
    static JsonArray Failures(string folder)=>File.Exists(Path.Combine(folder,"product-failures.json"))
        ?JsonNode.Parse(File.ReadAllText(Path.Combine(folder,"product-failures.json")))!.AsArray():new JsonArray();
    public static void RequireRemaining(string folder)
    {
        var failed=Failures(folder).Select(r=>r!["outputId"]!.GetValue<string>()).ToHashSet();
        using var rows=JsonDocument.Parse(File.ReadAllText(Path.Combine(folder,"rows.json")));
        if(!rows.RootElement.EnumerateArray().Any(r=>!failed.Contains(r.GetProperty("outputId").GetString()!)))
            throw new Exception("Hiçbir ürün sonraki aşamaya geçemedi; product-results.json incelenmeli.");
    }
    public static void CheckStage(string folder,string report,int exit)
    {
        var path=Path.Combine(folder,report);
        if(!File.Exists(path))throw new Exception("Aşama sonuç kaydı oluşturulamadı: "+report);
        using var doc=JsonDocument.Parse(File.ReadAllText(path));
        if(doc.RootElement.TryGetProperty("scriptAccepted",out var accepted)&&!accepted.GetBoolean())
            throw new Exception("Ortak geometri kodu çalıştırılamadı: "+doc.RootElement.GetProperty("error").GetString());
        if(exit!=0&&!Failures(folder).Any())throw new Exception("Ortak aşama hatası: "+report);
        RequireRemaining(folder);
    }
    public static bool Save(string folder,string stage,string? globalError,string origin)
    {
        var rowsPath=Path.Combine(folder,"rows.json");if(!File.Exists(rowsPath))return false;
        var failures=Failures(folder).ToDictionary(r=>r!["outputId"]!.GetValue<string>(),r=>r!);
        var completed=new HashSet<string>();var sheetsPath=Path.Combine(folder,"script-sheet-results.json");
        if(File.Exists(sheetsPath))
        {
            using var sheets=JsonDocument.Parse(File.ReadAllText(sheetsPath));
            foreach(var row in sheets.RootElement.GetProperty("results").EnumerateArray())
                if(row.GetProperty("status").GetString()=="sheet-produced")completed.Add(row.GetProperty("outputId").GetString()!);
        }
        var results=new JsonArray();var messages=new List<string>();
        using var rows=JsonDocument.Parse(File.ReadAllText(rowsPath));
        foreach(var row in rows.RootElement.EnumerateArray())
        {
            string id=row.GetProperty("outputId").GetString()!;
            if(completed.Contains(id)&&!failures.ContainsKey(id)){results.Add(new JsonObject{["outputId"]=id,["status"]="completed"});continue;}
            var failure=failures.TryGetValue(id,out var f)?f.DeepClone():new JsonObject{["outputId"]=id,["stage"]=stage,["origin"]=origin,["reason"]=globalError??"Ürün tamamlanamadı."};
            failure["status"]="failed";results.Add(failure);
            messages.Add($"{id}: {failure["reason"]} [{failure["origin"]} / {failure["stage"]}]");
        }
        File.WriteAllText(Path.Combine(folder,"product-results.json"),results.ToJsonString(new JsonSerializerOptions{WriteIndented=true}));
        File.WriteAllLines(Path.Combine(folder,"failed-products.txt"),messages);
        foreach(var message in messages)Console.WriteLine(message);
        return messages.Count>0;
    }
}
