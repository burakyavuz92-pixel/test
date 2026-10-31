public static class CadRecipePrompt
{
    public static string Instructions =>
        File.ReadAllText("contracts/cad-v9-draft/local-prompt.txt")+"\n\n"+
        File.ReadAllText("contracts/cad-v9-draft/local-contract.txt");
    public static string PresentationMode(IEnumerable<Dictionary<string,string>> rows)
    {
        var local=rows.Select(r=>LocalDrawingSettings.Read(r) is not null).Distinct().ToArray();
        if(local.Length>1)throw new FormatException("Aynı grupta yerel ayarlı ve eski düzende satırlar karıştırılamaz.");
        return local.FirstOrDefault()?"local-round-v1":"model-views-legacy";
    }
    public static string ForRows(IEnumerable<Dictionary<string,string>> rows)
    {
        if(PresentationMode(rows)!="local-round-v1")
            throw new FormatException("Yeni analiz için izometrik aci, kesit dogrultu, kesit kacikligi ve kacik kesitin genisligi sütunları gerekli. Kesit/kamera kararı modele gönderilmez.");
        return Instructions;
    }
}
