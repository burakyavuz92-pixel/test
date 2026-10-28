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
    public static List<Dictionary<string,string>> Read(string path)
    {
        using var wb=new XLWorkbook(path);var ws=wb.Worksheets.First();
        var columns=ws.Row(1).CellsUsed().Select(c=>(Name:c.GetString().Trim().Trim('\'', '’','‘'),Col:c.Address.ColumnNumber)).ToList();
        if(columns.Select(c=>c.Name).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=columns.Count)throw new Exception("Tekrarlı sütun.");
        var expected=new[]{"jpeg file name","A","B","C","D","E","F","G","H"};
        if(!columns.Select(c=>c.Name).Order().SequenceEqual(expected.Order()))throw new Exception("Bu akış yalnızca ikinci grubun A–H sütunlarını destekler.");
        var result=ws.RowsUsed().Skip(1).Where(r=>columns.Any(c=>!r.Cell(c.Col).IsEmpty())).Select(r=>columns.ToDictionary(c=>c.Name,c=>r.Cell(c.Col).GetFormattedString().Trim())).ToList();
        if(result.Count==0)throw new Exception("Excel'de veri yok.");
        if(result.Select(r=>r["jpeg file name"]).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=result.Count)throw new Exception("Tekrarlı çıktı adı.");
        return result;
    }
    public static List<string> ValidateRow(Dictionary<string,string> r,double? radius=null)
    {
        var errors=new List<string>();
        try
        {
            if(!Regex.IsMatch(r["jpeg file name"],@"^[A-Za-z0-9_-]+$"))errors.Add("Güvensiz dosya adı.");
            if(string.IsNullOrWhiteSpace(r["H"]))errors.Add("H parça numarası boş.");
            double a=Value(r["A"]),b=Value(r["B"]),g=Value(r["G"]),c=Value(r["C"]),d=Value(r["D"]);
            if(a<=0||b<=0||c<=0||d<=0||g<0||g>b)errors.Add("Geçersiz çap/konum.");
            bool present=r["E"].Length>0;
            if(present!=(r["F"].Length>0))errors.Add("E ve F birlikte dolu/boş olmalı.");
            var holes=new List<(double X,double Y,double D)>{(0,b-g,c),(0,-g,d)};
            if(present && r["F"].Length>0){double e=Value(r["E"]),f=Value(r["F"]);if(e<=0)errors.Add("E çapı pozitif olmalı.");holes.Add((-f,0,e));}
            double boundary=a/2-(radius??0);
            foreach(var h in holes)if(Math.Sqrt(h.X*h.X+h.Y*h.Y)+h.D/2>=boundary)errors.Add("Delik dış kenara/büküm bölgesine taşıyor.");
            for(int i=0;i<holes.Count;i++)for(int j=i+1;j<holes.Count;j++)
                if(Math.Sqrt(Math.Pow(holes[i].X-holes[j].X,2)+Math.Pow(holes[i].Y-holes[j].Y,2))<=(holes[i].D+holes[j].D)/2)errors.Add("Delikler çakışıyor.");
        }
        catch(Exception ex){errors.Add(ex.Message);}
        return errors.Distinct().ToList();
    }
    public static Dictionary<string,string> Rules=new(){["UpperX"]="0",["UpperY"]="B-G",["LowerX"]="0",["LowerY"]="-G",["ThirdX"]="-F",["ThirdY"]="0"};
    public static string ExtractJson(string content)
    {
        content=content.Trim();
        if(content.StartsWith('{'))return content;
        var blocks=Regex.Matches(content,@"```(?:json)?\s*(\{[\s\S]*?\})\s*```",RegexOptions.IgnoreCase);
        if(blocks.Count!=1)throw new Exception("Tek bir JSON nesnesi bekleniyor.");
        return blocks[0].Groups[1].Value;
    }
    public static List<string> MeasurementFeedback(JsonElement plan,List<Dictionary<string,string>> samples)
    {
        var errors=new List<string>();
        double Eval(string expr,Dictionary<string,string> row) => Regex.Replace(expr,@"\s+", "").ToUpperInvariant() switch {
            "0"=>0,"B-G"=>Value(row["B"])-Value(row["G"]),"-G"=>-Value(row["G"]),"B/2"=>Value(row["B"])/2,"-B/2"=>-Value(row["B"])/2,"-F"=>-Value(row["F"]),_=>throw new Exception("Unsupported expression")};
        try
        {
            var rules=plan.GetProperty("rules");
            foreach(var row in samples)
            {
                double upper=Eval(rules.GetProperty("UpperY").GetString()!,row),lower=Eval(rules.GetProperty("LowerY").GetString()!,row);
                double b=Value(row["B"]),g=Value(row["G"]);
                if(Math.Abs(upper-lower-b)>.00001)errors.Add($"{row["jpeg file name"]}: candidate upper-minus-lower={upper-lower}, but measured B={b}.");
                if(Math.Abs(lower+g)>.00001)errors.Add($"{row["jpeg file name"]}: candidate lower distance from origin={-lower}, but measured G={g}. A conditional note about hiding G when it equals B/2 does not impose symmetry when G differs.");
            }
        }catch(Exception ex){errors.Add("Cannot evaluate candidate relations: "+ex.Message);}
        return errors;
    }
    public static List<string> CheckPlan(JsonElement p,bool allowApproximateCamera=false)
    {
        var errors=new List<string>();
        try
        {
            if(p.GetProperty("family").GetString()!="plate-optional-third")errors.Add("Desteklenmeyen geometri ailesi.");
            foreach(var (name,expected) in Rules)
            {var formula=Regex.Replace(p.GetProperty("rules").GetProperty(name).GetString()??"",@"\s+","").ToUpperInvariant();if(formula!=expected)errors.Add(name+" ilişkisi desteklenen geometriye uymuyor: "+formula);}
            if(!p.GetProperty("blankEFMeansAbsent").GetBoolean())errors.Add("Boş E/F sözleşmesi uyuşmuyor.");
            if(!p.GetProperty("hideFWhenZero").GetBoolean()||!p.GetProperty("hideGWhenHalfB").GetBoolean())errors.Add("Ölçü gizleme sözleşmesi uyuşmuyor.");
            foreach(var question in p.GetProperty("questions").EnumerateArray())
            {
                var text=question.GetString()??"";
                bool cameraOnly=Regex.IsMatch(text,@"\A(?:Camera direction|The camera (?:tilt|direction)|Please confirm (?:the )?camera)",RegexOptions.IgnoreCase)
                    && !Regex.IsMatch(text,@"thickness|radius|diameter|hole|coordinate|dimension",RegexOptions.IgnoreCase);
                if(!(allowApproximateCamera && cameraOnly))errors.Add("Açık soru: "+text);
            }
            _=OcctSheetService.Camera(p,allowApproximateCamera);
            var settings=p.GetProperty("renderSettings").Deserialize<SheetSettings>(Json)!;
            if(settings.ThicknessMm<=0||settings.DepthMm<=settings.ThicknessMm||settings.OuterBendRadiusMm is null||settings.OuterBendRadiusMm<=settings.ThicknessMm)errors.Add("Sabit geometri geçersiz.");
            foreach(var field in new[]{"HideThickness","HideDepth","HideRadius"})_ = p.GetProperty("renderSettings").GetProperty(field).GetBoolean();
        }catch(Exception ex){errors.Add("Plan şeması eksik/geçersiz: "+ex.Message);}
        return errors;
    }
    public static List<Dictionary<string,string>> SampleRows(List<Dictionary<string,string>> rows) =>
        rows.GroupBy(r=>(r["E"].Length>0,r["F"].Length>0 && Value(r["F"])==0,Math.Abs(Value(r["G"])-Value(r["B"])/2)<.00001))
            .Select(g=>g.First()).Concat(rows.OrderBy(r=>Value(r["A"])).Take(1))
            .Concat(rows.OrderByDescending(r=>Value(r["A"])).Take(1)).Distinct().Take(8).ToList();
}
