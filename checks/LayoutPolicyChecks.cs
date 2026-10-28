
static void Check(bool condition,string name){if(!condition)throw new Exception(name);Console.WriteLine("PASS "+name);}
var p=new ScalePolicy();
Check(LayoutPolicy.ChooseScale(new(136,136,116,116),p)==2,"compact envelope");
foreach(var size in new[]{227,259,286})Check(LayoutPolicy.ChooseScale(new(size,size,116,116),p)==2.5f,"shared reference scale "+size);
var scale=LayoutPolicy.ChooseScale(new(400,80,100,40),p);Check(400/scale<=100&&80/scale<=40,"noncircular envelope respects both axes");
try{LayoutPolicy.ChooseScale(new(0,10,100,100),p);throw new Exception("invalid input accepted");}catch(ArgumentException){Console.WriteLine("PASS invalid envelope rejected");}
var placement=LayoutPolicy.LeaderLabel(new(20,20),new(0,0),12);
Check(Math.Abs(placement.Angle-45)<.01,"readable leader angle");
Check(Math.Abs(Math.Sqrt(placement.TextAnchor.X*placement.TextAnchor.X+placement.TextAnchor.Y*placement.TextAnchor.Y)-12)<.01,"label offset from outer endpoint");
var sizes=DimensionTypography.Sizes(DimensionTypography.DefaultScale);
Check(Math.Abs(sizes.Nominal-13.75f)<.001f,"dimension nominal size increased ten percent");
Check(Math.Abs(sizes.Tolerance-9.35f)<.001f,"tolerance proportion preserved");
try{DimensionTypography.Sizes(float.NaN);throw new Exception("invalid scale accepted");}catch(ArgumentOutOfRangeException){Console.WriteLine("PASS invalid typography scale rejected");}
var row=new Dictionary<string,string>{{"jpeg file name","test"},{"A","Ø160±1"},{"B","88,9±0,5"},{"C","Ø10 (+0,1|-0,0)"},{"D","Ø10 (+0,1|-0,0)"},{"E","Ø5 (+0,1|-0,0)"},{"F","44,5±0,5"},{"G","44,45±0,5"},{"H","test"}};
Check(GroupWorkflow.ValidateRow(row,8).Count==0,"supported geometry preflight");
var missing=new Dictionary<string,string>(row);missing["E"]="";
Check(GroupWorkflow.ValidateRow(missing).Count>0,"partial optional feature rejected");
var zero=new Dictionary<string,string>(row);zero["F"]="0";
Check(GroupWorkflow.ValidateRow(zero,8).Count==0,"zero position keeps optional hole");
var collide=new Dictionary<string,string>(zero);collide["E"]="Ø100";
Check(GroupWorkflow.ValidateRow(collide,8).Any(e=>e.Contains("çakışıyor")),"hole collision rejected");
var edge=new Dictionary<string,string>(row);edge["F"]="100";
Check(GroupWorkflow.ValidateRow(edge,8).Count>0,"hole outside face rejected");
var data=Enumerable.Range(0,83).Select(i=>{var r=new Dictionary<string,string>(row);r["jpeg file name"]="part-"+i;return r;}).ToList();
Check(GroupWorkflow.SampleRows(data).Count<=8,"83 rows do not produce 83 API sample rows");
using(var workbook=new ClosedXML.Excel.XLWorkbook())
{
    var path=Path.Combine(Path.GetTempPath(),Guid.NewGuid()+".xlsx");
    try
    {
        var sheet=workbook.AddWorksheet("data");var cols=row.Keys.ToArray();
        for(int c=0;c<cols.Length;c++)sheet.Cell(1,c+1).Value=cols[c];
        for(int r=0;r<data.Count;r++)for(int c=0;c<cols.Length;c++)sheet.Cell(r+2,c+1).Value=data[r][cols[c]];
        workbook.SaveAs(path);Check(GroupWorkflow.Read(path).Count==83,"83-row workbook read without rendering or API");
    }finally{File.Delete(path);}
}
try{GroupWorkflow.Value("-1");throw new Exception("negative dimension accepted");}catch(Exception ex)when(ex.Message.StartsWith("Geçersiz ölçü")){Console.WriteLine("PASS unsupported negative dimension rejected");}
using(var candidate=System.Text.Json.JsonDocument.Parse("""{"rules":{"UpperY":"B/2","LowerY":"-B/2"}}"""))
{
    var asymmetric=new Dictionary<string,string>(row);asymmetric["B"]="165,4±0,5";asymmetric["G"]="78,7±0,5";
    Check(GroupWorkflow.MeasurementFeedback(candidate.RootElement,new(){asymmetric}).Any(e=>e.Contains("78.7")||e.Contains("78,7")),"generated feedback catches false symmetry");
}
Check(GroupWorkflow.ExtractJson("text\n```json\n{\"ok\":true}\n```")=="{\"ok\":true}","single fenced object extracted without accepting ambiguous blocks");
OcctSheetService.ValidateCamera(new(new double[]{1,-1,1},new double[]{0,1,0},"orthographic","medium"));
Console.WriteLine("PASS explicit camera accepted");
try{OcctSheetService.ValidateCamera(new(new double[]{0,1,0},new double[]{0,1,0},"orthographic","high"));throw new Exception("parallel camera accepted");}catch(Exception ex)when(ex.Message.Contains("çakışıyor")){Console.WriteLine("PASS degenerate camera rejected");}
try{OcctSheetService.ValidateCamera(new(new double[]{1,-1,1},new double[]{0,1,0},"orthographic","low"));throw new Exception("uncertain camera accepted");}catch(Exception ex)when(ex.Message.Contains("belirsiz")){Console.WriteLine("PASS uncertain camera rejected");}
using(var plan=System.Text.Json.JsonDocument.Parse(File.ReadAllText("checks/fixtures/camera-low-plan.json")))
{
    Check(GroupWorkflow.CheckPlan(plan.RootElement).Count>0,"uncertain camera blocks production");
    Check(GroupWorkflow.CheckPlan(plan.RootElement,true).Count==0,"camera-only uncertainty permits a review preview");
    var node=System.Text.Json.Nodes.JsonNode.Parse(plan.RootElement.GetRawText())!;
    node["questions"]=new System.Text.Json.Nodes.JsonArray("Third-hole position is unclear.");
    using var unsafePlan=System.Text.Json.JsonDocument.Parse(node.ToJsonString());
    Check(GroupWorkflow.CheckPlan(unsafePlan.RootElement,true).Count>0,"geometry questions still block preview");
}
var example=new Dictionary<string,string>{{"A","Ø286±1"},{"B","139,7±0,5"},{"C","Ø21 (+0,1|-0,0)"},{"D","Ø12,6 (+0,1|-0,0)"},{"E","11-30-121"}};
Check(Math.Abs(CadPlanWorkflow.Expression("-B/2",example)+69.85)<1e-6,"restricted expression evaluates target row");
try{CadPlanWorkflow.Expression("System.IO.File.Delete(x)",example);throw new Exception("code expression accepted");}catch(Exception ex)when(ex.Message.StartsWith("Desteklenmeyen ifade")){Console.WriteLine("PASS arbitrary model code rejected");}
var temporaryFont=Path.GetTempFileName();var previousFont=Environment.GetEnvironmentVariable("DRAWING_FONT_PATH");
try
{
    // Placeholder path tests JSON lifetime only; no glyph rendering or fake-font acceptance claim.
    Environment.SetEnvironmentVariable("DRAWING_FONT_PATH",temporaryFont);object resolved;
    using(var doc=System.Text.Json.JsonDocument.Parse(File.ReadAllText("checks/fixtures/cad-plan.json")))resolved=CadPlanWorkflow.Resolve(doc.RootElement,example,"11-30-121","samples/highres-reference.jpg");
    var encoded=System.Text.Json.JsonSerializer.Serialize(resolved);
    Check(encoded.Contains("fixedAnnotations")&&encoded.Contains("geometricTolerances"),"resolved CAD plan survives source JsonDocument disposal");
}finally{Environment.SetEnvironmentVariable("DRAWING_FONT_PATH",previousFont);File.Delete(temporaryFont);}
using(var blockedPlan=System.Text.Json.JsonDocument.Parse("""{"section":{"plane":"offset"},"issues":[]}"""))
{
    var report=WorkflowReports.Inspect(blockedPlan.RootElement);
    Check(report.Any(i=>i.Code=="UNSUPPORTED_SECTION"&&i.Category=="software"),"unsupported cut reported as software limitation, not bad input");
}
using(var questionPlan=System.Text.Json.JsonDocument.Parse("""{"section":{"plane":"X=0"},"questions":["Confirm radius?"]}"""))
    Check(WorkflowReports.Inspect(questionPlan.RootElement).Any(i=>i.Code=="QUESTION_RESPONSE"),"legacy question output rejected as protocol report");
