using System.Text.Json;
using ClosedXML.Excel;

public record WorkflowIssue(string Code,string Category,string Severity,string Message,string[] AffectedFields,string RecommendedAction,string Origin="validator");
public static class WorkflowReports
{
    public static int ExitCode(string status)=>status.StartsWith("blocked")?2:status.StartsWith("failed")?1:0;
    public static readonly JsonSerializerOptions Json=new(){WriteIndented=true,PropertyNameCaseInsensitive=true};
    public static List<Dictionary<string,string>> ReadRows(string path)
    {
        using var wb=new XLWorkbook(path);var ws=wb.Worksheets.First();
        var headers=ws.Row(1).CellsUsed().Select(c=>(Name:c.GetString().Trim().Trim('\'', '’','‘'),Column:c.Address.ColumnNumber)).ToList();
        if(headers.Count==0||headers[0].Column!=1)throw new Exception("İlk sütun çıktı kimliği olmalı.");
        var first=headers[0];
        if(!first.Name.Equals("output jpeg name",StringComparison.OrdinalIgnoreCase)&&!first.Name.Equals("jpeg file name",StringComparison.OrdinalIgnoreCase))throw new Exception("A sütunu başlığı output jpeg name olmalı (eski jpeg file name de kabul edilir).");
        headers[0]=("jpeg file name",1);
        if(headers.Any(h=>LocalDrawingSettings.IsSetting(h.Name)))
        {
            var fixedNames=new[]{"jpeg file name","izometrik aci","kesit dogrultu","kesit kacikligi","kacik kesitin genisligi"};
            if(headers.Count<6||!headers.Take(5).Select(h=>h.Column).SequenceEqual(new[]{1,2,3,4,5}))
                throw new FormatException("A–E yerel ayarlar, F ve sonrası ölçü sütunları olmalı.");
            for(int i=1;i<5;i++)
            {
                if(!LocalDrawingSettings.IsSetting(headers[i].Name)||headers[i].Name!=fixedNames[i])
                    throw new FormatException($"{(char)('A'+i)} sütunu başlığı {fixedNames[i]} olmalı.");
            }
            if(headers.Skip(5).Any(h=>LocalDrawingSettings.IsSetting(h.Name)||h.Name.Equals("H",StringComparison.OrdinalIgnoreCase)))
                throw new FormatException("F ve sonrasında yalnız ölçü etiketleri olmalı; H ürün kimliği için A sütunundan alınır.");
            if(headers.Select(h=>h.Column).Last()!=headers.Count)throw new FormatException("Ölçü sütunlarında başlıksız ara sütun var.");
        }
        if(headers.Any(h=>h.Name.Length==0)||headers.Select(h=>h.Name).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=headers.Count)throw new Exception("Boş/tekrarlı başlık.");
        if(!headers.Any(h=>h.Name=="jpeg file name"))throw new Exception("jpeg file name sütunu yok.");
        var rows=ws.RowsUsed().Skip(1).Where(r=>headers.Any(h=>!r.Cell(h.Column).IsEmpty())).Select(r=>headers.ToDictionary(h=>h.Name,h=>r.Cell(h.Column).GetFormattedString().Trim())).ToList();
        if(rows.Count==0||rows.Select(r=>r["jpeg file name"]).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=rows.Count)throw new Exception("Veri yok veya tekrarlı çıktı adı.");
        return rows;
    }
    public static void Save(string folder,string status,IEnumerable<WorkflowIssue> issues,object run)
    {
        Directory.CreateDirectory(folder);var list=issues.ToArray();
        File.WriteAllText(Path.Combine(folder,"run-report.json"),JsonSerializer.Serialize(new{Status=status,Issues=list,Run=run,HumanApproved=false},Json));
        string text="# Çalışma raporu\n\nDurum: "+status+"\n\n"+string.Join("\n\n",list.Select(i=>$"- **{i.Code} / {i.Category} / {i.Severity} / {i.Origin}**: {i.Message}\n  Aksiyon: {i.RecommendedAction}"));
        text+="\n\nOrigin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.\n";
        File.WriteAllText(Path.Combine(folder,"RAPOR.md"),text);
    }
}
