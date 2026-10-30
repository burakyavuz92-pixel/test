using System.Text.Json;
using System.Text;
using System.Net.Http.Headers;
using System.Security.Cryptography;

public static class CadRecipeWorkflow
{
    static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    public static void Review(string excel,string image,string saved,string output)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        using var old=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"run-report.json")));
        var binding=old.RootElement.GetProperty("Run").GetProperty("Source");
        if(binding.GetProperty("ExcelSha256").GetString()!=Hash(excel)||binding.GetProperty("ImageSha256").GetString()!=Hash(image))throw new Exception("Kaynak özeti uyuşmuyor.");
        using var pd=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"recipe.json")));var rows=WorkflowReports.ReadRows(excel);var issues=CadRecipe.Check(pd.RootElement,rows);Directory.CreateDirectory(output);
        string state=issues.Any(i=>i.Severity=="error")?"blocked-with-report":"recipe-analysis-only";
        if(state=="recipe-analysis-only")foreach(var row in rows)File.WriteAllText(Path.Combine(output,row["jpeg file name"]+".resolved.json"),JsonSerializer.Serialize(CadRecipe.Resolve(pd.RootElement,row),WorkflowReports.Json));
        WorkflowReports.Save(output,state,issues,new{Source=binding,SourceRun=Path.GetFullPath(saved),NewApiCalls=0,ProducedImages=0,NativeExecutionImplemented=false,AssistantAnswersUsed=false});Environment.ExitCode=WorkflowReports.ExitCode(state);
    }
    public static async Task Analyze(string excel,string image,string output,bool execute=false)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        Directory.CreateDirectory(output);var issues=new List<WorkflowIssue>();string state="failed-with-report";int calls=0,count=0;double? cost=null;
        var source=new{ExcelSha256=Hash(excel),ImageSha256=Hash(image)};
        try
        {
            var rows=WorkflowReports.ReadRows(excel);count=rows.Count;
            foreach(var row in rows)if(!System.Text.RegularExpressions.Regex.IsMatch(row["jpeg file name"],@"^[A-Za-z0-9_-]+$"))throw new Exception("Geçersiz çıktı kimliği.");
            var all=ExcelModelInput.Build(rows);File.WriteAllText(Path.Combine(output,"normalized-excel.json"),JsonSerializer.Serialize(all,WorkflowReports.Json));
            var sample=rows.Count<=8?rows:rows.GroupBy(r=>string.Join('|',r.Values.Select(v=>v.Length==0?"blank":v=="0"?"zero":"value"))).Select(g=>g.First()).Concat(rows.TakeLast(1)).Distinct().Take(8).ToList();
            var input=ExcelModelInput.Build(sample);string geometryImage=Path.Combine(output,"geometry-no-red.jpg");await ImageAssets.PrepareGeometryView(image,geometryImage);
            var geometry=new{lengthUnit="mm",rows=input.rows.Select(r=>new{r.outputId,cells=r.cells.ToDictionary(c=>c.Key,c=>new{c.Value.state,c.Value.nominalMm,c.Value.diameterSymbol,c.Value.isZero})})};
            var prompt=CadRecipePrompt.Instructions+"\ngeometryInput: "+JsonSerializer.Serialize(geometry)+"\nannotationInput: "+JsonSerializer.Serialize(input);
            File.WriteAllText(Path.Combine(output,"request-prompt.txt"),prompt);File.WriteAllText(Path.Combine(output,"model-input.json"),JsonSerializer.Serialize(input,WorkflowReports.Json));
            var model=Environment.GetEnvironmentVariable("OPENROUTER_MODEL")??throw new Exception("Model yok.");var key=Environment.GetEnvironmentVariable("OPENROUTER_API_KEY")??throw new Exception("API anahtarı yok.");
            using var client=new HttpClient{Timeout=TimeSpan.FromMinutes(3)};client.DefaultRequestHeaders.Authorization=new AuthenticationHeaderValue("Bearer",key);
            var body=new{model,max_tokens=20000,reasoning=new{effort="high"},response_format=new{type="json_object"},messages=new[]{new{role="user",content=new object[]{new{type="text",text=prompt},new{type="text",text="Image 1: geometry."},new{type="image_url",image_url=new{url="data:image/jpeg;base64,"+Convert.ToBase64String(File.ReadAllBytes(geometryImage))}},new{type="text",text="Image 2: original color reference."},new{type="image_url",image_url=new{url="data:image/jpeg;base64,"+Convert.ToBase64String(File.ReadAllBytes(image))}}}}}};
            calls++;using var response=await client.PostAsync("https://openrouter.ai/api/v1/chat/completions",new StringContent(JsonSerializer.Serialize(body),Encoding.UTF8,"application/json"));response.EnsureSuccessStatusCode();var raw=await response.Content.ReadAsStringAsync();File.WriteAllText(Path.Combine(output,"api-response.json"),raw);
            using var rd=JsonDocument.Parse(raw);if(rd.RootElement.TryGetProperty("usage",out var usage)&&usage.TryGetProperty("cost",out var value))cost=value.GetDouble();var choice=rd.RootElement.GetProperty("choices")[0];if(choice.GetProperty("finish_reason").GetString()!="stop")throw new Exception("Model yanıtı tamamlanmadı.");
            using var pd=JsonDocument.Parse(GroupWorkflow.ExtractJson(choice.GetProperty("message").GetProperty("content").GetString()!));var plan=pd.RootElement;
            File.WriteAllText(Path.Combine(output,"recipe.json"),JsonSerializer.Serialize(plan,WorkflowReports.Json));issues.AddRange(CadRecipe.Check(plan,rows));
            if(issues.Any(i=>i.Severity=="error")){state="blocked-with-report";return;}
            foreach(var row in rows)File.WriteAllText(Path.Combine(output,row["jpeg file name"]+".resolved.json"),JsonSerializer.Serialize(CadRecipe.Resolve(plan,row),WorkflowReports.Json));
            state="recipe-analysis-only";
            if(execute){issues.Add(new("GENERAL_EXECUTOR_PENDING","software","error","Genel CAD tarifi çözüldü; yeni native geometri/pafta yürütücüsü henüz uygulanmadı.",[],"İşlem yürütücüsü ve genel ölçülendirme desteği tamamlanmalı; eski pleyt motoruna zorlanmaz."));state="blocked-with-report";}
        }
        catch(Exception ex){issues.Add(new("RECIPE_RUN_FAILURE","software","error",ex.Message,[],"Kayıtlar incelenmeli; kullanıcı cevabı beklenmez."));}
        finally{WorkflowReports.Save(output,state,issues,new{Source=source,SchemaVersion=6,RowCount=count,ApiCalls=calls,ReportedCostUsd=cost,ReasoningEffort="high",ProducedImages=0,NativeExecutionImplemented=false,AssistantAnswersUsed=false});Environment.ExitCode=WorkflowReports.ExitCode(state);Console.WriteLine(state+"; "+Path.Combine(output,"RAPOR.md"));}
    }
}
