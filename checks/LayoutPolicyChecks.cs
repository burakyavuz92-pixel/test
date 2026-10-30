using System.Text.Json;
using System.Text.Json.Nodes;
static void Check(bool yes,string name){if(!yes)throw new Exception(name);Console.WriteLine("PASS "+name);}
var recipe=JsonNode.Parse("""
{"schemaVersion":5,"parameters":[{"id":"OD","unit":"mm","source":{"kind":"column","column":"A"}},{"id":"T","unit":"mm","source":{"kind":"column","column":"F"}},{"id":"two","unit":"scalar","source":{"kind":"constant","value":2}},{"id":"R","unit":"mm","source":{"kind":"derived","op":"divide","args":["OD","two"]}}],"frames":[{"id":"main","origin":[0,0,0],"xAxis":[1,0,0],"zAxis":[0,0,1]}],"operations":[{"id":"profile","op":"sketch","frame":"main","inputs":[],"when":{"kind":"always"},"args":{"plane":"XY","loops":[{"kind":"circle","center":[0,0],"diameter":{"param":"OD"}}]}},{"id":"base","op":"extrude","frame":"main","inputs":["profile"],"when":{"kind":"always"},"args":{"length":{"param":"T"},"direction":[0,0,-1]}}],"result":"base","dimensions":[{"id":"od","type":"diameter","parameter":"OD","targets":[{"operation":"base","role":"outerRim"}],"sourceColor":"green","visible":true,"hideIf":{"kind":"never"}}],"geometricTolerances":[],"views":[],"sections":[],"issues":[]}
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
