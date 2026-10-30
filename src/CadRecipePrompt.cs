public static class CadRecipePrompt
{
    public const string Instructions="""
    Read the engineering drawing JPEG and tableInput. Return one shared, parameterized CAD and drawing description for this product group as JSON schemaVersion 8. Apply the specified measurements and complete unspecified geometric details consistently with the drawing. Success contains data only. If impossible, return {"error":"one short Turkish sentence"}.

    INPUT: one JPEG and one locally parsed table. Quoted drawing labels match Excel columns. nominalMm is the geometry value; tolerances are attached locally to annotations. Blank cells stay blank and zero stays zero; interpret them using the drawing. outputId is the filename and title-block quoted H unless H is a numeric measurement. Black and green dimensions describe geometry. sourceColor marks green annotations for local hiding. Red drafting notes concern presentation.

    VALUES: a scalar s is a number, {"column":"A"}, or {"expr":"A / 2 - 3"}. Expressions use column names, decimal numbers, + - * / and parentheses. Each expression is independent; repeat expressions or values wherever useful. Software evaluates them per row. No parameter declarations or helper-variable graph is needed. Length fields are mm, angle fields degrees, counts integers, direction vectors dimensionless. Choose one consistent coordinate system. The software provides frame "world": origin [0,0,0], X [1,0,0], Z [0,0,1]. Optional geometry.frames entries are {id,origin:[s,s,s],xAxis:[x,y,z],zAxis:[x,y,z]}, Y=Z cross X.

    GEOMETRY: geometry.features is an ordered array; each entry {id,kind,args,...} constructs or modifies geometry. frame is optional, default "world". Optional presence={kind:"columnPresent",column} controls a feature according to a nonblank cell. Features are present by default. Write straightforward CAD steps; repeated data is allowed. IDs identify resulting shapes. Dependencies are named fields:
    sketch: args={plane:"XY"|"XZ"|"YZ",loops:[profile,...]}.
      profile={kind:"circle",center:[s,s],diameter:s}; or {kind:"polyline",points:[[s,s],...],closed:true}; or {kind:"roundedSlot",center:[s,s],width:s,length:s,angleDeg:s}; or {kind:"path",segments:[{kind:"line",start:[s,s],end:[s,s]}|{kind:"arc",start:[s,s],mid:[s,s],end:[s,s]}],closed:true}. Slot length is overall tip-to-tip; path arcs pass through all three points.
    extrude: sketch:id, args={length:s,direction:[x,y,z]}.
    revolve: sketch:id, args={axisOrigin:[s,s,s],axisDirection:[x,y,z],angleDeg:s}.
    cylinder: args={diameter:s,length:s,origin:[s,s,s],direction:[x,y,z]}.
    cut: body:id, tool:id, args={}.
    fuse: body:id, additions:[id,...], args={}. Absent additions are skipped.
    hole: body:id, args={diameter:s,origin:[s,s,s],direction:[x,y,z],throughAll:boolean,depth:s|null}.
    circularPattern: seed:id, args={count:s,pitchDiameter:s,startAngleDeg:s,totalAngleDeg:s,center:[s,s,s],axis:[x,y,z]}. Seed is centered at center. Copies lie at pitchDiameter/2, angle=startAngleDeg+i*totalAngleDeg/count, including rotation of seed orientation.
    linearPattern: seed:id, args={count:s,spacing:s,direction:[x,y,z]}, includes seed at index zero.
    fillet/chamfer: body:id, args={size:s,selectors:[{operation:id,role:string,near:[s,s,s],directionKind:"axis"|"tangent",direction:[x,y,z]}]}. near is a point on the intended edge; axis is the circular/elliptic edge rotation axis, tangent is edge tangent at near.
    geometry.result is the final shape ID.

    DRAWING: dimensions, views, sections, details, geometricTolerances are arrays. Describe the template's annotation and view relationships. Geometry values may be repeated in drawing data; construction calculations and annotation values remain independent.
    dimensions: {id,type,valueSource,targets:[{operation:id,role:string}],axis,sourceColor}. type=diameter|pitchDiameter|distance|angle|radius|thickness. axis=X|Y|Z|radial. valueSource={kind:"column",column} for the original measurement with its local tolerance, or {kind:"constant",value:number,unit:"mm"|"deg"}. sourceColor=black|green. Optional quantity defaults 1, visible defaults true, hideIf={kind:"never"}|{kind:"zero"}, default never.
    views: {id,direction:[x,y,z],up:[x,y,z],projection:"orthographic"}. direction is object-to-camera. Include a template-like isometric view.
    sections: {id,view,sourceView,kind:"featureTrace",main:reference,through:[reference,...]}. reference={feature:id,entity:"axis"|"frameOrigin",instance?:integer}. main locates the main trace; through names features crossed by the template's trace. Software constructs cutting coordinates from references and skips absent features. Axis references support hole/cylinder/revolve, circular extrusions, and circularPattern with zero-based instance. frameOrigin uses the feature's frame origin. Alternatively a straight section is {id,view,kind:"planar",frame:"world",point:[s,s,s],normal:[x,y,z]}.
    details: {id,label,sourceView,features:[id,...],sheetBox:[x,y,width,height]}. The box is the detail's location on the original page, normalized 0..1 from top-left. It magnifies existing geometry from the source view/section.
    geometricTolerances: {kind,value:s,targets:[{operation:id,role:string}]}.

    Root: {schemaVersion:8,geometry:{frames:[],features:[],result:id},drawing:{dimensions:[],views:[],sections:[],details:[],geometricTolerances:[]}}.
    """;
}
