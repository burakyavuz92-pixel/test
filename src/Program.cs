using System.Globalization;
using System.Net.Http.Headers;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using ClosedXML.Excel;


var json = new JsonSerializerOptions { WriteIndented = true, PropertyNameCaseInsensitive = true };
try
{
    if (args.Length == 0) throw new Exception("Komutlar: run-cad | render-cad-plan | occt-demo | validate-analysis");
    if(args[0] == "render-cad-group")
    {
        if(args.Length!=5)throw new Exception("render-cad-group <xlsx> <jpeg> <saved-run> <empty-output>");
        await CadGroupWorkflow.RenderSaved(args[1],args[2],args[3],args[4]);return;
    }
    if(args[0] == "review-cad-group")
    {
        if(args.Length!=5)throw new Exception("review-cad-group <xlsx> <jpeg> <saved-run> <empty-output>");
        CadGroupWorkflow.ReviewSaved(args[1],args[2],args[3],args[4]);return;
    }
    if(args[0] == "analyze-cad-group")
    {
        if(args.Length is not (4 or 5)||args.Length==5&&args[4]!="--technical-jargon")throw new Exception("analyze-cad-group <xlsx> <jpeg> <empty-output> [--technical-jargon]");
        await CadGroupWorkflow.Run(args[1],args[2],args[3],analysisOnly:true,technicalJargon:args.Length==5);return;
    }
    if(args[0] == "run-cad-group")
    {
        if(args.Length!=4)throw new Exception("run-cad-group <xlsx> <jpeg> <empty-output>");
        await CadGroupWorkflow.Run(args[1],args[2],args[3]);return;
    }
    if(args[0] == "render-cad-plan")
    {
        if(args.Length!=6)throw new Exception("render-cad-plan <xlsx> <jpeg> <product> <saved-run> <empty-output>");
        await CadPlanWorkflow.RenderSaved(args[1],args[2],args[3],args[4],args[5]);return;
    }
    if(args[0] == "run-cad")
    {
        if(args.Length!=5)throw new Exception("run-cad <xlsx> <jpeg> <product> <empty-output>");
        await CadPlanWorkflow.Run(args[1],args[2],args[3],args[4]);return;
    }
    if(args[0] == "occt-demo")
    {
        if(args.Length!=3)throw new Exception("occt-demo <parameters.json> <empty-output-directory>");
        var python=Environment.GetEnvironmentVariable("OCCT_PYTHON")??"/workspace/occt-venv/bin/python";
        IIsometricBackend backend=new OcctProcessBackend(python,"experiments/occt/worker.py");
        await backend.Generate(args[1],args[2]);return;
    }
    if(args[0] == "validate-analysis")
    {
        if(args.Length != 5) throw new Exception("validate-analysis <xlsx> <reference> <analysis.json> <report.json>");
        using var input = JsonDocument.Parse(File.ReadAllText(args[3]));
        var report = AnalysisValidation.Check(args[1], args[2], input.RootElement);
        File.WriteAllText(args[4], JsonSerializer.Serialize(report, json));
        foreach(var error in report.Errors) Console.Error.WriteLine(error);
        Console.WriteLine(report.Passed ? "Veri kontrolü geçti; görsel/geometrik onay henüz verilmedi." : "Analiz reddedildi.");
        Environment.ExitCode = report.Passed ? 0 : 1;
        return;
    }
    throw new Exception("Geçersiz/eski komut. Güncel akış: run-cad, render-cad-plan, occt-demo.");
}
catch(Exception ex) { Console.Error.WriteLine(ex.Message); Environment.ExitCode=1; }
