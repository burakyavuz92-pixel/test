using System.Globalization;
using System.Text.RegularExpressions;

// Parse once locally. The API receives one typed table; annotation retains source tolerance.
public record ParsedTolerance(string kind, double upperDeviationMm, double lowerDeviationMm);
public record ParsedExcelCell(string state, double? nominalMm = null, bool? isZero = null,
    bool? diameterSymbol = null, ParsedTolerance? tolerance = null, string? text = null);
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
        // Never silently reinterpret an unrecognized tolerance/dimension as an identifier.
        if (Regex.IsMatch(value, @"^[+\-−\d.,Øø⌀]|[±Øø⌀]"))
            throw new FormatException("Desteklenmeyen ölçü/tolerans biçimi: " + value);
        return new("text", text: value);
    }

    public static ExcelApiInput Build(IEnumerable<Dictionary<string, string>> rows) => new(1, "mm",
        rows.Select(row => new ParsedExcelRow(row["jpeg file name"], row.Where(kv => kv.Key != "jpeg file name" && kv.Value!=row["jpeg file name"])
            .ToDictionary(kv => kv.Key, kv => {
                try {
                    var cell=ParseCell(kv.Value);
                    if(cell.state=="text")throw new FormatException("Ölçü sütunu sayısal değer veya boş hücre içermeli.");
                    return cell;
                }
                catch (FormatException ex) { throw new FormatException($"{row["jpeg file name"]} / {kv.Key}: {ex.Message}"); }
            }))).ToArray());

}
