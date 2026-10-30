using System.Globalization;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using ClosedXML.Excel;

public static class GroupWorkflow
{
    static readonly JsonSerializerOptions Json=new(){WriteIndented=true,PropertyNameCaseInsensitive=true};
    public static double Value(string text)
    {
        ParsedExcelCell parsed;
        try { parsed=ExcelModelInput.ParseCell(text); }
        catch(FormatException) { throw new Exception("Geçersiz ölçü: "+text); }
        if(parsed.state!="number")throw new Exception("Geçersiz ölçü: "+text);
        return parsed.nominalMm!.Value;
    }
    public static string ExtractJson(string content)
    {
        content=content.Trim();
        if(content.StartsWith('{'))return content;
        var blocks=Regex.Matches(content,@"```(?:json)?\s*(\{[\s\S]*?\})\s*```",RegexOptions.IgnoreCase);
        if(blocks.Count!=1)throw new Exception("Tek bir JSON nesnesi bekleniyor.");
        return blocks[0].Groups[1].Value;
    }
}