Check(WorkflowReports.ExitCode("blocked-with-report")==2,"blocked run has distinct nonzero exit code");
using(var wrong=System.Text.Json.JsonDocument.Parse("""{"parameters":{"outerDiameterExpression":"A"},"holes":[{"id":"u","diameterExpression":"C","xExpression":"0","yExpression":"B/2"},{"id":"l","diameterExpression":"D","xExpression":"0","yExpression":"-B/2"}],"dimensions":[{"kind":"verticalOffset","feature":"l","column":"G"}]}"""))
{
    var asymmetric=new Dictionary<string,string>{{"jpeg file name","row"},{"A","Ø286±1"},{"B","165,4±0,5"},{"C","Ø21 (+0,1|-0,0)"},{"D","Ø12,6 (+0,1|-0,0)"},{"G","78,7±0,5"}};
    Check(WorkflowReports.CheckMeasurements(wrong.RootElement,new(){asymmetric}).Any(i=>i.Code=="MODEL_MEASUREMENT_CONFLICT"),"group report checks model offsets against actual Excel");
}
var symmetricCell=ExcelModelInput.ParseCell("Ø227±1");
Check(symmetricCell.state=="number"&&symmetricCell.nominalMm==227&&symmetricCell.diameterSymbol==true&&symmetricCell.tolerance!.upperDeviationMm==1&&symmetricCell.tolerance.lowerDeviationMm==-1,"nominal geometry and signed symmetric tolerance separated");
var asymmetricCell=ExcelModelInput.ParseCell("Ø21 (+0,1|-0,0)");
Check(asymmetricCell.nominalMm==21&&asymmetricCell.tolerance!.upperDeviationMm==0.1&&asymmetricCell.tolerance.lowerDeviationMm==0,"asymmetric decimal-comma tolerance parsed without changing geometry");
Check(ExcelModelInput.ParseCell(" ").state=="blank"&&ExcelModelInput.ParseCell(" ").nominalMm is null,"empty cell never becomes numeric zero");
var zeroCell=ExcelModelInput.ParseCell("0,00±0,5");
Check(zeroCell.state=="number"&&zeroCell.isZero==true&&zeroCell.tolerance!.lowerDeviationMm==-0.5,"real zero remains present even with tolerance");
Check(ExcelModelInput.ParseCell("11-30-381").state=="text","part identifier is not parsed as a dimension");
Check(ExcelModelInput.ParseCell("33,0").tolerance is null,"unspecified tolerance is not invented");
foreach(var bad in new[]{"Ø21 (+0,1|oops)","21±x","21±1)","21 (±1","-2"})
{
    try{ExcelModelInput.ParseCell(bad);throw new Exception("malformed notation accepted");}
    catch(FormatException){Console.WriteLine("PASS malformed notation rejected: "+bad);}
}
var structured=ExcelModelInput.Build(new[]{row,zero});
var encodedInput=System.Text.Json.JsonSerializer.Serialize(structured);
Check(!encodedInput.Contains("88,9")&&!encodedInput.Contains("±")&&structured.rows[1].cells["F"].isZero==true,"model input contains typed dimensions instead of raw measurement strings");
var blankPair=new Dictionary<string,string>(row);blankPair["E"]="";blankPair["F"]="";
Check(ExcelModelInput.Build(new[]{blankPair}).rows[0].cells["E"].state=="blank","optional blank pair is preserved without inventing a hole rule");
using(var conditional=System.Text.Json.JsonDocument.Parse("""
{"schemaVersion":2,"kind":"revolved-plate","partNumberColumn":"H","parameters":{"outerDiameterExpression":"A","depthMm":33,"thicknessMm":3,"outerRadiusMm":8},"holes":[{"id":"u","diameterExpression":"C","xExpression":"0","yExpression":"B-G","presentIfColumn":null},{"id":"l","diameterExpression":"D","xExpression":"0","yExpression":"-G","presentIfColumn":null},{"id":"t","diameterExpression":"E","xExpression":"-F","yExpression":"0","presentIfColumn":"E"}],"section":{"mode":"through-features","featureIds":["u","l","t"]},"camera":{"direction":[1,-1,1],"up":[0,1,0],"projection":"orthographic","confidence":"medium"},"dimensions":[{"id":"e","kind":"diameter","feature":"t","column":"E","visible":true,"hideWhen":"never"},{"id":"f","kind":"horizontalOffset","feature":"t","column":"F","visible":true,"hideWhen":"zero"}],"fixedAnnotations":[],"geometricTolerances":[]}
"""))
{
    using var absent=System.Text.Json.JsonDocument.Parse(System.Text.Json.JsonSerializer.Serialize(CadGroupExecutor.Resolve(conditional.RootElement,blankPair,"source.jpg")));
    Check(absent.RootElement.GetProperty("holes").GetArrayLength()==2&&absent.RootElement.GetProperty("drawing").GetProperty("dimensions").GetArrayLength()==0,"executor removes absent optional hole and dependent dimensions");
    using var centered=System.Text.Json.JsonDocument.Parse(System.Text.Json.JsonSerializer.Serialize(CadGroupExecutor.Resolve(conditional.RootElement,zero,"source.jpg")));
    Check(centered.RootElement.GetProperty("holes").GetArrayLength()==3&&!centered.RootElement.GetProperty("drawing").GetProperty("dimensions")[1].GetProperty("visible").GetBoolean(),"executor keeps zero-position hole but hides zero offset annotation");
}
