using System.Diagnostics;
using System.Text.Json;

public static class NativeRecipeExecutor
{
    public static async Task RenderSaved(string excel,string image,string saved,string output)
    {
        CadRecipeWorkflow.Review(excel,image,saved,output);
        if(Environment.ExitCode!=0)return;
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
        foreach(var arg in new[]{Path.GetFullPath("tools/cad_recipe_executor.py"),Path.GetFullPath(output),Path.GetFullPath(image)})start.ArgumentList.Add(arg);
        start.Environment.Remove("OPENROUTER_API_KEY");start.Environment.Remove("OPENROUTER_MODEL");start.Environment["LIBGL_ALWAYS_SOFTWARE"]="1";
        using var process=Process.Start(start)??throw new Exception("Native yürütücü başlatılamadı.");
        var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();
        using var timeout=new CancellationTokenSource(TimeSpan.FromMinutes(10));
        try{await process.WaitForExitAsync(timeout.Token);}catch(OperationCanceledException){process.Kill(true);throw new Exception("Native yürütücü zaman aşımı.");}
        File.WriteAllText(Path.Combine(output,"native-stdout.log"),await stdout);File.WriteAllText(Path.Combine(output,"native-stderr.log"),await stderr);
        using var results=JsonDocument.Parse(File.ReadAllText(Path.Combine(output,"native-results.json")));
        int count=results.RootElement.GetProperty("results").EnumerateArray().Count(r=>r.GetProperty("status").GetString()=="preview-produced");
        File.WriteAllText(Path.Combine(output,"render-report.json"),JsonSerializer.Serialize(new{Status=process.ExitCode==0?"review-previews-produced":"partial-native-failure",ApiCalls=0,ProducedImages=count,HumanApproved=false,Limits=new[]{"Önizleme paftası; taslak anteti ve ölçü oku yerleşimi henüz uygulanmadı.","Ölçü/toleranslar tabloda; üretim onayı değildir."}},WorkflowReports.Json));
        Console.WriteLine($"{count} JPEG önizleme; API çağrısı 0; {output}");Environment.ExitCode=process.ExitCode;
    }
}
