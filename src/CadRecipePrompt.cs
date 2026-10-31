public static class CadRecipePrompt
{
    public static string Instructions => File.ReadAllText("contracts/cad-v9-draft/prompt.txt") + "\n\n" + File.ReadAllText("contracts/cad-v9-draft/contract.txt");
    public static string ForRows(IEnumerable<Dictionary<string,string>> rows)
    {
        if(!rows.Any(row=>LocalDrawingSettings.Read(row) is not null))return Instructions;
        var contract=File.ReadAllText("contracts/cad-v9-draft/contract.txt");
        contract=contract.Replace(",\"views\":[],\"sections\":[]", "");
        int start=contract.IndexOf("views: {",StringComparison.Ordinal);
        int end=contract.IndexOf("geometricTolerances:",start,StringComparison.Ordinal);
        contract=contract.Remove(start,end-start);
        contract=contract.Replace("Choose model coordinates consistently across the description.",
            "The round part's top-face center is [0,0,0]; +X is page-right, +Y page-up, +Z outward from that face. The body extends towards -Z.");
        contract=contract.Replace("sourceColor=black|green. Software hides green dimensions.",
            "sourceColor=\"#000000\"|\"#008000\" records the annotation color in the JPEG.");
        contract=contract.Replace(",visible?,hideIf?", "");
        int defaults=contract.IndexOf("Defaults: when=true",StringComparison.Ordinal);
        int next=contract.IndexOf("A dimension's condition",defaults,StringComparison.Ordinal);
        contract=contract.Remove(defaults,next-defaults).Insert(defaults,"Defaults: when=true, quantity=1. ");
        return File.ReadAllText("contracts/cad-v9-draft/local-prompt.txt")+"\n\n"+contract;
    }
}
