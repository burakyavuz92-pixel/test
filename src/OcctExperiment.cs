using System.Diagnostics;

public interface IIsometricBackend
{
    Task Generate(string requestPath,string outputDirectory);
}

// Local process boundary keeps the native CAD runtime optional and replaceable.
public sealed class OcctProcessBackend(string python,string worker) : IIsometricBackend
{
    public async Task Generate(string requestPath,string outputDirectory)
    {
        if(!File.Exists(python)||!File.Exists(worker))throw new Exception("OCCT Python/worker dosyası bulunamadı. OCCT_PYTHON yolunu ayarlayın.");
        if(!File.Exists(requestPath))throw new Exception("OCCT parametre dosyası bulunamadı.");
        var info=new ProcessStartInfo(python){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
        info.ArgumentList.Add(Path.GetFullPath(worker));info.ArgumentList.Add(Path.GetFullPath(requestPath));info.ArgumentList.Add(Path.GetFullPath(outputDirectory));
        if(OperatingSystem.IsLinux())info.Environment["LIBGL_ALWAYS_SOFTWARE"]="1";
        info.Environment.Remove("OPENROUTER_API_KEY");info.Environment.Remove("OPENROUTER_MODEL");
        using var process=Process.Start(info)??throw new Exception("OCCT yardımcı süreci başlatılamadı.");
        var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();
        using var limit=new CancellationTokenSource(TimeSpan.FromMinutes(2));
        try{await process.WaitForExitAsync(limit.Token);}catch(OperationCanceledException){process.Kill(true);throw new Exception("OCCT denemesi 120 saniyede tamamlanmadı.");}
        var output=await stdout;var error=await stderr;
        if(process.ExitCode!=0)throw new Exception("OCCT süreç çıkış kodu "+process.ExitCode+": "+error+"\n"+output);
        if(!File.Exists(Path.Combine(outputDirectory,"result.json")))throw new Exception("OCCT sonuç doğrulama dosyası yok.");
        Console.WriteLine(output.Trim());
        if(!string.IsNullOrWhiteSpace(error))Console.Error.WriteLine(error.Trim());
    }
}
