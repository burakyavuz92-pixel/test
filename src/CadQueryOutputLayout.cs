using System.Text.Json;

public static class CadQueryOutputLayout
{
    public const string ReportsFolder = "raporlar";
    // Accept both historical flat run records and the new user-facing output folder.
    public static string Records(string folder) => File.Exists(Path.Combine(folder,"part.py"))
        ? folder : Directory.Exists(Path.Combine(folder,ReportsFolder)) ? Path.Combine(folder,ReportsFolder) : folder;

    public static void Publish(string records, string destination)
    {
        // Geometry previews use the same JPEG name: publish JPEG only after sheet production.
        var sheets=new HashSet<string>();
        var geometry=new HashSet<string>();
        var geometryReport=Path.Combine(records,"script-results.json");
        if(File.Exists(geometryReport)) {
            using var doc=JsonDocument.Parse(File.ReadAllText(geometryReport));
            foreach(var row in doc.RootElement.GetProperty("results").EnumerateArray())
                if(row.GetProperty("status").GetString()=="geometry-preview-produced")geometry.Add(row.GetProperty("outputId").GetString()!);
        }
        var report=Path.Combine(records,"script-sheet-results.json");
        if(File.Exists(report)) {
            using var doc=JsonDocument.Parse(File.ReadAllText(report));
            foreach(var row in doc.RootElement.GetProperty("results").EnumerateArray())
                if(row.GetProperty("status").GetString()=="sheet-produced")sheets.Add(row.GetProperty("outputId").GetString()!);
        }
        var rowsPath=Path.Combine(records,"rows.json");
        if(!File.Exists(rowsPath))return;
        using var rows=JsonDocument.Parse(File.ReadAllText(rowsPath));
        foreach(var row in rows.RootElement.EnumerateArray()) {
            string id=row.GetProperty("outputId").GetString()!;
            if(!System.Text.RegularExpressions.Regex.IsMatch(id,@"^[A-Za-z0-9_-]+$"))throw new Exception("Geçersiz çıktı kimliği.");
            foreach(var extension in new[]{".step",".jpeg"}) {
                if(extension==".jpeg"&&!sheets.Contains(id))continue;
                if(extension==".step"&&!geometry.Contains(id))continue;
                string source=Path.Combine(records,id,id+extension);
                if(File.Exists(source))File.Copy(source,Path.Combine(destination,id+extension),overwrite:false);
            }
        }
    }
}
