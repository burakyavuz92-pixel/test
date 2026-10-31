using System.Text.Json;
using System.Security.Cryptography;

public static class RecipeLibrary
{
    const string Contract="cad-v7-feature-trace-1";
    static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    static string[] Columns(List<Dictionary<string,string>> rows)=>ExcelModelInput.Build(rows.Take(1)).rows[0].cells.Keys.OrderBy(x=>x,StringComparer.Ordinal).ToArray();
    static string Pattern(Dictionary<string,string> row)=>string.Join("|",ExcelModelInput.Build(new[]{row}).rows[0].cells.OrderBy(c=>c.Key,StringComparer.Ordinal).Select(c=>c.Key+":"+(c.Value.state=="blank"?"blank":c.Value.isZero==true?"zero":"value")));
    public static void SaveCandidate(string output,string image,List<Dictionary<string,string>> rows)
    {
        var record=new{Contract,PresentationMode=CadRecipePrompt.PresentationMode(rows),ImageSha256=Hash(image),RecipeSha256=Hash(Path.Combine(output,"recipe.json")),Columns=Columns(rows),Patterns=rows.Select(Pattern).Distinct().ToArray(),HumanApproved=false};
        File.WriteAllText(Path.Combine(output,"recipe-cache.json"),JsonSerializer.Serialize(record,WorkflowReports.Json));
    }
    static string LibraryRoot=>Environment.GetEnvironmentVariable("CAD_RECIPE_LIBRARY")??Path.Combine(Directory.GetCurrentDirectory(),".recipe-library");
    public static bool TryReuseApproved(string excel,string image,string output,bool execute=false)
    {
        string saved=Path.Combine(LibraryRoot,Hash(image));if(!File.Exists(Path.Combine(saved,"recipe-cache.json")))return false;
        using var manifest=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"recipe-cache.json")));
        var mode=manifest.RootElement.TryGetProperty("PresentationMode",out var value)?value.GetString():"model-views-legacy";
        if(mode!=CadRecipePrompt.PresentationMode(WorkflowReports.ReadRows(excel)))return false;
        Reuse(excel,image,saved,output,execute);return true;
    }
    public static void Approve(string saved)
    {
        string path=Path.Combine(saved,"recipe-cache.json");var record=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(path))!;
        if(record["RecipeSha256"]!.GetValue<string>()!=Hash(Path.Combine(saved,"recipe.json")))throw new Exception("Tarif özeti uyuşmuyor.");
        record["HumanApproved"]=true;File.WriteAllText(path,record.ToJsonString(WorkflowReports.Json));
        string target=Path.Combine(LibraryRoot,record["ImageSha256"]!.GetValue<string>());Directory.CreateDirectory(target);
        if(Path.GetFullPath(saved)!=Path.GetFullPath(target))
        {
            File.Copy(Path.Combine(saved,"recipe.json"),Path.Combine(target,"recipe.json"),true);
            File.Copy(path,Path.Combine(target,"recipe-cache.json"),true);
        }
    }
    public static void Reuse(string excel,string image,string saved,string output,bool execute=false)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        Directory.CreateDirectory(output);var issues=new List<WorkflowIssue>();string state="blocked-with-report";bool approved=false;
        try
        {
            using var manifest=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"recipe-cache.json")));var m=manifest.RootElement;
            if(m.GetProperty("Contract").GetString()!=Contract||m.GetProperty("ImageSha256").GetString()!=Hash(image)||m.GetProperty("RecipeSha256").GetString()!=Hash(Path.Combine(saved,"recipe.json")))throw new Exception("Kayıtlı tarif/sözleşme/JPEG eşleşmiyor; yeni grup analizi gerekli.");
            var rows=WorkflowReports.ReadRows(excel);
            var mode=m.TryGetProperty("PresentationMode",out var value)?value.GetString():"model-views-legacy";
            if(mode!=CadRecipePrompt.PresentationMode(rows))throw new Exception("Kayıtlı tarifin koordinat/sunum düzeni farklı; yeni grup analizi gerekli.");
            if(!Columns(rows).SequenceEqual(m.GetProperty("Columns").EnumerateArray().Select(x=>x.GetString()!)))throw new Exception("Excel sütunları kayıtlı grupla eşleşmiyor.");
            var patterns=m.GetProperty("Patterns").EnumerateArray().Select(x=>x.GetString()!).ToHashSet();
            if(rows.Any(r=>!patterns.Contains(Pattern(r))))throw new Exception("Yeni boş/sıfır/değer örüntüsü var; kayıtlı tarifin kapsamı dışında.");
            if(rows.Any(r=>!System.Text.RegularExpressions.Regex.IsMatch(r["jpeg file name"],@"^[A-Za-z0-9_-]+$")))throw new Exception("Geçersiz çıktı kimliği.");
            using var recipe=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"recipe.json")));
            issues.AddRange(CadRecipeV7.Check(recipe.RootElement,rows));
            if(issues.Any(i=>i.Severity=="error"))return;
            approved=m.GetProperty("HumanApproved").GetBoolean();
            foreach(var row in rows)File.WriteAllText(Path.Combine(output,row["jpeg file name"]+".resolved.json"),JsonSerializer.Serialize(CadRecipeV7.Resolve(recipe.RootElement,row),WorkflowReports.Json));
            File.Copy(Path.Combine(saved,"recipe.json"),Path.Combine(output,"recipe.json"));
            state=approved?"approved-recipe-analysis-only":"candidate-recipe-analysis-only";
            if(execute){issues.Add(new("GENERAL_EXECUTOR_PENDING","software","error","Kayıtlı tarif çözüldü; genel native yürütücü henüz uygulanmadı.",[],""));state="blocked-with-report";}
        }
        catch(Exception ex){issues.Add(new("RECIPE_REUSE_REJECTED","input","error",ex.Message,[],"Girdi/kayıtlı tarif incelenmeli; otomatik API çağrısı yapılmaz."));}
        finally{WorkflowReports.Save(output,state,issues,new{Source=new{ExcelSha256=Hash(excel),ImageSha256=Hash(image)},SavedRecipe=Path.GetFullPath(saved),ApiCalls=0,ReportedCostUsd=0,RecipeHumanApproved=approved,ProducedImages=0,NativeExecutionImplemented=false});Environment.ExitCode=WorkflowReports.ExitCode(state);Console.WriteLine(state+"; "+Path.Combine(output,"RAPOR.md"));}
    }
}
