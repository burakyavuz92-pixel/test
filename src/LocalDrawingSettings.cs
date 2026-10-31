using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// Presentation metadata never enters the API's measurement table.
public sealed record LocalDrawingSettings(string IsoPreset, string SectionDirection, double OffsetMm, double SpanMm)
{
    static readonly string[] Headers={"izometrik aci","kesit dogrultu","kesit kacikligi","kacik kesitin genisligi"};
    static string Normalize(string value)=>string.Concat(value.ToLowerInvariant().Replace('ı','i').Normalize(NormalizationForm.FormD)
        .Where(c=>CharUnicodeInfo.GetUnicodeCategory(c)!=UnicodeCategory.NonSpacingMark)).Normalize(NormalizationForm.FormC).Trim();
    public static bool IsSetting(string key)=>Headers.Contains(Normalize(key));
    public static LocalDrawingSettings? Read(Dictionary<string,string> row)
    {
        var fields=row.Where(kv=>IsSetting(kv.Key)).ToDictionary(kv=>Normalize(kv.Key),kv=>kv.Value.Trim());
        if(fields.Count==0)return null; // Historical workbooks keep their saved recipe views.
        string Need(string key)=>fields.TryGetValue(key,out var value)&&value.Length>0?value:
            throw new FormatException($"{row["jpeg file name"]}: Yerel çizim ayarı eksik: {key}");
        double Number(string key)
        {
            if(!double.TryParse(Need(key).Replace(',','.'),NumberStyles.AllowLeadingSign|NumberStyles.AllowDecimalPoint,
                CultureInfo.InvariantCulture,out var value)||!double.IsFinite(value))
                throw new FormatException($"{row["jpeg file name"]}: {key} sonlu, toleranssız mm değeri olmalı.");
            return value;
        }
        string iso=Need(Headers[0]).ToUpperInvariant(),direction=Need(Headers[1]).ToUpperInvariant();
        if(iso!="ON_SAG")throw new FormatException("Desteklenen izometrik önayar: ON_SAG.");
        if(direction!="V"&&direction!="H")throw new FormatException("Kesit doğrultusu V veya H olmalı.");
        double offset=Number(Headers[2]),span=Number(Headers[3]);
        if(span<0||(offset!=0&&span==0))throw new FormatException("Kaçık kesitte kademe boyu pozitif olmalı; merkez kesitte sıfır olabilir.");
        return new(iso,direction,offset,span);
    }
    public void Apply(JsonNode root)
    {
        var drawing=root["drawing"]!;
        // Object-to-camera: front face +Z, upper right +X,+Y.
        var normal=SectionDirection=="V"?new[]{1,0,0}:new[]{0,1,0};
        var up=SectionDirection=="V"?new[]{0,1,0}:new[]{1,0,0};
        drawing["views"]=JsonSerializer.SerializeToNode(new object[]{
            new{id="front",direction=new[]{0,0,1},up=new[]{0,1,0},projection="orthographic"},
            new{id="section",direction=normal,up,projection="orthographic"},
            new{id="iso",direction=new[]{1,1,1},up=new[]{0,1,0},projection="orthographic"}});
        drawing["sections"]=JsonSerializer.SerializeToNode(new[]{new{id="A-A",view="section",sourceView="front",
            kind="localCentered",direction=SectionDirection,offsetMm=OffsetMm,spanMm=SpanMm}});
        root["localDrawingSettings"]=JsonSerializer.SerializeToNode(this);
    }
}
