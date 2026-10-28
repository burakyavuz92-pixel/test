using System.Diagnostics;
public static class ImageAssets
{
    public static async Task PrepareGeometryView(string source,string output)
    {
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python"){UseShellExecute=false,RedirectStandardError=true};
        start.ArgumentList.Add("tools/color_views.py");start.ArgumentList.Add(Path.GetFullPath(source));start.ArgumentList.Add(Path.GetFullPath(output));
        start.Environment.Remove("OPENROUTER_API_KEY");start.Environment.Remove("OPENROUTER_MODEL");
        using var process=Process.Start(start)??throw new Exception("Renk ön işleme süreci başlatılamadı.");var error=process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();if(process.ExitCode!=0)throw new Exception("Renk ön işleme başarısız: "+await error);
    }
    public static async Task CropReference(string source,string output)
    {
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python"){UseShellExecute=false,RedirectStandardError=true};
        start.ArgumentList.Add("tools/image_assets.py");start.ArgumentList.Add(source);start.ArgumentList.Add(output);
        start.Environment.Remove("OPENROUTER_API_KEY");
        using var process=Process.Start(start)!;var err=process.StandardError.ReadToEndAsync();await process.WaitForExitAsync();if(process.ExitCode!=0)throw new Exception(await err);
    }
}
