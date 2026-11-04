using System.Globalization;
using System.Text.RegularExpressions;

// Parse once locally. The API receives one typed table; annotation retains source tolerance.
public record ParsedTolerance(string kind, double upperDeviationMm, double lowerDeviationMm);
public record ParsedExcelCell(string state, double? nominalMm = null, bool? isZero = null,
    bool? diameterSymbol = null, ParsedTolerance? tolerance = null, string? text = null, string? threadCallout = null, string? displayText = null, double? chamferAngleDeg = null);
public record ParsedExcelRow(string outputId, Dictionary<string, ParsedExcelCell> cells);
public record ExcelApiInput(int schemaVersion, string lengthUnit, ParsedExcelRow[] rows);

public static class ExcelModelInput
{
    const string Number = @"\d+(?:[.,]\d+)?";
    static readonly Regex Measurement = new(
        @"^\s*(?<diameter>[Øø⌀])?\s*(?<nominal>" + Number + @")\s*(?:" +
        @"±\s*(?<symmetric>" + Number + @")|\(\s*±\s*(?<symmetric>" + Number + @")\s*\)|" +
        @"\(\s*\+\s*(?<upper>" + Number + @")\s*\|\s*[-−]\s*(?<lower>" + Number + @")\s*\))?\s*$",
        RegexOptions.CultureInvariant);
    static double Numeric(string value) => double.Parse(value.Replace(',', '.'), CultureInfo.InvariantCulture);

    public static ParsedExcelCell ParseCell(string source)
    {
        string value = source.Trim();
        if (value.Length == 0) return new("blank");
        // Preserve product identifiers as text, even when they start with digits.
        if (Regex.IsMatch(value, @"^\d+(?:-\d+){2,}$")) return new("text", text: value);
        var chamfer=Regex.Match(value,@"^(?<leg>"+Number+@")\s*[xX×]\s*(?<angle>"+Number+@")\s*°$");
        if(chamfer.Success) {
            double leg=Numeric(chamfer.Groups["leg"].Value),angle=Numeric(chamfer.Groups["angle"].Value);
            if(!double.IsFinite(leg)||!double.IsFinite(angle)||angle<=0||angle>=90)throw new FormatException("Pah açısı 0 ile 90 derece arasında olmalı.");
            return new("number",leg,leg==0,false,displayText:value,chamferAngleDeg:angle);
        }
        var m = Measurement.Match(value);
        if (m.Success)
        {
            double nominal = Numeric(m.Groups["nominal"].Value);
            ParsedTolerance? tolerance = null;
            if (m.Groups["symmetric"].Success)
            {
                double deviation = Numeric(m.Groups["symmetric"].Value);
                tolerance = new("symmetric", deviation, -deviation);
            }
            else if (m.Groups["upper"].Success)
                tolerance = new("asymmetric", Numeric(m.Groups["upper"].Value), -Numeric(m.Groups["lower"].Value));
            return new("number", nominal, nominal == 0, m.Groups["diameter"].Success, tolerance);
        }
        // Parenthesized suffix is opaque presentation text, never a thread specification.
        var suffix = Regex.Match(value, @"^(?<base>[^()]+)\((?<display>.*)\)$");
        if (suffix.Success && Measurement.IsMatch(suffix.Groups["base"].Value))
            return ParseCell(suffix.Groups["base"].Value) with { displayText = suffix.Groups["display"].Value };
        // Never silently reinterpret an unrecognized tolerance/dimension as an identifier.
        if (Regex.IsMatch(value, @"^[+\-−\d.,Øø⌀]|[±Øø⌀]"))
            throw new FormatException("Desteklenmeyen ölçü/tolerans biçimi: " + value);
        return new("text", text: value);
    }

