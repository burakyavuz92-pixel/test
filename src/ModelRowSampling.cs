using System.Text.Json;

// Select examples for shared functions; execution always retains every original row.
public static class ModelRowSampling
{
    public record Selection(int TotalRows, int UniqueRows, ParsedExcelRow[] Rows,
        object[] Coverage, string Policy = "coverage-and-numeric-diversity-v1");
    static string Signature(ParsedExcelRow r) => JsonSerializer.Serialize(r.cells.OrderBy(x=>x.Key)
        .Select(x=>new {x.Key,x.Value.state,x.Value.nominalMm,x.Value.diameterSymbol,x.Value.radiusSymbol,x.Value.chamferAngleDeg}));
    public static Selection Select(ParsedExcelRow[] rows, int target = 12)
    {
        if(target<1)throw new ArgumentOutOfRangeException(nameof(target));
        var unique=rows.GroupBy(Signature).Select(g=>g.First()).ToArray();
        var keys=unique.SelectMany(r=>ExcelModelInput.Parameters(r).Keys).Distinct().Order().ToArray();
        var orderKeys=keys.Where(k=>!k.EndsWith("__angleDeg",StringComparison.Ordinal)).ToArray();
        var values=unique.Select(ExcelModelInput.Parameters).ToArray();
        double? Value(int i,string k)=>values[i].GetValueOrDefault(k);
        var ranges=keys.ToDictionary(k=>k,k=>values.Select(v=>v.GetValueOrDefault(k)).Where(v=>v.HasValue).Select(v=>v!.Value).ToArray());
        var features=unique.Select(_=>new HashSet<string>()).ToArray();
        for(int i=0;i<unique.Length;i++) {
            foreach(var c in unique[i].cells) {
                features[i].Add($"{c.Key}:state={c.Value.state}:{(c.Value.isZero==true?"zero":"nonzero")}");
                features[i].Add($"{c.Key}:symbols={c.Value.diameterSymbol}/{c.Value.radiusSymbol}");
                if(c.Value.chamferAngleDeg is double angle)features[i].Add($"{c.Key}:angle={angle:R}");
            }
            foreach(var k in keys)if(Value(i,k) is double v && ranges[k].Length>0) {
                if(v==ranges[k].Min())features[i].Add(k+":minimum");
                if(v==ranges[k].Max())features[i].Add(k+":maximum");
                var positive=ranges[k].Where(x=>x>0).ToArray();
                if(positive.Length>0 && v==positive.Min())features[i].Add(k+":minimum-positive");
            }
            // Relative order changes can affect construction, without assuming a particular sketch.
            for(int a=0;a<orderKeys.Length;a++)for(int b=a+1;b<orderKeys.Length;b++)
                if(Value(i,orderKeys[a]) is double x && Value(i,orderKeys[b]) is double y)
                    features[i].Add($"order:{orderKeys[a]}/{orderKeys[b]}={Math.Sign(x-y)}");
        }
        var selected=new List<int>();var covered=new HashSet<string>();
        void Add(int i){selected.Add(i);covered.UnionWith(features[i]);}
        double Distance(int a,int b)=>keys.Sum(k=>{
            var x=Value(a,k);var y=Value(b,k);
            if(!x.HasValue||!y.HasValue)return x.HasValue==y.HasValue?0:1;
            double span=ranges[k].Max()-ranges[k].Min();return span==0?0:Math.Pow((x.Value-y.Value)/span,2);
        });
        if(rows.Length<=target){for(int i=0;i<unique.Length;i++)Add(i);}
        else {
            // Coverage is mandatory: the target is soft, never discard a rare state to meet it.
            while(true){var candidates=Enumerable.Range(0,unique.Length).Except(selected)
                .Select(i=>new{i,gain=features[i].Count(f=>!covered.Contains(f))}).OrderByDescending(x=>x.gain).ThenBy(x=>x.i).ToArray();
                if(candidates.Length==0||candidates[0].gain==0)break;Add(candidates[0].i);}
            while(selected.Count<Math.Min(target,unique.Length)) {
                int next=Enumerable.Range(0,unique.Length).Except(selected)
                    .OrderByDescending(i=>selected.Count==0?0:selected.Min(j=>Distance(i,j))).ThenBy(i=>i).First();Add(next);
            }
        }
        var chosen=selected.Order().ToArray();
        return new(rows.Length,unique.Length,chosen.Select(i=>unique[i]).ToArray(),chosen.Select(i=>(object)new{
            outputId=unique[i].outputId,coveredCases=features[i].Order().ToArray(),
            equivalentOutputIds=rows.Where(r=>Signature(r)==Signature(unique[i])).Select(r=>r.outputId).ToArray()}).ToArray());
    }
}
