using System.Diagnostics;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

public static class CadQueryPipeline
{
    static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    public static async Task Run(string excel,string image,string output,string? replay=null)
    {
        if(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())throw new Exception("Çıktı klasörü boş olmalı.");
        Directory.CreateDirectory(output);
        var issues=new List<WorkflowIssue>();string state="failed",stage="input";int calls=0;double cost=0;string? globalError=null;string errorOrigin="software";
        var settings=OpenRouterSettings.Load();var usages=new List<JsonElement>();var apiTimings=new List<object>();var totalTimer=Stopwatch.StartNew();
        try
        {
            var raw=WorkflowReports.ReadRows(excel);var parsed=ExcelModelInput.Build(raw);
            foreach(var r in raw)if(LocalDrawingSettings.Read(r) is null)throw new Exception("Yerel çizim ayarları gerekli.");
            foreach(var r in parsed.rows)if(!System.Text.RegularExpressions.Regex.IsMatch(r.outputId,@"^[A-Za-z0-9_-]+$"))throw new Exception("Geçersiz çıktı kimliği.");
            File.WriteAllText(Path.Combine(output,"rows.json"),JsonSerializer.Serialize(parsed.rows.Select(r=>new{r.outputId,parameters=ExcelModelInput.Parameters(r)}),WorkflowReports.Json));
            File.WriteAllText(Path.Combine(output,"normalized-excel.json"),JsonSerializer.Serialize(parsed,WorkflowReports.Json));
            File.WriteAllText(Path.Combine(output,"pipeline-source.json"),JsonSerializer.Serialize(new{excelSha256=Hash(excel),imageSha256=Hash(image)},WorkflowReports.Json));
            var selection=ModelRowSampling.Select(parsed.rows);
            string table=JsonSerializer.Serialize(ExcelModelInput.ForModel(selection.Rows));
            File.WriteAllText(Path.Combine(output,"sampling-report.json"),JsonSerializer.Serialize(new{selection.Policy,selection.TotalRows,selection.UniqueRows,SelectedRows=selection.Rows.Length,selection.Coverage,FullTableBytes=Encoding.UTF8.GetByteCount(JsonSerializer.Serialize(ExcelModelInput.ForModel(parsed.rows))),SelectedTableBytes=Encoding.UTF8.GetByteCount(table)},WorkflowReports.Json));
            File.WriteAllText(Path.Combine(output,"model-input.json"),table);
            async Task<JsonElement> Request(string name,string prompt)
            {
                errorOrigin="api";
                File.WriteAllText(Path.Combine(output,name+"-prompt.txt"),prompt);
                using var client=new HttpClient{Timeout=TimeSpan.FromSeconds(settings.TimeoutSeconds)};
                client.DefaultRequestHeaders.Authorization=new AuthenticationHeaderValue("Bearer",Environment.GetEnvironmentVariable("OPENROUTER_API_KEY")??throw new Exception("API anahtarı yok."));
                var body=new{model=settings.Model,max_tokens=settings.MaxCompletionTokens,reasoning=new{effort=settings.ReasoningEffort},response_format=new{type="json_object"},messages=new[]{new{role="user",content=new object[]{new{type="text",text=prompt},new{type="image_url",image_url=new{url="data:image/jpeg;base64,"+Convert.ToBase64String(File.ReadAllBytes(image))}}}}}};
                var requestTimer=Stopwatch.StartNew();calls++;using var response=await client.PostAsync("https://openrouter.ai/api/v1/chat/completions",new StringContent(JsonSerializer.Serialize(body),Encoding.UTF8,"application/json"));string text=await response.Content.ReadAsStringAsync();
                apiTimings.Add(new{Name=name,Seconds=requestTimer.Elapsed.TotalSeconds});
                File.WriteAllText(Path.Combine(output,name+"-api-response.json"),text);response.EnsureSuccessStatusCode();using var doc=JsonDocument.Parse(text);
                if(doc.RootElement.TryGetProperty("usage",out var usage)){usages.Add(usage.Clone());if(usage.TryGetProperty("cost",out var amount))cost+=amount.GetDouble();}
                var choice=doc.RootElement.GetProperty("choices")[0];if(choice.GetProperty("finish_reason").GetString()!="stop")throw new Exception("Model yanıtı tamamlanmadı.");
                using var answer=JsonDocument.Parse(GroupWorkflow.ExtractJson(choice.GetProperty("message").GetProperty("content").GetString()!));
                if(answer.RootElement.TryGetProperty("error",out var error)){errorOrigin="model";throw new Exception(error.GetString());}errorOrigin="software";return answer.RootElement.Clone();
            }
            void SaveCode(string filename,string source){if(source.Length>120000)throw new Exception("Betik boyut sınırı.");File.WriteAllText(Path.Combine(output,filename),source);}
            stage="geometry-model";
            if(replay is null){var r=await Request("geometry",File.ReadAllText("contracts/cadquery/geometry.txt")+"\nTABLE:\n"+table);SaveCode("part.py",r.GetProperty("script").GetString()!);SaveCode("face-tags.py",r.GetProperty("face_tags_script").GetString()!);}
            else {File.Copy(Path.Combine(replay,"part.py"),Path.Combine(output,"part.py"));if(File.Exists(Path.Combine(replay,"face-tags.py")))File.Copy(Path.Combine(replay,"face-tags.py"),Path.Combine(output,"face-tags.py"));}
            stage="geometry-execution";CadQueryProducts.CheckStage(output,"script-results.json",await CadScriptWorkflow.Execute(output));
            stage="face-tags";
            if(File.Exists(Path.Combine(output,"face-tags.py")))
            {
                var tagStart=new ProcessStartInfo(Environment.GetEnvironmentVariable("CADQUERY_PYTHON")??"/workspace/cq-venv/bin/python"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
                tagStart.ArgumentList.Add(Path.GetFullPath("tools/tag_script_steps.py"));tagStart.ArgumentList.Add(Path.GetFullPath(output));tagStart.Environment.Remove("OPENROUTER_API_KEY");tagStart.Environment.Remove("OPENROUTER_MODEL");
                using var tagProcess=Process.Start(tagStart)??throw new Exception("Yüz etiketi işlemi başlamadı.");var tagOut=tagProcess.StandardOutput.ReadToEndAsync();var tagErr=tagProcess.StandardError.ReadToEndAsync();using var tagTimeout=new CancellationTokenSource(TimeSpan.FromMinutes(3));
                try{await tagProcess.WaitForExitAsync(tagTimeout.Token);}catch(OperationCanceledException){tagProcess.Kill(true);throw new Exception("Yüz etiketi zaman aşımı.");}
                File.WriteAllText(Path.Combine(output,"face-tag-stdout.log"),await tagOut);File.WriteAllText(Path.Combine(output,"face-tag-stderr.log"),await tagErr);CadQueryProducts.CheckStage(output,"face-tag-results.json",tagProcess.ExitCode);
            }
            stage="measurement-model";
            if(replay is null){var r=await Request("measurements",File.ReadAllText("contracts/cadquery/measurements.txt")+"\nGEOMETRY:\n"+File.ReadAllText(Path.Combine(output,"part.py"))+"\nTABLE:\n"+table);SaveCode("measurements.py",r.GetProperty("script").GetString()!);File.WriteAllText(Path.Combine(output,"visual-markers.json"),r.GetProperty("markers").GetRawText());}
            else {File.Copy(Path.Combine(replay,"measurements.py"),Path.Combine(output,"measurements.py"));File.Copy(Path.Combine(replay,"visual-markers.json"),Path.Combine(output,"visual-markers.json"));}
            stage="measurement-execution";
            var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("CADQUERY_PYTHON")??"/workspace/cq-venv/bin/python"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
            start.ArgumentList.Add(Path.GetFullPath("tools/evaluate_script_measurements.py"));start.ArgumentList.Add(Path.GetFullPath(output));start.Environment.Remove("OPENROUTER_API_KEY");start.Environment.Remove("OPENROUTER_MODEL");
            using(var process=Process.Start(start)??throw new Exception("Ölçü yürütücüsü başlamadı."))
            {
                var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(2));
                try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new Exception("Ölçü zaman aşımı.");}
                File.WriteAllText(Path.Combine(output,"measurement-stdout.log"),await stdout);File.WriteAllText(Path.Combine(output,"measurement-stderr.log"),await stderr);
                if(process.ExitCode!=0)throw new Exception("Ortak ölçü fonksiyonu çalıştırılamadı.");
                CadQueryProducts.RequireRemaining(output);
            }
            stage="sheets";await CadScriptWorkflow.RenderSheets(excel,image,output);CadQueryProducts.CheckStage(output,"script-sheet-results.json",Environment.ExitCode);
            using var sheets=JsonDocument.Parse(File.ReadAllText(Path.Combine(output,"script-sheet-results.json")));
            bool unconfirmed=sheets.RootElement.GetProperty("results").EnumerateArray().Where(r=>r.GetProperty("status").GetString()=="sheet-produced").Any(r=>r.GetProperty("drafting").TryGetProperty("unconfirmedVisualLabels",out var labels)&&labels.GetArrayLength()>0);
            bool incomplete=sheets.RootElement.GetProperty("results").EnumerateArray().Where(r=>r.GetProperty("status").GetString()=="sheet-produced").Any(r=>r.GetProperty("drafting").GetProperty("unresolvedDimensions").GetArrayLength()>0);
            state=unconfirmed?"sheets-produced-with-unconfirmed-labels":incomplete?"sheets-produced-with-unresolved-measurements":"sheets-produced";Environment.ExitCode=incomplete||unconfirmed?2:0;
        }
        catch(Exception ex){globalError=ex.Message;issues.Add(new("CADQUERY_PIPELINE",stage,"error",ex.Message,[],"Aşama kayıtları incelenmeli; otomatik API tekrarı yok."));Environment.ExitCode=1;}
        finally{bool partial=CadQueryProducts.Save(output,stage,globalError,errorOrigin);if(partial&&state.StartsWith("sheets-produced")){state="partially-produced";Environment.ExitCode=2;}WorkflowReports.Save(output,state,issues,new{Stage=stage,ApiCalls=calls,ReportedCostUsd=cost,Model=settings.Model,Reasoning=settings.ReasoningEffort,Replay=replay is not null,Usage=usages,ApiTimings=apiTimings,TotalSeconds=totalTimer.Elapsed.TotalSeconds});Console.WriteLine(state+"; "+output);}
    }
}
