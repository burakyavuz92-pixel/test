public static class DrawingFonts
{
    public static string ArialPath()
    {
        string path=Environment.GetEnvironmentVariable("DRAWING_FONT_PATH")??"/workspace/fonts/arial/arial.ttf";
        if(!File.Exists(path))throw new Exception("Arial dosyası bulunamadı; DRAWING_FONT_PATH ayarlayın.");
        return Path.GetFullPath(path); // The native worker verifies actual font family via fontTools.
    }
}
