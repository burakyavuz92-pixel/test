public static class CadRecipePrompt
{
    public static string Instructions => File.ReadAllText("contracts/cad-v9-draft/prompt.txt") + "\n\n" + File.ReadAllText("contracts/cad-v9-draft/contract.txt");
}
