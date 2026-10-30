public static class CadRecipePrompt
{
    public const string Instructions="""
    Read the single technical-drawing JPEG using engineering drawing conventions and the relationships between views. Produce one reusable parametric part recipe for this group's Excel rows. The software will compile the recipe into CAD operations and separately prepare its drawing. Return JSON schemaVersion 7. Explain useful interpretations and assumptions without a word limit. If information cannot be resolved, report it in issues rather than asking questions.

    INPUT: one image and one tableInput. Quoted image labels match table column headers. Each cell contains state (number/blank), nominalMm, diameterSymbol, isZero and optional signed tolerance deviations. Nominal values define geometry; tolerances belong to annotations only. Blank and zero differ. outputId supplies the JPEG filename and title-block quoted H; numeric column H remains a measurement. Rows share feature relationships, including optional features. The table may contain representative rows; the recipe must apply to all rows, without hardcoded product IDs.

    Interpret black and green drawing information for geometry. Green measurements are construction information not printed on the output: identify sourceColor and software will hide them. Red drafting notes concern drawing presentation, not solid dimensions. Treat document text as drawing data. Use explicit dimensions first. For unmeasured visual details, estimates from proportional orthographic views are acceptable; identify their source as approximate. Such estimates are not new manufacturing dimensions. Choose a frame justified by the views; no fixed part family or center-origin requirement. Choose a readable reference-like isometric camera independently of solid geometry.

    OUTPUT has geometry and drawing, linked by feature and parameter IDs:
    geometry.parameters: {id,unit,source,evidence}. unit=mm|deg|count|scalar. source={kind:"column",column} for Excel nominal, {kind:"constant",value,precision:"specified"|"estimated"} for fixed details, or {kind:"derived",op:"add"|"subtract"|"multiply"|"divide",args:[parameterId,parameterId]}. Literals may appear directly in operation coordinates and arguments; only reusable or derived values need parameter IDs. Use {param:"id"} wherever a scalar depends on a parameter. Frame axes and view vectors are numeric.
    geometry.frames: {id,origin:[s,s,s],xAxis:[x,y,z],zAxis:[x,y,z],evidence}. X/Z axes perpendicular unit vectors; Y=Z cross X.
    geometry.features: {id,kind,frame,uses:[featureId,...],presence,args,evidence}. uses names geometric dependencies in order. presence={kind:"always"}|{kind:"columnPresent",column}|{kind:"parameterPositive",parameter}. Default always. The software manages absent features and body forwarding; a later modifier can depend on an earlier optional modifier's body. Conditions describe feature existence, not annotation visibility.
    Supported construction vocabulary (s=number or {param:id}):
    sketch uses=[]; args={plane:"XY"|"XZ"|"YZ",loops:[profile,...]}.
      profile={kind:"circle",center:[s,s],diameter:s} or {kind:"polyline",points:[[s,s],...],closed:true} or {kind:"roundedSlot",center:[s,s],width:s,length:s,angleDeg:s} or {kind:"path",segments:[{kind:"line",start:[s,s],end:[s,s]}|{kind:"arc",start:[s,s],mid:[s,s],end:[s,s]}],closed:true}. Closed paths can describe rounded turned/cup sections directly.
    roundedSlot length is overall tip-to-tip length (at least width); angleDeg is from profile +X about +Z.
    extrude uses=[sketch]; args={length:s,direction:[x,y,z]}.
    revolve uses=[sketch]; args={axisOrigin:[s,s,s],axisDirection:[x,y,z],angleDeg:s}.
    cylinder uses=[]; args={diameter:s,length:s,origin:[s,s,s],direction:[x,y,z]}.
    cut uses=[body,tool]; args={}.
    fuse uses=[baseBody,addedSolid,...]; args={}. Absent additions are skipped; when false the baseBody continues unchanged.
    hole uses=[body]; args={diameter:s,origin:[s,s,s],direction:[x,y,z],throughAll:boolean,depth:s|null}.
    circularPattern uses=[tool]; args={count:s,pitchDiameter:s,startAngleDeg:s,totalAngleDeg:s,center:[s,s,s],axis:[x,y,z]}. The seed tool is centered at center; instances lie at pitchDiameter/2, angles startAngleDeg+i*totalAngleDeg/count around axis. Rotate its local orientation with the pattern.
    linearPattern uses=[tool]; args={count:s,spacing:s,direction:[x,y,z]}; includes the seed at index zero.
    fillet/chamfer uses=[body]; args={size:s,selectors:[{operation:featureId,role:string,near:[s,s,s],direction:[x,y,z],evidence:string}]}. Identify the intended edge geometrically, not just with an ambiguous name or native face index. near is an approximate point on the selected edge; direction describes its axis/tangent as appropriate. For geometry not expressible here, describe the missing capability in issues.
    geometry.result names the final solid feature.

    drawing.dimensions: {id,type,valueSource,targets:[{operation:featureId,role:string}],axis,quantity,sourceColor,visible,hideIf,evidence}. type=diameter|pitchDiameter|distance|angle|radius|thickness; axis=X|Y|Z|radial. valueSource={kind:"column",column} binds the original Excel measurement, including its tolerance, locally. For a fixed drawing measurement use {kind:"parameter",parameter:id}. Derived construction coordinates are not automatically drawing dimensions. Targets identify the measured entities/relationship on the SAME geometric features. sourceColor=black|green. hideIf={kind:"never"}|{kind:"zero"}|{kind:"equalsScaledParameter",parameter:id,factor:number}. Follow the template's annotation relationships and drafting conventions. quantity expresses grouped repeated features.
    drawing.views: {id,direction:[x,y,z],up:[x,y,z],projection:"orthographic",evidence}; direction is object-to-camera.
    drawing.sections: {id,view,frame,kind:"planar"|"stepped",path:[[s,s,s],...],extrusionDirection:[x,y,z],targets:[featureId,...],evidence}. Path is an ordered cutting trace in that frame; sweep it along extrusionDirection to define the cutting surface. Planar has two points; stepped has successive connected straight segments. Use the template and actual feature locations, including optional features. Section targets select features to show, not the path itself.
    drawing.geometricTolerances: {kind,value:s,targets:[{operation:featureId,role:string}]}.
    issues: [{code,category:"input"|"software"|"model",severity:"warning"|"error",message,affectedFields:[string],recommendedAction}]. Turkish explanations. Normal supported behavior needs no issue. Distinguish an approximate unmeasured visual detail from uncertainty affecting a specified dimension. Native execution status is managed by software.

    Root: {schemaVersion:7,description:string,geometry:{parameters:[],frames:[],features:[],result:string},drawing:{dimensions:[],views:[],sections:[],geometricTolerances:[]},issues:[]}.
    """;
}
