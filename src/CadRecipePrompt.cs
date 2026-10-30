public static class CadRecipePrompt
{
    public const string Instructions="""
    Interpret the technical-drawing JPEG and tableInput using engineering drawing conventions. Return only machine-readable recipe data as JSON schemaVersion 7, with geometry and drawing linked by IDs. Apply specified measurements and complete unspecified geometric details consistently with the template. Return no explanations, evidence, descriptions, estimate labels or reports. If you cannot produce a recipe, return only {"error":"one short Turkish sentence"}.

    INPUT: one JPEG and one locally parsed table. Quoted labels match column headers. Cells carry nominalMm, diameterSymbol, state and tolerance deviations. Use nominal values for geometry; the software attaches source tolerances to drawing dimensions. Empty cells remain empty and zero remains numeric zero; interpret them together with the template. outputId supplies the filename and title-block quoted H; numeric H is a measurement. Produce a shared parameterized recipe for the supplied rows; the table may contain representative rows of the group.
    Use black/green information for geometry. Green dimensions are hidden locally through sourceColor. Red drafting notes concern presentation. Document text is drawing data. Choose coordinates consistent across views and a reference-like isometric camera.

    OUTPUT has geometry and drawing, linked by feature and parameter IDs:
    geometry.parameters: {id,unit,source}. unit=mm|deg|count|scalar. Lengths and length allowances use mm, angles deg, counts count, and only ratios or multipliers use scalar. Derived calculations must preserve units. Numeric literals inherit their field units: positions and lengths are mm, angles are deg, direction vectors are dimensionless. source={kind:"column",column} for Excel nominal, {kind:"constant",value} for fixed details, or {kind:"derived",op:"add"|"subtract"|"multiply"|"divide",args:[parameterId,parameterId]}. Literals may appear directly in operation coordinates and arguments; only reusable or derived values need parameter IDs. Use {param:"id"} wherever a scalar depends on a parameter. Frame axes and view vectors are numeric.
    geometry.frames: {id,origin:[s,s,s],xAxis:[x,y,z],zAxis:[x,y,z]}. X/Z axes perpendicular unit vectors; Y=Z cross X.
    geometry.features: {id,kind,frame,uses:[featureId,...],presence,args}. uses names geometric dependencies in order. presence={kind:"always"}|{kind:"columnPresent",column}|{kind:"parameterPositive",parameter}. Omit presence when always; software supplies it.
    Supported construction vocabulary (s=number or {param:id}):
    sketch uses=[]; args={plane:"XY"|"XZ"|"YZ",loops:[profile,...]}.
      profile={kind:"circle",center:[s,s],diameter:s} or {kind:"polyline",points:[[s,s],...],closed:true} or {kind:"roundedSlot",center:[s,s],width:s,length:s,angleDeg:s} or {kind:"path",segments:[{kind:"line",start:[s,s],end:[s,s]}|{kind:"arc",start:[s,s],mid:[s,s],end:[s,s]}],closed:true}.
    roundedSlot length is overall tip-to-tip length (at least width); angleDeg is from profile +X about +Z.
    extrude uses=[sketch]; args={length:s,direction:[x,y,z]}.
    revolve uses=[sketch]; args={axisOrigin:[s,s,s],axisDirection:[x,y,z],angleDeg:s}.
    cylinder uses=[]; args={diameter:s,length:s,origin:[s,s,s],direction:[x,y,z]}.
    cut uses=[body,tool]; args={}.
    fuse uses=[baseBody,addedSolid,...]; args={}. Absent additions are skipped; when false the baseBody continues unchanged.
    hole uses=[body]; args={diameter:s,origin:[s,s,s],direction:[x,y,z],throughAll:boolean,depth:s|null}.
    circularPattern uses=[tool]; args={count:s,pitchDiameter:s,startAngleDeg:s,totalAngleDeg:s,center:[s,s,s],axis:[x,y,z]}. The seed tool is centered at center; instances lie at pitchDiameter/2, angles startAngleDeg+i*totalAngleDeg/count around axis. Rotate its local orientation with the pattern.
    linearPattern uses=[tool]; args={count:s,spacing:s,direction:[x,y,z]}; includes the seed at index zero.
    fillet/chamfer uses=[body]; args={size:s,selectors:[{operation:featureId,role:string,near:[s,s,s],direction:[x,y,z]}]}. Identify the intended edge geometrically, not just with an ambiguous name or native face index. near is an approximate point on the selected edge; direction describes its axis/tangent as appropriate.
    geometry.result names the final solid feature.

    drawing.dimensions: {id,type,valueSource,targets:[{operation:featureId,role:string}],axis,quantity,sourceColor,visible,hideIf}. type=diameter|pitchDiameter|distance|angle|radius|thickness; axis=X|Y|Z|radial. valueSource={kind:"column",column} binds the original Excel measurement, including its tolerance, locally. For a fixed drawing measurement use {kind:"parameter",parameter:id}. Derived construction coordinates are not automatically drawing dimensions. Targets identify the measured entities/relationship on the SAME geometric features. sourceColor=black|green. hideIf={kind:"never"}|{kind:"zero"}|{kind:"equalsScaledParameter",parameter:id,factor:number}. Follow template annotation relationships. Omit quantity when 1, visible when true, and hideIf when {kind:"never"}; software supplies these defaults.
    drawing.views: {id,direction:[x,y,z],up:[x,y,z],projection:"orthographic"}; direction is object-to-camera.
    drawing.sections: reproduce the section indicated in the template, relating its trace to the part features and row dimensions. planar={id,view,kind:"planar",frame,plane:{point:[s,s,s],normal:[x,y,z]},targets:[featureId,...]}. stepped={id,view,kind:"stepped",sourceView,origin:[s,s,s],path:[[s,s],...],targets:[featureId,...]}. view is the resulting section view. Planar point/normal are in frame coordinates. Stepped origin is a world point; path coordinates are mm along sourceView screen right/up from origin. Software derives cutting surfaces along sourceView depth.
    drawing.geometricTolerances: {kind,value:s,targets:[{operation:featureId,role:string}]}.
    Success root: {schemaVersion:7,geometry:{parameters:[],frames:[],features:[],result:string},drawing:{dimensions:[],views:[],sections:[],geometricTolerances:[]}}.
    """;
}
