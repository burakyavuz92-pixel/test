using System.Diagnostics;
public static class ApiImageTransport
{
    public static string Prepare(string image,string output,string model)
    {
        // Observed GPT-6 Luna limit: 30,000 image patches. 6400x4525 uses 28,400 32px patches.
        string? setting=Environment.GetEnvironmentVariable("OPENROUTER_IMAGE_MAX_EDGE");
        int maxEdge=setting is null?(model=="openai/gpt-6-luna"?6400:0):int.Parse(setting);
        if(maxEdge==0)return image;
        string path=Path.Combine(output,"api-input.jpeg");
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
        foreach(string arg in new[]{Path.GetFullPath("tools/prepare_api_image.py"),Path.GetFullPath(image),Path.GetFullPath(path),maxEdge.ToString(System.Globalization.CultureInfo.InvariantCulture),model=="openai/gpt-6-luna"?"30000":"0"})start.ArgumentList.Add(arg);
        start.Environment.Remove("OPENROUTER_API_KEY");start.Environment.Remove("OPENROUTER_MODEL");
        using var p=Process.Start(start)??throw new Exception("API görsel hazırlığı başlamadı.");
        var stdout=p.StandardOutput.ReadToEndAsync();var stderr=p.StandardError.ReadToEndAsync();
        if(!p.WaitForExit(30000)){p.Kill(true);throw new Exception("API görsel hazırlığı zaman aşımı.");}
        if(p.ExitCode!=0)throw new Exception(stderr.GetAwaiter().GetResult());
        File.WriteAllText(Path.Combine(output,"image-transport.json"),stdout.GetAwaiter().GetResult());return path;
    }
}
