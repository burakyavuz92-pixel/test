using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;
using ClosedXML.Excel;

public record ValidationResult(bool Passed, string Reference, List<string> Errors, List<string> Warnings);
public static class AnalysisValidation
{
    public static Dictionary<string,string> ReferenceValues(string xlsx, string reference)
    {
        using var book = new XLWorkbook(xlsx);
        var sheet = book.Worksheets.First();
        var headers = sheet.Row(1).CellsUsed().Select(c => (Name: c.GetString().Trim().Trim('\'', '’', '‘'), Col: c.Address.ColumnNumber)).ToList();
        if(headers.Any(h => h.Name.Length == 0) || headers.Select(h=>h.Name).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=headers.Count)
            throw new Exception("Boş veya tekrarlı Excel sütun adı.");
        var file = headers.Single(h => h.Name.Equals("jpeg file name", StringComparison.OrdinalIgnoreCase));
        var row = sheet.RowsUsed().Skip(1).Single(r=>r.Cell(file.Col).GetFormattedString().Trim()==reference);
        return headers.Where(h=>h.Col!=file.Col).ToDictionary(h=>h.Name,h=>row.Cell(h.Col).GetFormattedString().Trim(),StringComparer.OrdinalIgnoreCase);
    }
    static decimal Number(string s) => decimal.Parse(s.Replace(',','.'), CultureInfo.InvariantCulture);
    static (decimal Nominal, decimal? Upper, decimal? Lower)? Dimension(string value)
    {
        var m=Regex.Match(value,@"^\s*[Øø⌀]?\s*(?<n>\d+(?:[.,]\d+)?)\s*(?:±\s*(?<both>\d+(?:[.,]\d+)?)|\(\s*(?<up>\+\d+(?:[.,]\d+)?)\s*[|/]\s*(?<lo>-\d+(?:[.,]\d+)?)\s*\))?\s*$");
        if(!m.Success)return null;
        if(m.Groups["both"].Success){var t=Number(m.Groups["both"].Value);return (Number(m.Groups["n"].Value),t,-t);}
        return (Number(m.Groups["n"].Value),m.Groups["up"].Success?Number(m.Groups["up"].Value):null,m.Groups["lo"].Success?Number(m.Groups["lo"].Value):null);
    }
    static (decimal? Upper,decimal? Lower)? Tolerance(JsonElement mapping)
    {
        if(!mapping.TryGetProperty("toleranceText",out var t))return null;
        if(t.ValueKind==JsonValueKind.Null || t.ValueKind==JsonValueKind.String && string.IsNullOrWhiteSpace(t.GetString()))return (null,null);
        if(t.ValueKind!=JsonValueKind.String)return null;
        var raw=t.GetString()!.Trim();
        var d=Dimension("1 "+(raw.StartsWith('±') || raw.StartsWith('(')?raw:"("+raw+")"));
        return d is {} v?(v.Upper,v.Lower):null;
    }
    public static ValidationResult Check(string xlsx,string reference,JsonElement root)
    {
        var expected=ReferenceValues(xlsx,reference);var errors=new List<string>();var warnings=new List<string>();
        if(!root.TryGetProperty("reference",out var rf)||rf.ValueKind!=JsonValueKind.String||rf.GetString()!=reference)errors.Add("Referans ürün uyuşmuyor.");
        if(!root.TryGetProperty("mappings",out var mappings)||mappings.ValueKind!=JsonValueKind.Array)
            return new(false,reference,new(){"mappings dizisi bulunamadı."},warnings);
        var seen=new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach(var m in mappings.EnumerateArray())
        {
            if(m.ValueKind!=JsonValueKind.Object || !m.TryGetProperty("label",out var label)||label.ValueKind!=JsonValueKind.String){errors.Add("Geçersiz eşleştirme etiketi.");continue;}
            var name=label.GetString()!.Trim().Trim('\'', '’','‘');
            if(!seen.Add(name)){errors.Add("Tekrarlı etiket: "+name);continue;}
            if(!expected.TryGetValue(name,out var source)){errors.Add("Excel'de olmayan etiket: "+name);continue;}
            if(source.Length==0){errors.Add("Boş Excel değeri: "+name);continue;}
            foreach(var field in new[]{"meaning","evidence"})
                if(!m.TryGetProperty(field,out var v)||v.ValueKind!=JsonValueKind.String||string.IsNullOrWhiteSpace(v.GetString()))errors.Add(name+": eksik "+field);
            if(!m.TryGetProperty("confidence",out var confidence)||confidence.ValueKind!=JsonValueKind.String||confidence.GetString() is not ("high" or "medium" or "low"))errors.Add(name+": geçersiz confidence");
            else if(confidence.GetString()=="low")errors.Add(name+": düşük güven, inceleme gerekli.");
            else if(confidence.GetString()=="medium")warnings.Add(name+": orta güven, önizlemede kontrol edin.");
            var dimension=Dimension(source);
            if(dimension is {} dim)
            {
                if(!m.TryGetProperty("nominalMm",out var nom)||nom.ValueKind!=JsonValueKind.Number||!nom.TryGetDecimal(out var number)||number!=dim.Nominal)errors.Add(name+": nominal ölçü uyuşmuyor.");
                var tolerance=Tolerance(m);
                if(tolerance is not {} tol||tol.Upper!=dim.Upper||tol.Lower!=dim.Lower)errors.Add(name+": tolerans uyuşmuyor veya ayrıştırılamadı.");
            }
            else
            {
                if(!m.TryGetProperty("valueText",out var text)||text.ValueKind!=JsonValueKind.String||text.GetString()!=source)errors.Add(name+": metin değeri eksik veya uyuşmuyor.");
                if(!m.TryGetProperty("nominalMm",out var nom)||nom.ValueKind!=JsonValueKind.Null)errors.Add(name+": metin alanı geometri olarak kullanılamaz.");
            }
        }
        foreach(var name in expected.Keys.Where(k=>!seen.Contains(k)))errors.Add("Eksik etiket: "+name);
        if(root.TryGetProperty("questions",out var questions)&&questions.ValueKind==JsonValueKind.Array)
            foreach(var q in questions.EnumerateArray())if(q.TryGetProperty("blocking",out var b)&&b.ValueKind==JsonValueKind.True)errors.Add("Çözülmemiş engelleyici soru: "+q.GetProperty("question").GetString());
        warnings.Add("Bu kontrol geometrik yorumun doğruluğunu veya üç görünüşün tutarlılığını kanıtlamaz; insan önizleme onayı gereklidir.");
        return new(errors.Count==0,reference,errors,warnings);
    }
}
