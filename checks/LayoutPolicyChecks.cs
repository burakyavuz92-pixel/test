using System.Text.Json;
using System.Text.Json.Nodes;
static void Check(bool yes,string name){if(!yes)throw new Exception(name);Console.WriteLine("PASS "+name);}
var recipe=JsonNode.Parse("""
{"schemaVersion":6,"parameters":[{"id":"OD","unit":"mm","source":{"kind":"column","column":"A"}},{"id":"T","unit":"mm","source":{"kind":"column","column":"F"}},{"id":"two","unit":"scalar","source":{"kind":"constant","value":2}},{"id":"R","unit":"mm","source":{"kind":"derived","op":"divide","args":["OD","two"]}}],"frames":[{"id":"main","origin":[0,0,0],"xAxis":[1,0,0],"zAxis":[0,0,1]}],"operations":[{"id":"profile","op":"sketch","frame":"main","inputs":[],"when":{"kind":"always"},"args":{"plane":"XY","loops":[{"kind":"circle","center":[0,0],"diameter":{"param":"OD"}}]}},{"id":"base","op":"extrude","frame":"main","inputs":["profile"],"when":{"kind":"always"},"args":{"length":{"param":"T"},"direction":[0,0,-1]}}],"result":"base","dimensions":[{"id":"od","type":"diameter","parameter":"OD","targets":[{"operation":"base","role":"outerRim"}],"sourceColor":"green","visible":true,"hideIf":{"kind":"never"}}],"geometricTolerances":[],"views":[],"sections":[],"issues":[]}
""")!;
var row=new Dictionary<string,string>{{"jpeg file name","cover"},{"A","Ø236±1"},{"F","5"}};
JsonElement Doc(JsonNode n)=>JsonSerializer.SerializeToElement(n);
var resolved=CadRecipe.Resolve(Doc(recipe),row);
Check(resolved.GetProperty("parameters").GetProperty("R").GetDouble()==118,"derived radius computed from a diameter without model formula code");
Check(resolved.GetProperty("operations")[1].GetProperty("args").GetProperty("length").GetDouble()==5,"Excel thickness bound to generic extrusion");
Check(!resolved.GetProperty("dimensions")[0].GetProperty("effectiveVisible").GetBoolean(),"green annotation hidden locally");
Check(recipe["dimensions"][0]["visible"].GetValue<bool>(),"raw recipe visibility unmodified");
Check(resolved.GetProperty("executionStatus").GetString()=="recipe-resolved-not-rendered","resolution does not claim native execution");
void Reject(Action<JsonNode> mutate,string name){var bad=recipe.DeepClone();mutate(bad);Check(CadRecipe.Check(Doc(bad),new(){row}).Any(i=>i.Severity=="error"),name);}
Reject(n=>n["parameters"][2]["source"]=JsonNode.Parse("""{"kind":"derived","op":"multiply","args":["R","two"]}"""),"cyclic parameter references rejected");
Reject(n=>n["parameters"][2]["source"]["value"]=0,"division by zero rejected");
Reject(n=>n["parameters"][2]["unit"]="mm","dimensionally invalid diameter division rejected");
Reject(n=>n["operations"][0]["inputs"]=new JsonArray("base"),"cyclic operations rejected");
Reject(n=>n["operations"][1]["inputs"]=new JsonArray("missing"),"unknown operation dependency rejected");
Reject(n=>n["operations"][1]["op"]="exec","model executable operation rejected");
Reject(n=>n["frames"][0]["xAxis"]=new JsonArray(0,0,1),"invalid frame rejected");
Reject(n=>n["operations"][1]["when"]=JsonNode.Parse("""{"kind":"parameterPositive","parameter":"missing"}"""),"unknown presence parameter rejected");
Reject(n=>n["operations"][1]["args"].AsObject().Remove("length"),"operation required arguments checked");
Check(ExcelModelInput.ParseCell("Ø11,7±0,1").tolerance!.upperDeviationMm==.1,"cover tolerances parsed");
Check(ExcelModelInput.ParseCell("0").isZero==true&&ExcelModelInput.ParseCell("").state=="blank","zero is not absence");
Check(!CadRecipePrompt.Instructions.Contains("kind:\"revolved-plate\""),"new model schema has no fixed plate family");
var rounded=recipe.DeepClone();rounded["frames"][0]["xAxis"]=new JsonArray(0.7071,0.7071,0);
var roundResult=CadRecipe.Resolve(Doc(rounded),row);
Check(roundResult.GetProperty("frames")[0].GetProperty("basisNormalizationApplied").GetBoolean(),"rounded unit vectors normalized without modifying source recipe");
Check(Math.Abs(roundResult.GetProperty("frames")[0].GetProperty("xAxis")[0].GetDouble()-Math.Sqrt(.5))<1e-10,"native-bound frame has unit-length axes");
var conditional=recipe.DeepClone();
conditional["parameters"].AsArray().Add(JsonNode.Parse("""{"id":"optionalDiameter","unit":"mm","source":{"kind":"column","column":"E"}}"""));
conditional["operations"].AsArray().Add(JsonNode.Parse("""{"id":"optionalHole","op":"hole","frame":"main","target":"base","tool":null,"inputs":[],"optionalInputs":[],"when":{"kind":"columnPresent","column":"E"},"args":{"diameter":{"param":"optionalDiameter"},"origin":[0,0,0],"direction":[0,0,-1],"throughAll":true,"depth":null}}"""));
conditional["operations"].AsArray().Add(JsonNode.Parse("""{"id":"nextHole","op":"hole","frame":"main","target":"optionalHole","tool":null,"inputs":[],"optionalInputs":[],"when":{"kind":"always"},"args":{"diameter":1,"origin":[1,0,0],"direction":[0,0,-1],"throughAll":true,"depth":null}}"""));
conditional["dimensions"].AsArray().Add(JsonNode.Parse("""{"id":"optionalDim","type":"diameter","parameter":"optionalDiameter","targets":[{"operation":"optionalHole","role":"holeAxis"}],"sourceColor":"black","visible":true,"hideIf":{"kind":"never"}}"""));
conditional["sections"]=JsonNode.Parse("""[{"id":"AA","targets":["optionalHole","nextHole"]}]""");conditional["result"]="nextHole";
var noE=new Dictionary<string,string>(row){["E"]=""};var withE=new Dictionary<string,string>(row){["E"]="Ø5"};
var without=CadRecipe.Resolve(Doc(conditional),noE);var with=CadRecipe.Resolve(Doc(conditional),withE);
Check(without.GetProperty("operations").EnumerateArray().Single(o=>o.GetProperty("id").GetString()=="optionalHole").GetProperty("op").GetString()=="passThrough","absent modifier passes target body through without binding blank args");
Check(without.GetProperty("operations").EnumerateArray().Single(o=>o.GetProperty("id").GetString()=="nextHole").GetProperty("target").GetString()=="optionalHole","next modifier follows same body chain even when optional feature is absent");
Check(!without.GetProperty("featureApplied").GetProperty("optionalHole").GetBoolean()&&with.GetProperty("featureApplied").GetProperty("optionalHole").GetBoolean(),"body availability and feature presence tracked separately");
Check(without.GetProperty("dimensions").GetArrayLength()==1&&with.GetProperty("dimensions").GetArrayLength()==2,"absent feature dimension removed while existing body dimension retained");
Check(without.GetProperty("sections")[0].GetProperty("targets").GetArrayLength()==1,"absent feature removed from section targets");
var ambiguous=conditional.DeepClone();ambiguous["operations"][2]["inputs"]=new JsonArray("base");
Check(CadRecipe.Check(Doc(ambiguous),new(){withE}).Any(i=>i.Severity=="error"),"modifier cannot mix target with alternate inputs");
var cycleTarget=conditional.DeepClone();cycleTarget["operations"][2]["target"]="nextHole";
Check(CadRecipe.Check(Doc(cycleTarget),new(){withE}).Any(i=>i.Message.Contains("Döngüsel")),"cycles through target references rejected");

