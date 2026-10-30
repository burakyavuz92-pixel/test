try
{
    if(args.Length==5&&args[0]=="review-cad-group"){CadRecipeWorkflow.Review(args[1],args[2],args[3],args[4]);return;}
    if(args.Length!=4||args[0] is not ("analyze-cad-group" or "run-cad-group"))throw new Exception("Genel CAD v7: analyze-cad-group <xlsx> <jpeg> <empty-output> | run-cad-group <xlsx> <jpeg> <empty-output>. Eski tarif komutları kaldırıldı.");
    await CadRecipeWorkflow.Analyze(args[1],args[2],args[3],execute:args[0]=="run-cad-group");
}
catch(Exception ex){Console.Error.WriteLine(ex.Message);Environment.ExitCode=1;}
