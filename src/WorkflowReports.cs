using System.Text.Json;
using ClosedXML.Excel;

public record WorkflowIssue(string Code,string Category,string Severity,string Message,string[] AffectedFields,string RecommendedAction,string Origin="validator");
public static class WorkflowReports
{
    public static int ExitCode(string status)=>status.StartsWith("blocked")?2:status.StartsWith("failed")?1:0;
    public static readonly JsonSerializerOptions Json=new(){WriteIndented=true,PropertyNameCaseInsensitive=true};
    public static WorkflowIssue[] Inspect(JsonElement plan)
    {
        var result=new List<WorkflowIssue>();
        if(plan.TryGetProperty("questions",out var questions)&&questions.GetArrayLength()>0)
            result.Add(new("QUESTION_RESPONSE","protocol","error","Model istenen rapor yerine soru döndürdü.",[],"Model yanıt şeması düzeltilmeli; kullanıcıya soru gönderilmez."));
        if(plan.TryGetProperty("issues",out var issues))foreach(var issue in issues.EnumerateArray())
            {
            var parsed=issue.Deserialize<WorkflowIssue>(Json)??throw new Exception("Geçersiz sorun kaydı.");
            if(parsed.Message.Contains('?')||parsed.RecommendedAction.Contains('?'))
                result.Add(new("MODEL_UNRESOLVED","protocol","error","Model belirsizliği rapor yerine soru biçiminde döndürdü.",parsed.AffectedFields,"İlgili alanlar açıkça tanımlanmalı; kullanıcıdan sohbet cevabı beklenmez."));
            else result.Add(parsed with{Origin="model"});
        }
        if(plan.TryGetProperty("section",out var section)&&section.TryGetProperty("plane",out var plane)&&plane.GetString()!="X=0")
            result.Add(new("UNSUPPORTED_SECTION","software","error","Taslak kademeli/ofset kesit gerektiriyor; yeni OCCT çizim yolu yalnızca X=0 düzlemini destekliyor.",["section"],"Yazılıma kademeli kesit desteği eklenmeli. Doğru girdiyi değiştirmek gerekli değildir."));
        return result.DistinctBy(i=>(i.Code,i.Message)).ToArray();
    }
    public static List<WorkflowIssue> CheckMeasurements(JsonElement plan,List<Dictionary<string,string>> rows)
    {
        var errors=new List<WorkflowIssue>();
        foreach(var row in rows)
        {
            string product=row["jpeg file name"];
            try
            {
                var points=new Dictionary<string,(double X,double Y,double Diameter)>();
                foreach(var hole in plan.GetProperty("holes").EnumerateArray())
                {
                    if(hole.TryGetProperty("presentIfColumn",out var presence)&&presence.ValueKind==JsonValueKind.String&&string.IsNullOrEmpty(row[presence.GetString()!]))continue;
                    points.Add(hole.GetProperty("id").GetString()!,(
                        CadPlanWorkflow.Expression(hole.GetProperty("xExpression").GetString()!,row),
                        CadPlanWorkflow.Expression(hole.GetProperty("yExpression").GetString()!,row),
                        CadPlanWorkflow.Expression(hole.GetProperty("diameterExpression").GetString()!,row)));
                }
                foreach(var dimension in plan.GetProperty("dimensions").EnumerateArray())
                {
                    string feature=dimension.GetProperty("feature").GetString()!,column=dimension.GetProperty("column").GetString()!,kind=dimension.GetProperty("kind").GetString()!;
                    if(row[column].Length==0)continue;
                    double actual;
                    if(kind=="diameter")actual=feature=="body"?CadPlanWorkflow.Expression(plan.GetProperty("parameters").GetProperty("outerDiameterExpression").GetString()!,row):points[feature].Diameter;
                    else if(kind=="centerDistance"){var ids=feature.Split(':');var a=points[ids[0]];var b=points[ids[1]];actual=Math.Sqrt(Math.Pow(a.X-b.X,2)+Math.Pow(a.Y-b.Y,2));}
                    else if(kind=="horizontalOffset")actual=Math.Abs(points[feature].X);
                    else if(kind=="verticalOffset")actual=Math.Abs(points[feature].Y);
                    else throw new Exception("Desteklenmeyen ölçü türü.");
                    double expected=GroupWorkflow.Value(row[column]);
                    if(Math.Abs(expected-actual)>1e-5)errors.Add(new("MODEL_MEASUREMENT_CONFLICT","model","error",$"{product}: modelde {column}={actual}, Excel nominali {expected}.",[product,column],"Model geometrik ilişkisi düzeltilmeli; geçerli Excel değeri değiştirilmemeli."));
                }
            }catch(Exception ex){errors.Add(new("PLAN_VALIDATION","model","error",product+": "+ex.Message,[product],"Planın özellik/sütun eşleşmeleri düzeltilmeli."));}
        }
        return errors;
    }
    public static List<Dictionary<string,string>> ReadRows(string path)
    {
        using var wb=new XLWorkbook(path);var ws=wb.Worksheets.First();
        var headers=ws.Row(1).CellsUsed().Select(c=>(Name:c.GetString().Trim().Trim('\'', '’','‘'),Column:c.Address.ColumnNumber)).ToList();
        if(headers.Any(h=>h.Name.Length==0)||headers.Select(h=>h.Name).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=headers.Count)throw new Exception("Boş/tekrarlı başlık.");
        if(!headers.Any(h=>h.Name=="jpeg file name"))throw new Exception("jpeg file name sütunu yok.");
        var rows=ws.RowsUsed().Skip(1).Where(r=>headers.Any(h=>!r.Cell(h.Column).IsEmpty())).Select(r=>headers.ToDictionary(h=>h.Name,h=>r.Cell(h.Column).GetFormattedString().Trim())).ToList();
        if(rows.Count==0||rows.Select(r=>r["jpeg file name"]).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=rows.Count)throw new Exception("Veri yok veya tekrarlı çıktı adı.");
        return rows;
    }
    public static void ReconcileAdvisories(List<WorkflowIssue> issues,JsonElement plan,List<Dictionary<string,string>> rows)
    {
        string part=plan.TryGetProperty("partNumberColumn",out var pn)?pn.GetString()??"H":"H";
        bool supported=true;
        foreach(var r in rows)foreach(var (column,value) in r)
            if(column!="jpeg file name"&&column!=part&&value.Length>0)
                try{_=GroupWorkflow.Value(value);}catch{supported=false;}
        if(supported)
        {
            for(int i=0;i<issues.Count;i++)if(issues[i].Origin=="model"&&issues[i].Code.Contains("TOLERANCE",StringComparison.OrdinalIgnoreCase))
                issues[i]=issues[i] with{RecommendedAction="Yerel ayrıştırıcı bu dosyadaki nominal/tolerans biçimlerini başarıyla okudu. Bu model önerisi nedeniyle Excel sütunlarını ayırmayın."};
        }
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