// Public v7 contract separates solid geometry from source-linked drawing measurements.
var v7=JsonNode.Parse("""
{"schemaVersion":7,"description":"cover","geometry":{"parameters":[],"frames":[],"features":[],"result":"base"},"drawing":{"dimensions":[],"views":[],"sections":[],"geometricTolerances":[]},"issues":[]}
""")!;
v7["geometry"]["parameters"]=recipe["parameters"].DeepClone();
v7["geometry"]["parameters"][2]["source"]["precision"]="specified";
v7["geometry"]["frames"]=recipe["frames"].DeepClone();
foreach(var op in recipe["operations"].AsArray())v7["geometry"]["features"].AsArray().Add(new JsonObject{["id"]=op["id"].DeepClone(),["kind"]=op["op"].DeepClone(),["frame"]=op["frame"].DeepClone(),["uses"]=op["inputs"].DeepClone(),["args"]=op["args"].DeepClone()});
var dimension=recipe["dimensions"][0].DeepClone();dimension.AsObject().Remove("parameter");dimension["valueSource"]=JsonNode.Parse("""{"kind":"column","column":"A"}""");v7["drawing"]["dimensions"].AsArray().Add(dimension);
var v7result=CadRecipeV7.Resolve(Doc(v7),row);
Check(v7result.GetProperty("drawing").GetProperty("dimensions")[0].GetProperty("sourceMeasurement").GetProperty("tolerance").GetProperty("upperDeviationMm").GetDouble()==1,"v7 annotation receives original Excel tolerance locally");
Check(!v7result.GetProperty("geometry").TryGetProperty("tolerance",out _),"geometry has no annotation tolerance payload");
Check(v7result.GetProperty("geometry").GetProperty("parameterMetadata").GetProperty("OD").GetProperty("source").GetProperty("column").GetString()=="A","parameter unit and source survive resolution");
var rowChanged=new Dictionary<string,string>(row){["A"]="Ø236±9"};var changed=CadRecipeV7.Resolve(Doc(v7),rowChanged);
Check(changed.GetProperty("geometry").GetRawText()==v7result.GetProperty("geometry").GetRawText(),"changing only tolerance never changes solid geometry");
Check(changed.GetProperty("drawing").GetProperty("dimensions")[0].GetProperty("sourceMeasurement").GetProperty("tolerance").GetProperty("upperDeviationMm").GetDouble()==9,"changed tolerance reaches drawing independently");
var badV7=v7.DeepClone();badV7["drawing"]["dimensions"][0]["valueSource"]["column"]="missing";
Check(CadRecipeV7.Check(Doc(badV7),new(){row}).Any(i=>i.Severity=="error"),"unknown annotation source rejected");
var arcRecipe=v7.DeepClone();arcRecipe["geometry"]["features"][0]["args"]["loops"]=JsonNode.Parse("""[{"kind":"path","closed":true,"segments":[{"kind":"arc","start":[-1,0],"mid":[0,1],"end":[1,0]},{"kind":"line","start":[1,0],"end":[-1,0]}]}]""");
Check(CadRecipeV7.Check(Doc(arcRecipe),new(){row}).All(i=>i.Severity!="error"),"general three-point arc profile supported");
arcRecipe["geometry"]["features"][0]["args"]["loops"][0]["segments"][0]["mid"]=new JsonArray(0,0);
Check(CadRecipeV7.Check(Doc(arcRecipe),new(){row}).Any(i=>i.Severity=="error"),"degenerate profile arc rejected");
var symbolicQuantity=v7.DeepClone();symbolicQuantity["drawing"]["dimensions"][0]["quantity"]=JsonNode.Parse("""{"param":"two"}""");
Check(CadRecipeV7.Resolve(Doc(symbolicQuantity),row).GetProperty("drawing").GetProperty("dimensions")[0].GetProperty("quantity").GetDouble()==2,"symbolic annotation quantity resolved locally");
var v7optional=v7.DeepClone();v7optional["geometry"]["parameters"]=conditional["parameters"].DeepClone();v7optional["geometry"]["parameters"][2]["source"]["precision"]="specified";
foreach(var op in conditional["operations"].AsArray().Skip(2))v7optional["geometry"]["features"].AsArray().Add(new JsonObject{["id"]=op["id"].DeepClone(),["kind"]=op["op"].DeepClone(),["frame"]=op["frame"].DeepClone(),["uses"]=new JsonArray(op["target"].GetValue<string>()),["presence"]=op["when"].DeepClone(),["args"]=op["args"].DeepClone()});
v7optional["geometry"]["result"]="nextHole";
var optionalV7Result=CadRecipeV7.Resolve(Doc(v7optional),noE);
Check(optionalV7Result.GetProperty("geometry").GetProperty("operations").EnumerateArray().Single(o=>o.GetProperty("id").GetString()=="optionalHole").GetProperty("op").GetString()=="passThrough","v7 dependencies compile optional modifier without asking model for body forwarding");
var sectionV7=v7.DeepClone();sectionV7["drawing"]["views"]=JsonNode.Parse("""[{"id":"front","direction":[1,0,0],"up":[0,1,0]}]""");
sectionV7["drawing"]["sections"]=JsonNode.Parse("""[{"id":"AA","view":"front","frame":"main","kind":"planar","plane":{"point":[0,{"param":"R"},0],"normal":[1,0,0]},"targets":["base"]}]""");
Check(CadRecipeV7.Resolve(Doc(sectionV7),row).GetProperty("drawing").GetProperty("sections")[0].GetProperty("cuttingPlanes")[0].GetProperty("point")[1].GetDouble()==118,"section plane uses same resolved geometry parameters");
sectionV7["drawing"]["views"][0]["up"]=new JsonArray(1,0,0);
Check(CadRecipeV7.Check(Doc(sectionV7),new(){row}).Any(i=>i.Severity=="error"),"degenerate camera orientation rejected");
var noQuestion=v7.DeepClone();noQuestion["questions"]=new JsonArray("What size?");
Check(CadRecipeV7.Check(Doc(noQuestion),new(){row}).Any(i=>i.Severity=="error"),"v7 returns reports instead of questions");
var union=v7.DeepClone();union["geometry"]["parameters"].AsArray().Add(JsonNode.Parse("""{"id":"E","unit":"mm","source":{"kind":"column","column":"E"}}"""));
union["geometry"]["features"].AsArray().Add(JsonNode.Parse("""{"id":"extra","kind":"cylinder","frame":"main","uses":[],"presence":{"kind":"parameterPositive","parameter":"E"},"args":{"diameter":10,"length":{"param":"E"},"origin":[0,0,0],"direction":[0,0,1]}}"""));
union["geometry"]["features"].AsArray().Add(JsonNode.Parse("""{"id":"union","kind":"fuse","frame":"main","uses":["base","extra"],"presence":{"kind":"parameterPositive","parameter":"E"},"args":{}}"""));union["geometry"]["result"]="union";
Check(CadRecipeV7.Resolve(Doc(union),noE).GetProperty("geometry").GetProperty("operations").EnumerateArray().Last().GetProperty("op").GetString()=="passThrough","v7 optional union preserves main body when E blank");
Check(CadRecipeV7.Resolve(Doc(union),new Dictionary<string,string>(row){["E"]="0"}).GetProperty("geometry").GetProperty("operations").EnumerateArray().Last().GetProperty("op").GetString()=="passThrough","v7 optional union preserves main body when E zero");
Check(CadRecipeV7.Resolve(Doc(union),withE).GetProperty("geometry").GetProperty("operations").EnumerateArray().Last().GetProperty("op").GetString()=="join","v7 positive addition compiles into deterministic body union");
var dataOnly=v7.DeepClone();dataOnly.AsObject().Remove("description");dataOnly.AsObject().Remove("issues");
void RemoveCommentary(JsonNode node)
{
 if(node is JsonObject obj){foreach(var key in new[]{"evidence","precision","description"})obj.Remove(key);foreach(var child in obj.Select(kv=>kv.Value).Where(v=>v!=null).ToArray())RemoveCommentary(child!);}
 else if(node is JsonArray array)foreach(var child in array.Where(v=>v!=null))RemoveCommentary(child!);
}
RemoveCommentary(dataOnly);
var bareDim=dataOnly["drawing"]["dimensions"][0];foreach(var key in new[]{"quantity","visible","hideIf"})bareDim.AsObject().Remove(key);
var bareResult=CadRecipeV7.Resolve(Doc(dataOnly),row);
Check(bareResult.GetProperty("geometry").GetProperty("parameters").GetProperty("OD").GetDouble()==236,"data-only response accepted without explanations or estimate tags");
Check(bareResult.GetProperty("drawing").GetProperty("dimensions")[0].GetProperty("quantity").GetInt32()==1,"omitted annotation defaults supplied by software");
Check(CadRecipeV7.Check(Doc(dataOnly),new(){row}).All(i=>i.Severity!="error"),"data-only success needs no issues report");
var shortError=JsonDocument.Parse("""{"error":"Taslak okunamıyor."}""");
Check(CadRecipeV7.Check(shortError.RootElement,new(){row}).Single().Code=="MODEL_RECIPE_ERROR","short model failure handled without attempting CAD resolution");
var mixedError=JsonNode.Parse("""{"error":"Hata.","geometry":{}}""");
Check(CadRecipeV7.Check(Doc(mixedError),new(){row}).Single().Code=="MODEL_ERROR_PROTOCOL","mixed success and failure rejected");
var newSection=v7.DeepClone();
newSection["drawing"]["views"]=JsonNode.Parse("""[{"id":"front","direction":[0,0,1],"up":[0,1,0]},{"id":"cut","direction":[1,0,0],"up":[0,1,0]}]""");
newSection["drawing"]["sections"]=JsonNode.Parse("""[{"id":"AA","view":"cut","kind":"planar","frame":"main","plane":{"point":[0,0,0],"normal":[1,0,0]},"targets":["base"]}]""");
Check(CadRecipeV7.Check(Doc(newSection),new(){row}).All(i=>i.Severity!="error"),"point-normal section accepted without model sweep calculation");
newSection["drawing"]["sections"][0]["plane"]["normal"]=new JsonArray(0,0,1);
Check(CadRecipeV7.Check(Doc(newSection),new(){row}).Any(i=>i.Severity=="error"),"horizontal plane rejected for side section view");
newSection["drawing"]["sections"]=JsonNode.Parse("""[{"id":"AA","view":"cut","kind":"stepped","sourceView":"front","origin":[0,0,0],"path":[[0,100],[0,10],[20,10],[20,-10],[0,-10],[0,-100]],"targets":["base"]}]""");
var steppedResult=CadRecipeV7.Resolve(Doc(newSection),row).GetProperty("drawing").GetProperty("sections")[0];
Check(steppedResult.GetProperty("sweepDirection")[2].GetDouble()==1,"stepped sweep derived from source view depth rather than section camera");
Check(steppedResult.GetProperty("cuttingPlanes").GetArrayLength()==5,"all stepped cutting segments represented");
Check(steppedResult.GetProperty("worldPath")[2][0].GetDouble()==20,"source view screen coordinates converted to world points");
newSection["drawing"]["sections"][0]["path"][1]=new JsonArray(0,100);
Check(CadRecipeV7.Check(Doc(newSection),new(){row}).Any(i=>i.Severity=="error"),"zero-length stepped segment rejected");
var oldSection=v7.DeepClone();oldSection["drawing"]["views"]=newSection["drawing"]["views"].DeepClone();
oldSection["drawing"]["sections"]=JsonNode.Parse("""[{"id":"AA","view":"cut","frame":"main","kind":"planar","path":[[0,-150,0],[0,150,0]],"extrusionDirection":[1,0,0],"targets":["base"]}]""");
Check(CadRecipeV7.Check(Doc(oldSection),new(){row}).Any(i=>i.Severity=="error"),"previous cover wrong sweep detected without silently correcting raw recipe");
oldSection["drawing"]["sections"][0]["extrusionDirection"]=new JsonArray(0,0,1);
Check(CadRecipeV7.Check(Doc(oldSection),new(){row}).All(i=>i.Severity!="error"),"historical valid trace remains reviewable");
var featureTrace=v7optional.DeepClone();
featureTrace["geometry"]["parameters"].AsArray().Add(JsonNode.Parse("""{"id":"Q","unit":"mm","source":{"kind":"column","column":"Q"}}"""));
featureTrace["geometry"]["features"][2]["args"]["origin"]=JsonNode.Parse("""[{"param":"Q"},0,0]""");
featureTrace["drawing"]["views"]=JsonNode.Parse("""[{"id":"front","direction":[0,0,1],"up":[0,1,0]},{"id":"cut","direction":[1,0,0],"up":[0,1,0]}]""");
featureTrace["drawing"]["sections"]=JsonNode.Parse("""[{"id":"AA","view":"cut","sourceView":"front","kind":"featureTrace","main":{"feature":"base","entity":"axis"},"through":[{"feature":"optionalHole","entity":"axis"}]}]""");
var ftBlank=new Dictionary<string,string>(noE){["Q"]=""};var ftZero=new Dictionary<string,string>(withE){["Q"]="0"};var ftOffset=new Dictionary<string,string>(withE){["Q"]="44.5"};
var absentTrace=CadRecipeV7.Resolve(Doc(featureTrace),ftBlank);var centerTrace=CadRecipeV7.Resolve(Doc(featureTrace),ftZero);var offsetTrace=CadRecipeV7.Resolve(Doc(featureTrace),ftOffset);
Check(absentTrace.GetProperty("drawing").GetProperty("sections")[0].GetProperty("kind").GetString()=="planar","feature trace skips absent feature without converting blank to zero");
Check(centerTrace.GetProperty("drawing").GetProperty("sections")[0].GetProperty("kind").GetString()=="planar"&&centerTrace.GetProperty("geometry").GetProperty("featureApplied").GetProperty("optionalHole").GetBoolean(),"zero offset becomes planar while real hole remains");
Check(offsetTrace.GetProperty("drawing").GetProperty("sections")[0].GetProperty("kind").GetString()=="stepped","offset feature produces stepped trace without model jog coordinates");
Check(offsetTrace.GetProperty("drawing").GetProperty("sections")[0].GetProperty("worldPath").EnumerateArray().Any(p=>Math.Abs(p[0].GetDouble()-44.5)<1e-9),"derived trace goes through referenced feature");
var oldLibrary=Environment.GetEnvironmentVariable("CAD_RECIPE_LIBRARY");
var cacheRoot=Path.Combine(Path.GetTempPath(),"recipe-library-"+Guid.NewGuid());Directory.CreateDirectory(cacheRoot);
try
{
 Environment.SetEnvironmentVariable("CAD_RECIPE_LIBRARY",Path.Combine(cacheRoot,"library"));
 var excel=Path.Combine(cacheRoot,"input.xlsx");var jpeg=Path.Combine(cacheRoot,"input.jpg");File.WriteAllText(jpeg,"fixture");
 void Workbook(string a,string f)
 {
  using var wb=new ClosedXML.Excel.XLWorkbook();var ws=wb.AddWorksheet("Data");ws.Cell(1,1).Value="jpeg file name";ws.Cell(1,2).Value="A";ws.Cell(1,3).Value="F";ws.Cell(2,1).Value="new-part";ws.Cell(2,2).Value=a;ws.Cell(2,3).Value=f;wb.SaveAs(excel);
 }
 var saved=Path.Combine(cacheRoot,"saved");Directory.CreateDirectory(saved);File.WriteAllText(Path.Combine(saved,"recipe.json"),dataOnly.ToJsonString());
 Workbook("Ø236±1","5");RecipeLibrary.SaveCandidate(saved,jpeg,WorkflowReports.ReadRows(excel));
 Workbook("Ø255±2","6");var reuse=Path.Combine(cacheRoot,"reused");RecipeLibrary.Reuse(excel,jpeg,saved,reuse);
 using(var report=JsonDocument.Parse(File.ReadAllText(Path.Combine(reuse,"run-report.json"))))Check(report.RootElement.GetProperty("Run").GetProperty("ApiCalls").GetInt32()==0&&File.Exists(Path.Combine(reuse,"new-part.resolved.json")),"new nominal rows reuse saved candidate with zero API calls");
 Workbook("Ø255±2","0");var bad=Path.Combine(cacheRoot,"unknown");RecipeLibrary.Reuse(excel,jpeg,saved,bad);
 Check(!File.Exists(Path.Combine(bad,"new-part.resolved.json")),"unseen state pattern rejected without API fallback");
 RecipeLibrary.Approve(saved);Workbook("Ø255±2","6");var approved=Path.Combine(cacheRoot,"approved");RecipeLibrary.Reuse(excel,jpeg,saved,approved);
 using(var report=JsonDocument.Parse(File.ReadAllText(Path.Combine(approved,"run-report.json"))))Check(report.RootElement.GetProperty("Run").GetProperty("RecipeHumanApproved").GetBoolean(),"explicit approval stored separately from candidate verification");
 Check(RecipeLibrary.TryReuseApproved(excel,jpeg,Path.Combine(cacheRoot,"automatic")),"approved matching template automatically selects local recipe");
 File.WriteAllText(jpeg,"different");var wrong=Path.Combine(cacheRoot,"wrong");RecipeLibrary.Reuse(excel,jpeg,saved,wrong);Check(!File.Exists(Path.Combine(wrong,"new-part.resolved.json")),"different template does not silently reuse recipe");
}
finally{Environment.SetEnvironmentVariable("CAD_RECIPE_LIBRARY",oldLibrary);Directory.Delete(cacheRoot,true);Environment.ExitCode=0;}