    static readonly string[] PresentationSuffixes = ["_METIN", "_TOLUST", "_TOLALT", "_TOL_UST", "_TOL_ALT"];
    public static bool IsPresentationColumn(string name) => PresentationSuffixes.Any(s => name.EndsWith(s, StringComparison.Ordinal));
    static string BaseColumn(string name) => name[..^PresentationSuffixes.First(s => name.EndsWith(s, StringComparison.Ordinal)).Length];
    static string? Presentation(Dictionary<string,string> row, string label, params string[] suffixes)
    {
        var present = suffixes.Select(s => label+s).Where(row.ContainsKey).ToArray();
        if (present.Length > 1) throw new FormatException(label+": aynı sunum alanı iki sütunda verilmiş.");
        return present.Length == 0 || string.IsNullOrWhiteSpace(row[present[0]]) ? null : row[present[0]];
    }
    static double Deviation(string? text)
    {
        if (text is null) return 0;
        if (!double.TryParse(text.Trim().Replace(',', '.'), NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out var n) || !double.IsFinite(n))
            throw new FormatException("Tolerans sayısal olmalı: "+text);
        return n;
    }
    public static ExcelApiInput Build(IEnumerable<Dictionary<string, string>> rows) => new(1, "mm",
        rows.Select(row => {
            LocalDrawingSettings.Read(row);
            var geometry = row.Keys.Where(k => k != "jpeg file name" && !LocalDrawingSettings.IsSetting(k) && !IsPresentationColumn(k)).ToArray();
            foreach (var key in row.Keys.Where(IsPresentationColumn))
                if (!geometry.Contains(BaseColumn(key))) throw new FormatException(row["jpeg file name"]+" / "+key+": karşılık gelen geometri sütunu yok.");
            var cells = new Dictionary<string,ParsedExcelCell>();
            foreach (var key in geometry)
            {
                try {
                    var cell=ParseCell(row[key]);
                    if(cell.state=="text")throw new FormatException("Ölçü sütunu sayısal değer veya boş hücre içermeli.");
                    var text=Presentation(row,key,"_METIN");
                    var upper=Presentation(row,key,"_TOLUST","_TOL_UST");
                    var lower=Presentation(row,key,"_TOLALT","_TOL_ALT");
                    if(cell.state=="blank" && (text is not null || upper is not null || lower is not null))
                        throw new FormatException("Metin/tolerans için geometri değeri gerekli.");
                    if(text is not null) {
                        cell=cell with {displayText=text};
                    }
                    if(upper is not null || lower is not null) {
                        if(cell.tolerance is not null)throw new FormatException("Toleransı hem ölçü hücresinde hem ayrı sütunda vermeyin.");
                        double u=Deviation(upper), l=-Math.Abs(Deviation(lower));
                        if(l>u)throw new FormatException("Alt tolerans üst toleranstan büyük olamaz.");
                        cell=cell with {tolerance=new(Math.Abs(u+l)<1e-12 ? "symmetric" : "asymmetric",u,l)};
                    }
                    cells.Add(key,cell);
                }
                catch(FormatException ex) {throw new FormatException($"{row["jpeg file name"]} / {key}: {ex.Message}");}
            }
            return new ParsedExcelRow(row["jpeg file name"],cells);
        }).ToArray());

    // Generated angle parameters keep p[label] numeric and retain each row's angle.
    public static Dictionary<string,double?> Parameters(ParsedExcelRow row)
    {
        var result=row.cells.ToDictionary(c=>c.Key,c=>c.Value.nominalMm);
        foreach(var cell in row.cells.Where(c=>c.Value.chamferAngleDeg is not null)) {
            var key=cell.Key+"__angleDeg";
            if(result.ContainsKey(key))throw new FormatException("Ayrılmış pah parametresiyle çakışan sütun: "+key);
            result.Add(key,cell.Value.chamferAngleDeg);
        }
        return result;
    }
    // Only geometric cell data enters the model request; presentation remains local.
    public static object ForModel(IEnumerable<Dictionary<string,string>> rows)
    {
        var parsed=Build(rows);
        return new{parsed.schemaVersion,parsed.lengthUnit,rows=parsed.rows.Select(r=>new{r.outputId,
            parameters=Parameters(r),cells=r.cells.ToDictionary(kv=>kv.Key,kv=>new{kv.Value.state,kv.Value.nominalMm,kv.Value.isZero,kv.Value.diameterSymbol,kv.Value.chamferAngleDeg})}).ToArray()};
    }
}
