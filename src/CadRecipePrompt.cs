public static class CadRecipePrompt
{
    // Historical workbooks keep their original interpretation path.
    public static string Instructions => Read("prompt.txt", "contract.txt");
    static string Read(string prompt,string contract) =>
        File.ReadAllText(Path.Combine("contracts/cad-v9-draft",prompt))+"\n\n"+
        File.ReadAllText(Path.Combine("contracts/cad-v9-draft",contract));
    public static string PresentationMode(IEnumerable<Dictionary<string,string>> rows)
    {
        var local=rows.Select(r=>LocalDrawingSettings.Read(r) is not null).Distinct().ToArray();
        if(local.Length>1)throw new FormatException("Aynı grupta yerel ayarlı ve eski düzende satırlar karıştırılamaz.");
        return local.FirstOrDefault()?"local-round-v1":"model-views-legacy";
    }
    public static string ForRows(IEnumerable<Dictionary<string,string>> rows) =>
        PresentationMode(rows)=="local-round-v1"?Read("local-prompt.txt","local-contract.txt"):Instructions;
}
