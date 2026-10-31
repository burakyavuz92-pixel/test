using System.Text.Json;

// Project settings are authoritative; stale environment model names do not override them.
// The API key is read separately from the environment, never from this file.
public sealed record OpenRouterSettings(
    string Model="anthropic/claude-sonnet-5.5",
    string ReasoningEffort="high",
    int MaxCompletionTokens=65536,
    int TimeoutSeconds=600)
{
    public static OpenRouterSettings Load(string path="config/openrouter.json")
    {
        var settings=File.Exists(path)?JsonSerializer.Deserialize<OpenRouterSettings>(File.ReadAllText(path),WorkflowReports.Json)
            ??throw new FormatException("OpenRouter ayar dosyası boş."):new OpenRouterSettings();
        return settings.Validated();
    }
    public OpenRouterSettings Validated()
    {
        if(string.IsNullOrWhiteSpace(Model)||!Model.Contains('/')||Model!=Model.Trim())throw new FormatException("Geçersiz OpenRouter model kodu.");
        if(Model.EndsWith(":batch",StringComparison.OrdinalIgnoreCase))throw new FormatException("Batch kullanımı kaldırıldı; normal model kodu gerekli.");
        if(ReasoningEffort is not ("none" or "minimal" or "low" or "medium" or "high" or "xhigh" or "max"))throw new FormatException("Geçersiz reasoning ayarı.");
        if(MaxCompletionTokens<=0||TimeoutSeconds<=0)throw new FormatException("Token sınırı ve zaman aşımı pozitif olmalı.");
        return this;
    }
}
