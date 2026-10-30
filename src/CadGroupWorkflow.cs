using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;

public static class CadGroupWorkflow
{
    static List<WorkflowIssue> Validate(JsonElement plan,List<Dictionary<string,string>> rows)=>plan.GetProperty("schemaVersion").GetInt32()>=3?CadPlanV3.Check(plan,rows):WorkflowReports.Inspect(plan).Concat(WorkflowReports.CheckMeasurements(plan,rows)).ToList();
    static object Resolve(JsonElement plan,Dictionary<string,string> row,string image)=>plan.GetProperty("schemaVersion").GetInt32()>=3?CadPlanV3.Resolve(plan,row,image):CadGroupExecutor.Resolve(plan,row,image);
    public static async Task RenderSaved(string xlsx,string image,string saved,string output)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        Directory.CreateDirectory(output);var issues=new List<WorkflowIssue>();string status="failed-with-report";int produced=0;bool assistantUsed=false;
        try
        {
            using var old=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"run-report.json")));
            var oldRun=old.RootElement.GetProperty("Run");
            assistantUsed=oldRun.TryGetProperty("AssistantAnswersUsed",out var used)&&used.GetBoolean();
            var binding=oldRun.GetProperty("Source");
            string Hash(string p)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(p)));
            if(binding.GetProperty("ExcelSha256").GetString()!=Hash(xlsx)||binding.GetProperty("ImageSha256").GetString()!=Hash(image))throw new Exception("Kaynak özeti uyuşmuyor.");
            using var doc=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"analysis-plan.json")));var plan=doc.RootElement;
            var rows=WorkflowReports.ReadRows(xlsx);issues.AddRange(Validate(plan,rows));
            if(issues.Any(i=>i.Severity=="error")){status="blocked-with-report";return;}
            var requests=rows.Select(r=>(Id:r["jpeg file name"],Request:Resolve(plan,r,image))).ToArray();
            IIsometricBackend backend=new OcctProcessBackend(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python","experiments/occt/worker.py");
            foreach(var r in requests)
            {
                string folder=Path.Combine(output,r.Id);Directory.CreateDirectory(folder);string input=Path.Combine(folder,"cad-request.json");File.WriteAllText(input,JsonSerializer.Serialize(r.Request,WorkflowReports.Json));
                await backend.Generate(input,Path.Combine(folder,"cad"));File.Copy(Path.Combine(folder,"cad","technical-sheet.jpeg"),Path.Combine(output,r.Id+".jpeg"));produced++;
            }
            status="produced-awaiting-review";
        }
        catch(Exception ex){issues.Add(new("RENDER_FAILURE","software","error",ex.Message,[],"Kayıtlı plan ve yerel çizim desteği incelenmeli."));}
        finally{WorkflowReports.Save(output,status,issues,new{SourceRun=Path.GetFullPath(saved),NewApiCalls=0,ProducedImages=produced,AssistantAnswersUsed=assistantUsed});Environment.ExitCode=WorkflowReports.ExitCode(status);}
    }
    public static void ReviewSaved(string xlsx,string image,string saved,string output)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        using var report=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"run-report.json")));
        string Hash(string p)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(p)));
        var binding=report.RootElement.GetProperty("Run").GetProperty("Source");
        if(binding.GetProperty("ExcelSha256").GetString()!=Hash(xlsx)||binding.GetProperty("ImageSha256").GetString()!=Hash(image))throw new Exception("Kaynak özeti uyuşmuyor.");
        using var doc=JsonDocument.Parse(File.ReadAllText(Path.Combine(saved,"analysis-plan.json")));var p=doc.RootElement;
        var rows=WorkflowReports.ReadRows(xlsx);var issues=Validate(p,rows);

        string status=issues.Any(i=>i.Severity=="error")?"blocked-with-report":"analysis-only";
        WorkflowReports.Save(output,status,issues,new{Source=binding,RowCount=rows.Count,NewApiCalls=0,ProducedImages=0,SourceRun=Path.GetFullPath(saved)});
        Environment.ExitCode=WorkflowReports.ExitCode(status);
    }
    public static async Task Run(string xlsx,string image,string output,bool analysisOnly=false,bool technicalJargon=false,string reasoningEffort="low")
    {
        if(reasoningEffort is not ("low" or "medium" or "high"))throw new Exception("Geçersiz akıl yürütme ayarı.");
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        Directory.CreateDirectory(output);var issues=new List<WorkflowIssue>();string status="failed";int calls=0,produced=0;double cost=0;int rowCount=0;int suppliedRows=0;bool apiCompleted=false;
        string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
        var source=new{ExcelSha256=Hash(xlsx),ImageSha256=Hash(image)};
        try
        {
            var rows=WorkflowReports.ReadRows(xlsx);rowCount=rows.Count;
            foreach(var row in rows)if(!System.Text.RegularExpressions.Regex.IsMatch(row["jpeg file name"],@"^[A-Za-z0-9_-]+$"))throw new Exception("Güvensiz dosya adı.");
            var samples=rows.Count<=8?rows.ToArray():rows.GroupBy(r=>string.Join("|",r.Select(v=>v.Value.Length==0?"blank":v.Value=="0"?"zero":"value"))).Select(g=>g.First()).Concat(rows.Take(1)).Concat(rows.TakeLast(1)).Distinct().Take(8).ToArray();
            // Validate every row locally, even if only a subset is sent to the model.
            var normalized=ExcelModelInput.Build(rows);
            File.WriteAllText(Path.Combine(output,"normalized-excel.json"),JsonSerializer.Serialize(normalized,WorkflowReports.Json));
            var modelInput=ExcelModelInput.Build(samples);suppliedRows=modelInput.rows.Length;
            string geometryImage=Path.Combine(output,"geometry-no-red.jpg");await ImageAssets.PrepareGeometryView(image,geometryImage);
            var geometryInput=new{lengthUnit="mm",rows=modelInput.rows.Select(r=>new{r.outputId,cells=r.cells.ToDictionary(k=>k.Key,k=>new{k.Value.state,k.Value.nominalMm,k.Value.isZero,k.Value.diameterSymbol})})};
            File.WriteAllText(Path.Combine(output,"geometry-input.json"),JsonSerializer.Serialize(geometryInput,WorkflowReports.Json));
            string prompt=(technicalJargon?CadAnalysisPrompt.TechnicalJargonDraft:CadAnalysisPrompt.Instructions)+"\ngeometryInput: "+JsonSerializer.Serialize(geometryInput)+"\nannotationInput: "+JsonSerializer.Serialize(modelInput);
            File.WriteAllText(Path.Combine(output,"model-input.json"),JsonSerializer.Serialize(modelInput,WorkflowReports.Json));
            File.WriteAllText(Path.Combine(output,"request-prompt.txt"),prompt);
            var key=Environment.GetEnvironmentVariable("OPENROUTER_API_KEY")??throw new Exception("API anahtarı yok.");var model=Environment.GetEnvironmentVariable("OPENROUTER_MODEL")??throw new Exception("Model yok.");
            using var client=new HttpClient{Timeout=TimeSpan.FromMinutes(3)};client.DefaultRequestHeaders.Authorization=new AuthenticationHeaderValue("Bearer",key);
            var messages=new List<object>{new{role="user",content=new object[]{new{type="text",text=prompt},new{type="text",text="IMAGE 1: GEOMETRY — black and green, red excluded."},new{type="image_url",image_url=new{url="data:image/jpeg;base64,"+Convert.ToBase64String(File.ReadAllBytes(geometryImage))}},new{type="text",text="IMAGE 2: ORIGINAL COLOR REFERENCE — annotation rules only."},new{type="image_url",image_url=new{url="data:image/jpeg;base64,"+Convert.ToBase64String(File.ReadAllBytes(image))}}}}};
            var body=new{model,max_tokens=6000,reasoning=new{effort=reasoningEffort},response_format=new{type="json_object"},messages};
            calls++;using var response=await client.PostAsync("https://openrouter.ai/api/v1/chat/completions",new StringContent(JsonSerializer.Serialize(body),Encoding.UTF8,"application/json"));response.EnsureSuccessStatusCode();apiCompleted=true;string raw=await response.Content.ReadAsStringAsync();File.WriteAllText(Path.Combine(output,"api-response.json"),raw);
            using var rd=JsonDocument.Parse(raw);if(rd.RootElement.TryGetProperty("usage",out var u)&&u.TryGetProperty("cost",out var c))cost=c.GetDouble();
            var choice=rd.RootElement.GetProperty("choices")[0];if(choice.GetProperty("finish_reason").GetString()!="stop")throw new Exception("API yanıtı eksik.");
            using var pd=JsonDocument.Parse(GroupWorkflow.ExtractJson(choice.GetProperty("message").GetProperty("content").GetString()!));var plan=pd.RootElement;
            File.WriteAllText(Path.Combine(output,"analysis-plan.json"),JsonSerializer.Serialize(plan,WorkflowReports.Json));
            issues.AddRange(CadPlanV3.Check(plan,rows));
            if(!plan.TryGetProperty("colorPolicyVersion",out var policy)||policy.GetInt32()!=1)
                issues.Add(new("COLOR_POLICY_MISSING","protocol","error","Model renk sözleşmesi sürümünü döndürmedi.",["colorPolicyVersion"],"Model yanıt şeması incelenmeli."));
            if(issues.Any(i=>i.Severity=="error")){status="blocked-with-report";return;}
            if(analysisOnly){status="analysis-only";return;}
            // Resolve every row before producing anything. No assistant-supplied relations.
            var requests=rows.Select(row=>(Id:row["jpeg file name"],Request:CadPlanV3.Resolve(plan,row,image))).ToArray();
            IIsometricBackend backend=new OcctProcessBackend(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python","experiments/occt/worker.py");
            foreach(var request in requests)
            {
                string folder=Path.Combine(output,request.Id);Directory.CreateDirectory(folder);
                string input=Path.Combine(folder,"cad-request.json");File.WriteAllText(input,JsonSerializer.Serialize(request.Request,WorkflowReports.Json));
                await backend.Generate(input,Path.Combine(folder,"cad"));
                File.Copy(Path.Combine(folder,"cad","technical-sheet.jpeg"),Path.Combine(output,request.Id+".jpeg"));produced++;
            }
            status="produced-awaiting-review";
        }
        catch(HttpRequestException ex) when(ex.StatusCode is System.Net.HttpStatusCode.Unauthorized or System.Net.HttpStatusCode.Forbidden)
        {
            issues.Add(new("API_AUTHENTICATION","configuration","error",$"OpenRouter kimlik doğrulama/erişim hatası: HTTP {(int)ex.StatusCode.Value}. Model analizi alınamadı; bu bir Excel veya JPEG anlama hatası değildir.",[],"Bulut ortamındaki OPENROUTER_API_KEY ve sağlayıcı erişim ayarlarını kontrol edip aynı girdilerle yeniden çalıştırın. Anahtarı sohbete veya rapora yazmayın."));
            status="failed-with-report";
        }
        catch(FormatException ex){issues.Add(new("EXCEL_PARSE","input","error",ex.Message,[],"Desteklenmeyen hücre gösterimini kontrol edin; nominal/tolerans tahmini yapılmaz."));status="blocked-with-report";}
        catch(Exception ex){issues.Add(new("RUN_FAILURE","software","error",ex.Message,[],"Rapor ve kayıtlı yanıt incelenmeli; yeni veri tahmin edilmez."));status="failed-with-report";}
        finally{Environment.ExitCode=WorkflowReports.ExitCode(status);WorkflowReports.Save(output,status,issues,new{Source=source,RowCount=rowCount,ModelSampleRowCount=suppliedRows,ExcelInputSchemaVersion=1,ApiCalls=calls,ApiResponseReceived=apiCompleted,ReportedCostUsd=cost,ProducedImages=produced,AnalysisOnly=analysisOnly,ReasoningEffort=reasoningEffort,PromptVariant=technicalJargon?"technical-jargon-draft":"production",ColorPolicyVersion=1,AssistantAnswersUsed=false});Console.WriteLine(status+"; rapor: "+Path.Combine(output,"RAPOR.md"));}
    }
}
