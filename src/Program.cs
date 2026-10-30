try
{
    if(args.Length==4&&args[0]=="analyze-script-group"){await CadScriptWorkflow.Analyze(args[1],args[2],args[3]);return;}
    if(args.Length==2&&args[0]=="run-saved-script"){Environment.ExitCode=await CadScriptWorkflow.Execute(args[1]);return;}
    if(args.Length==5&&args[0]=="render-saved-group"){await NativeRecipeExecutor.RenderSaved(args[1],args[2],args[3],args[4]);return;}
    if(args.Length==2&&args[0]=="approve-cad-recipe"){RecipeLibrary.Approve(args[1]);return;}
    if(args.Length==5&&args[0]=="reuse-cad-group"){RecipeLibrary.Reuse(args[1],args[2],args[3],args[4]);return;}
    if(args.Length==5&&args[0]=="review-cad-group"){CadRecipeWorkflow.Review(args[1],args[2],args[3],args[4]);return;}
    if(args.Length!=4||args[0] is not ("analyze-cad-group" or "run-cad-group" or "analyze-fresh-cad-group"))throw new Exception("Genel CAD v7: analyze-cad-group <xlsx> <jpeg> <empty-output> | run-cad-group <xlsx> <jpeg> <empty-output>. Eski tarif komutları kaldırıldı.");
    await CadRecipeWorkflow.Analyze(args[1],args[2],args[3],execute:args[0]=="run-cad-group",useLibrary:args[0]!="analyze-fresh-cad-group");
}
catch(Exception ex){Console.Error.WriteLine(ex.Message);Environment.ExitCode=1;}