var anchoredTrace=featureTrace.DeepClone();
foreach(var (id,y) in new[]{("upper",40),("lower",-40)})
{
 var anchorHole=JsonNode.Parse("""{"id":"anchor","kind":"hole","frame":"main","uses":["base"],"args":{"diameter":10,"origin":[0,0,0],"direction":[0,0,1],"throughAll":true,"depth":null}}""")!;
 anchorHole["id"]=id;anchorHole["args"]!["origin"]![1]=y;
 anchoredTrace["geometry"]["features"].AsArray().Add(anchorHole);
}
anchoredTrace["drawing"]["sections"][0]["main"]["feature"]="upper";
anchoredTrace["drawing"]["sections"][0]["through"]=JsonNode.Parse("""[{"feature":"optionalHole","entity":"axis"},{"feature":"lower","entity":"axis"}]""");
var anchoredResult=CadRecipeV7.Resolve(Doc(anchoredTrace),ftOffset);
var anchorPath=anchoredResult.GetProperty("drawing").GetProperty("sections")[0].GetProperty("worldPath").EnumerateArray().Select(p=>p.EnumerateArray().Take(2).Select(v=>v.GetDouble()).ToArray()).ToArray();
Check(FeatureSectionTrace.CoversProjectedPoint(anchorPath,new[]{0.0,40}),"main upper reference belongs to finite stepped trace");
Check(FeatureSectionTrace.CoversProjectedPoint(anchorPath,new[]{44.5,0}),"offset reference remains covered after main-anchor fix");
Check(FeatureSectionTrace.CoversProjectedPoint(anchorPath,new[]{0.0,-40}),"lower reference remains covered after main-anchor fix");
Check(CadRecipeV7.Resolve(Doc(anchoredTrace),ftBlank).GetProperty("drawing").GetProperty("sections")[0].GetProperty("kind").GetString()=="planar","main-anchor fix preserves absent-feature planar section");
Check(CadRecipeV7.Resolve(Doc(anchoredTrace),ftZero).GetProperty("drawing").GetProperty("sections")[0].GetProperty("kind").GetString()=="planar","main-anchor fix preserves zero-offset planar section");
Check(!FeatureSectionTrace.CoversProjectedPoint(new[]{new[]{0.0,10},new[]{0.0,-10}},new[]{0.0,40}),"infinite-plane membership does not count as finite trace coverage");
Check(!FeatureSectionTrace.CoversProjectedPoint(new[]{new[]{0.0,100},new[]{44.5,100},new[]{44.5,-20},new[]{0.0,-20},new[]{0.0,-100}},new[]{0.0,40}),"previous early-jog shape fails main-reference coverage check");
var legacyDetail=newSection.DeepClone();legacyDetail["drawing"]["sections"]=new JsonArray();legacyDetail["drawing"]["details"]=JsonNode.Parse("""[{"id":"B","sourceView":"missing","features":["missing"]}]""");
Check(!CadRecipeV7.Resolve(Doc(legacyDetail),row).GetProperty("drawing").TryGetProperty("details",out _),"legacy detail metadata is excluded from resolved drawings");

var directionRecipe=v7.DeepClone();directionRecipe["geometry"]["features"].AsArray().Add(JsonNode.Parse("""{"id":"edgeRound","kind":"fillet","frame":"main","uses":["base"],"args":{"size":1,"selectors":[{"operation":"base","role":"rim","near":[118,0,0],"directionKind":"axis","direction":[0,0,1]}]}}"""));directionRecipe["geometry"]["result"]="edgeRound";
Check(CadRecipeV7.Check(Doc(directionRecipe),new(){row}).All(i=>i.Severity!="error"),"explicit selector axis type accepted");
directionRecipe["geometry"]["features"].AsArray().Last()["args"]["selectors"][0]["directionKind"]="guess";
Check(CadRecipeV7.Check(Doc(directionRecipe),new(){row}).Any(i=>i.Severity=="error"),"unknown selector direction type rejected");
directionRecipe["geometry"]["features"].AsArray().Last()["args"]["selectors"][0]["directionKind"]="tangent";directionRecipe["geometry"]["features"].AsArray().Last()["args"]["selectors"][0]["direction"]=new JsonArray(0,0,0);
Check(CadRecipeV7.Check(Doc(directionRecipe),new(){row}).Any(i=>i.Severity=="error"),"zero selector direction rejected");

var v8=JsonDocument.Parse("""
{"schemaVersion":8,"geometry":{"frames":[],"features":[{"id":"base","kind":"cylinder","args":{"diameter":{"column":"A"},"length":{"expr":"F + 2 * (3 - 1)"},"origin":[0,0,0],"direction":[0,0,1]}},{"id":"optional","kind":"hole","body":"base","presence":{"kind":"columnPresent","column":"B"},"args":{"diameter":{"column":"B"},"origin":[{"expr":"B / 2"},0,0],"direction":[0,0,1],"throughAll":true,"depth":null}}],"result":"optional"},"drawing":{"dimensions":[{"id":"a","type":"diameter","valueSource":{"kind":"column","column":"A"},"targets":[{"operation":"base","role":"outer"}],"axis":"radial","sourceColor":"black"},{"id":"fixed","type":"thickness","valueSource":{"kind":"constant","value":3,"unit":"mm"},"targets":[{"operation":"base","role":"wall"}],"axis":"Z","sourceColor":"green"}],"views":[],"sections":[],"details":[],"geometricTolerances":[]}}
""").RootElement;
var v8row=new Dictionary<string,string>(row){["B"]=""};
Check(!CadRecipeV7.Check(v8,new(){v8row}).Any(i=>i.Severity=="error"),"v8 independent expressions and blank optional geometry accepted");
var v8resolved=CadRecipeV7.Resolve(v8,v8row);
Check(v8resolved.GetProperty("geometry").GetProperty("operations")[0].GetProperty("args").GetProperty("length").GetDouble()==9,"v8 local arithmetic precedence and parentheses");
Check(v8resolved.GetProperty("drawing").GetProperty("dimensions")[0].GetProperty("sourceMeasurement").GetProperty("tolerance").GetProperty("upperDeviationMm").GetDouble()==1,"v8 retains local source tolerance");
Check(v8resolved.GetProperty("geometry").GetProperty("featureApplied").GetProperty("optional").GetBoolean()==false,"v8 skips absent feature without evaluating blank expression");
Check(CadRecipeV8.Evaluate("-A / 2 + A",new Dictionary<string,double?>{{"A",10}})==5,"v8 repeated columns and unary signs");
foreach(var invalid in new[]{"A / 0","A + unknown","A; print(1)","A / (2 - 2)"}){
    bool rejected=false;try{CadRecipeV8.Evaluate(invalid,new Dictionary<string,double?>{{"A",10}});}catch{rejected=true;}Check(rejected,"v8 rejects unsafe or invalid expression: "+invalid);
}
var v8row2=new Dictionary<string,string>(v8row){["A"]="Ø300±2",["B"]="10",["F"]="7"};
var v8resolved2=CadRecipeV7.Resolve(v8,v8row2);
Check(v8resolved2.GetProperty("geometry").GetProperty("operations")[0].GetProperty("args").GetProperty("diameter").GetDouble()==300,"v8 shared recipe applies second row nominal rather than tolerance");
Check(v8resolved2.GetProperty("geometry").GetProperty("featureApplied").GetProperty("optional").GetBoolean(),"v8 optional feature becomes present on a different row");
Check(v8.GetProperty("schemaVersion").GetInt32()==8&&v8.GetProperty("geometry").GetProperty("features")[0].GetProperty("args").GetProperty("length").TryGetProperty("expr",out _),"v8 lowering preserves original model response");
var v9=JsonDocument.Parse("""
{"schemaVersion":9,"geometry":{"variables":{"r":"=A/2"},"features":[{"id":"body","op":"add","shape":{"kind":"cylinder","origin":[0,0,0],"direction":[0,0,1],"diameter":"=r*2","length":5}}]},"drawing":{"views":[],"sections":[],"dimensions":[],"details":[],"geometricTolerances":[]}}
""").RootElement;
var v9resolved=CadRecipeV7.Resolve(v9,row);
Check(v9resolved.GetProperty("geometry").GetProperty("operations")[0].GetProperty("args").GetProperty("diameter").GetDouble()==236,"v9 C# to local data compiler integration");
Check(v9resolved.GetProperty("geometry").GetProperty("result").GetString()=="body","v9 last current body is result");
var v9plane=JsonNode.Parse(v9.GetRawText())!;
v9plane["drawing"]!["views"]=JsonNode.Parse("""[{"id":"section","direction":[1,0,0],"up":[0,1,0],"projection":"orthographic"}]""");
v9plane["drawing"]!["sections"]=JsonNode.Parse("""[{"id":"A","view":"section","kind":"planar","point":[0,0,0],"normal":[1,0,0]}]""");
Check(CadRecipeV7.Resolve(Doc(v9plane),row).GetProperty("drawing").GetProperty("sections")[0].GetProperty("cuttingPlanes").GetArrayLength()==1,"v9 planar point/normal lowered to native section plane");
var v9trace=JsonNode.Parse(v9plane.ToJsonString())!;
v9trace["drawing"]!["views"]!.AsArray().Add(JsonNode.Parse("""{"id":"front","direction":[0,0,1],"up":[0,1,0],"projection":"orthographic"}"""));
v9trace["drawing"]!["sections"]=JsonNode.Parse("""[{"id":"A","view":"section","sourceView":"front","kind":"featureTrace","main":{"feature":"body","entity":"axis"},"through":[]}]""");
Check(CadRecipeV7.Resolve(Doc(v9trace),row).GetProperty("drawing").GetProperty("sections")[0].GetProperty("cuttingPlanes").GetArrayLength()==1,"v9 feature trace creates reserved section world frame");
