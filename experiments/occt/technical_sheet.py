"""OCCT-derived drawing curves/sections with a separate SVG annotation layer."""
import base64,io,math,re,json,html,pathlib
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from OCP.HLRBRep import HLRBRep_Algo,HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Pln,gp_Trsf,gp_Vec
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section,BRepAlgoAPI_Cut,BRepAlgoAPI_Common,BRepAlgoAPI_Fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_HSequenceOfShape
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
import cairosvg


def edge_points(edge):
    curve=BRepAdaptor_Curve(edge);sample=GCPnts_QuasiUniformDeflection(curve,.03)
    if not sample.IsDone():raise RuntimeError('OCCT curve sampling failed')
    points=[sample.Value(i) for i in range(1,sample.NbPoints()+1)]
    if edge.Orientation()==TopAbs_REVERSED:points.reverse()
    return points


def curves(shape):
    if shape.IsNull():return []
    result=[];exp=TopExp_Explorer(shape,TopAbs_EDGE)
    while exp.More():result.append(edge_points(TopoDS.Edge_s(exp.Current())));exp.Next()
    return result


def closed_wires(shape):
    edges=TopTools_HSequenceOfShape();exp=TopExp_Explorer(shape,TopAbs_EDGE)
    while exp.More():edges.Append(exp.Current());exp.Next()
    wires=TopTools_HSequenceOfShape();ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(edges,1e-6,False,wires)
    result=[]
    for i in range(1,wires.Length()+1):
        wire=TopoDS.Wire_s(wires.Value(i));explorer=BRepTools_WireExplorer(wire);pts=[]
        while explorer.More():pts.extend(edge_points(explorer.Current()));explorer.Next()
        if pts and pts[0].Distance(pts[-1])<1e-5:result.append((wire,pts))
        else:raise RuntimeError('Open section wire')
    return result


def section_bands(data):
    spec=data.get('drawing',{}).get('section')
    if not isinstance(spec,dict):return [(0,-data['outerDiameterMm'],data['outerDiameterMm'])]
    if spec['mode']!='through-features':raise ValueError('Unsupported section mode')
    targets=sorted([h for h in data['holes'] if h['id'] in spec['featureIds']],key=lambda h:h['yMm'])
    if not targets:raise ValueError('Section has no active targets')
    # The supported view keeps Y and depth unchanged, using parallel X planes.
    if abs(targets[0]['xMm'])>1e-6 or abs(targets[-1]['xMm'])>1e-6:raise ValueError('Section endpoints must lie on the main center plane')
    for a,b in zip(targets,targets[1:]):
        if b['yMm']-a['yMm']<a['diameterMm']/2+b['diameterMm']/2+1e-5:
            raise ValueError('No safe section transition between target holes')
    bounds=[-data['outerDiameterMm']]+[(a['yMm']+a['diameterMm']/2+b['yMm']-b['diameterMm']/2)/2 for a,b in zip(targets,targets[1:])]+[data['outerDiameterMm']]
    bands=[]
    for h,lo,hi in zip(targets,bounds,bounds[1:]):
        if bands and abs(bands[-1][0]-h['xMm'])<1e-6:bands[-1]=(h['xMm'],bands[-1][1],hi)
        else:bands.append((h['xMm'],lo,hi))
    return bands


def offset_section(shape,data,bands):
    faces=[];R=data['outerDiameterMm'];depth=data['depthMm']
    for x,lo,hi in bands:
        clip=BRepPrimAPI_MakeBox(gp_Pnt(-R,lo,-depth-1),2*R,hi-lo,depth+2).Shape()
        part=BRepAlgoAPI_Common(shape,clip);part.Build()
        if not part.IsDone():raise RuntimeError('Section band clipping failed')
        op=BRepAlgoAPI_Section(part.Shape(),gp_Pln(gp_Pnt(x,0,0),gp_Dir(1,0,0)),False);op.Build()
        if not op.IsDone():raise RuntimeError('Offset section failed')
        for wire,_ in closed_wires(op.Shape()):
            face=BRepBuilderAPI_MakeFace(wire,True).Face();tr=gp_Trsf();tr.SetTranslation(gp_Vec(-x,0,0))
            faces.append(BRepBuilderAPI_Transform(face,tr,True).Shape())
    if not faces:raise RuntimeError('Empty offset section')
    merged=faces[0]
    for face in faces[1:]:
        fuse=BRepAlgoAPI_Fuse(merged,face);fuse.Build()
        if not fuse.IsDone():raise RuntimeError('Section face union failed')
        merged=fuse.Shape()
    unify=ShapeUpgrade_UnifySameDomain(merged,True,True,False);unify.Build();merged=unify.Shape()
    loops=[pts for _,pts in closed_wires(merged)]
    return curves(merged),loops


def derive(shape,data):
    algo=HLRBRep_Algo();algo.Add(shape);algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(0,0,1),gp_Dir(1,0,0))));algo.Update();algo.Hide()
    converter=HLRBRep_HLRToShape(algo);front=curves(converter.VCompound())+curves(converter.Rg1LineVCompound())
    op=BRepAlgoAPI_Section(shape,gp_Pln(gp_Pnt(),gp_Dir(1,0,0)),False);op.Build()
    if not op.IsDone():raise RuntimeError('OCCT section failed')
    section=op.Shape();edges=TopTools_HSequenceOfShape();exp=TopExp_Explorer(section,TopAbs_EDGE)
    while exp.More():edges.Append(exp.Current());exp.Next()
    wires=TopTools_HSequenceOfShape();ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(edges,1e-6,False,wires)
    loops=[]
    for i in range(1,wires.Length()+1):
        wire=TopoDS.Wire_s(wires.Value(i));explorer=BRepTools_WireExplorer(wire);pts=[]
        while explorer.More():pts.extend(edge_points(explorer.Current()));explorer.Next()
        if pts and pts[0].Distance(pts[-1])<1e-5:loops.append(pts)
    if not front or not loops:raise RuntimeError('Drawing curves/closed section loops absent')
    R=data['outerDiameterMm']/2;depth=data['depthMm']
    half=BRepPrimAPI_MakeBox(gp_Pnt(0,-R-1,-depth-1),R+1,2*R+2,depth+2).Shape()
    cut=BRepAlgoAPI_Cut(shape,half);cut.Build()
    if not cut.IsDone():raise RuntimeError('Section half-space cut failed')
    projection=HLRBRep_Algo();projection.Add(cut.Shape());projection.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(1,0,0),gp_Dir(0,0,-1))));projection.Update();projection.Hide()
    visible=curves(HLRBRep_HLRToShape(projection).VCompound())
    bands=section_bands(data)
    if len(bands)>1:
        section_edges,loops=offset_section(shape,data,bands)
        # Compute rear visibility per band. Keep actual hole edges; remove only
        # clipping-boundary edges created by the artificial band transitions.
        visible=[];R=data['outerDiameterMm'];depth=data['depthMm']
        for x,lo,hi in bands:
            clip=BRepPrimAPI_MakeBox(gp_Pnt(-R,lo,-depth-1),2*R,hi-lo,depth+2).Shape()
            band=BRepAlgoAPI_Common(shape,clip);band.Build()
            half=BRepPrimAPI_MakeBox(gp_Pnt(x,lo-1,-depth-1),R-x,hi-lo+2,depth+2).Shape()
            cut=BRepAlgoAPI_Cut(band.Shape(),half);cut.Build()
            if not band.IsDone() or not cut.IsDone():raise RuntimeError('Band visibility cut failed')
            projection=HLRBRep_Algo();projection.Add(cut.Shape());projection.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(1,0,0),gp_Dir(0,0,-1))));projection.Update();projection.Hide()
            for pts in curves(HLRBRep_HLRToShape(projection).VCompound()):
                if all(abs(p.Y()-lo)<1e-6 for p in pts) or all(abs(p.Y()-hi)<1e-6 for p in pts):continue
                visible.append(pts)

    else:section_edges=curves(section)
    return front,section_edges,loops,visible


def write_sheet(shape,data,out):
    drawing=data['drawing'];front,section,loops,section_visible=derive(shape,data)
    source=Image.open(drawing['source']).convert('RGB');dpi=Image.open(drawing['source']).info.get('dpi')
    if not dpi or abs(dpi[0]-dpi[1])>.1:raise ValueError('Equal source X/Y DPI required')
    dpi=round(dpi[0]);W,H=1754,1240;LW=1487;LH=source.height/source.width*LW
    if source.size!=(7016,4961):raise ValueError('Source layout is not supported')
    page_scale=min(W/LW,H/LH);available_mm=580*page_scale/(dpi/25.4)
    denominator=next(n for n in (1,2,2.5,5,10,20,50) if data['outerDiameterMm']/n<=available_mm)
    s=dpi/25.4/page_scale/denominator;r=data['outerDiameterMm']*s/2;cx,cy,left=778,431,260
    # Preserve source border/title block but remove old engineering views/annotations.
    from PIL import ImageDraw
    bg=source.copy();paint=ImageDraw.Draw(bg);k=source.width/LW
    for box in [(95,65,1074,835),(1160,40,1445,445),(1328,943,1450,964),(1165,806,1191,831),(1412,848,1450,861)]:paint.rectangle(tuple(round(v*k) for v in box),fill='white')
    bg.thumbnail((W,H),Image.Resampling.LANCZOS);buf=io.BytesIO();bg.save(buf,format='PNG')
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {LW} {LH}">',f'<image width="{LW}" height="{LH}" href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"/>','<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M-1,1 L1,-1 M0,5 L5,0 M4,6 L6,4" stroke="#444" stroke-width=".45"/></pattern></defs>']
    font=TTFont(drawing['fontPath']);family=font['name'].getDebugName(1)
    if family!='Arial':raise ValueError('Arial font required')
    glyphs=font.getGlyphSet();cmap=font.getBestCmap();units=font['head'].unitsPerEm
    def text(value,x,y,size=13.75,angle=0,center=False):
        advance=sum(glyphs[cmap[ord(c)]].width for c in value)
        offset=-advance*size/units/2 if center else 0
        svg.append(f'<g data-text="{html.escape(value,quote=True)}" transform="translate({x},{y}) rotate({angle}) translate({offset},0)"><title>{html.escape(value)}</title>')
        pos=0
        for ch in value:
            glyph=glyphs[cmap[ord(ch)]];pen=SVGPathPen(glyphs);glyph.draw(pen)
            svg.append(f'<path d="{pen.getCommands()}" transform="translate({pos*size/units},0) scale({size/units},{-size/units})" fill="black"/>');pos+=glyph.width
        svg.append('</g>')
    def path(pts,mapper,close=False,fill='none'):
        xy=[mapper(p) for p in pts];d='M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in xy)+(' Z' if close else '')
        svg.append(f'<path d="{d}" fill="{fill}" stroke="black" stroke-width=".8"/>')
    for pts in front:path(pts,lambda p:(cx+p.X()*s,cy-p.Y()*s))
    for pts in loops:path(pts,lambda p:(left-p.Z()*s,cy-p.Y()*s),True,'url(#hatch)')
    for pts in section_visible:path(pts,lambda p:(left+p.X()*s,cy-p.Y()*s))
    for pts in section:path(pts,lambda p:(left-p.Z()*s,cy-p.Y()*s))
    def line(x,y,u,v,dash=False):svg.append(f'<path d="M{x},{y} L{u},{v}" stroke="black" stroke-width="{.5 if dash else .8}" fill="none"'+(' stroke-dasharray="16 4 3 4"' if dash else '')+'/>')
    def arrow(x,y,dx,dy):
        n=math.hypot(dx,dy);dx/=n;dy/=n
        svg.append(f'<path d="M{x},{y} L{x+dx*7-dy*2},{y+dy*7+dx*2} L{x+dx*7+dy*2},{y+dy*7-dx*2} Z"/>')
    def tolerance(raw,x,y,angle=0):
        m=re.fullmatch(r'(.*?)\s*\(\s*(\+[^|]+)\|\s*([^)]+)\)',raw)
        if m:
            svg.append(f'<g transform="translate({x},{y}) rotate({angle})">');nom=m[1].strip();text(nom,0,0)
            w=sum(glyphs[cmap[ord(c)]].width for c in nom)*13.75/units+4;text('(',w,0);text(m[2],w+5,-6,9.35);text(m[3],w+5,4,9.35);text(')',w+31,0);svg.append('</g>')
        else:text(re.sub(r'\s*±\s*', ' (±',raw)+(')' if '±' in raw else ''),x,y,angle=angle,center=True)
    line(cx-r-12,cy,cx+r+12,cy,True);line(cx,cy-r-30,cx,cy+r+30,True)
    holes={h['id']:h for h in data['holes']}
    for h in holes.values():
        x,y=cx+h['xMm']*s,cy-h['yMm']*s;half=h['diameterMm']*s/2+7;line(x-half,y,x+half,y,True);line(x,y-half,x,y+half,True)
    measured=[]
    def nominal(raw):return float(re.search(r'\d+(?:[.,]\d+)?',raw)[0].replace(',','.'))
    for dim in drawing['dimensions']:
        raw,feature=dim['valueText'],dim['feature']
        if dim['kind']=='diameter':actual=data['outerDiameterMm'] if feature=='body' else holes[feature]['diameterMm']
        elif dim['kind']=='centerDistance':
            h1,h2=[holes[i] for i in feature.split(':')];actual=math.hypot(h1['xMm']-h2['xMm'],h1['yMm']-h2['yMm'])
        elif dim['kind']=='horizontalOffset':actual=abs(holes[feature]['xMm'])
        elif dim['kind']=='verticalOffset':actual=abs(holes[feature]['yMm'])
        else:raise ValueError('Unsupported dimension kind')
        if not math.isclose(actual,nominal(raw),abs_tol=1e-5):raise ValueError('Dimension does not match OCCT model: '+dim['id'])
        measured.append(dict(id=dim['id'],modelValueMm=actual,valueText=raw,visible=dim['visible']))
        if not dim['visible']:continue
        if feature=='body':
            x,yt,yb=157,cy-r,cy+r;line(x,yt,left+data['outerRadiusMm']*s,yt);line(x,yb,left+data['outerRadiusMm']*s,yb);line(x,yt,x,yb);arrow(x,yt,0,1);arrow(x,yb,0,-1);tolerance(raw,x-9,cy,-90)
        elif dim['kind']=='centerDistance':
            yt,yb=sorted((cy-h1['yMm']*s,cy-h2['yMm']*s));x=463
            line(x,yt,cx-15,yt);line(x,yb,cx-15,yb);line(x,yt,x,yb);arrow(x,yt,0,1);arrow(x,yb,0,-1);tolerance(raw,x-9,(yt+yb)/2,-90)
        elif dim['kind']=='horizontalOffset':
            h=holes[feature];x1,x2=sorted((cx,cx+h['xMm']*s));y=cy-r-27
            line(x1,y,x1,cy-h['yMm']*s);line(x2,y,x2,cy-h['yMm']*s);line(x1,y,x2,y);arrow(x1,y,1,0);arrow(x2,y,-1,0);tolerance(raw,(x1+x2)/2,y-9)
        elif dim['kind']=='verticalOffset':
            h=holes[feature];y1,y2=sorted((cy,cy-h['yMm']*s));x=cx+r+32
            line(cx,y1,x,y1);line(cx,y2,x,y2);line(x,y1,x,y2);arrow(x,y1,0,1);arrow(x,y2,0,-1);tolerance(raw,x+19,(y1+y2)/2,-90)
        else:
            h=holes[feature];upper=h['yMm']>=0;side=-1 if h['xMm']<-.001 or abs(h['yMm'])<1e-6 else (1 if upper else -1)
            hx,hy=cx+h['xMm']*s+side*h['diameterMm']*s*.4,cy-h['yMm']*s+(-1 if upper else 1)*h['diameterMm']*s*.3
            if abs(h['yMm'])<1e-6:ex,ey=cx-r-65,cy-r*.45
            else:ex,ey=cx+side*r*.72,cy+(-1 if upper else 1)*(r+35)
            line(hx,hy,ex,ey);arrow(hx,hy,ex-hx,ey-hy)
            angle=math.degrees(math.atan2(ey-hy,ex-hx));angle=angle-180 if angle>90 else angle+180 if angle< -90 else angle
            tolerance(raw,ex,ey-10,angle)
    # Fixed annotations are visibility-controlled by the model, not injected from a previous group.
    for annotation in drawing['fixedAnnotations']:
        if not annotation['visible']:continue
        kind=annotation['kind'];depth=data['depthMm'];thickness=data['thicknessMm'];radius=data['outerRadiusMm'];right=left+depth*s;yt,yb=cy-r,cy+r
        if kind=='depth':line(left,yt,left,yt-25);line(right,yt,right,yt-25);line(left,yt-20,right,yt-20);arrow(left,yt-20,1,0);arrow(right,yt-20,-1,0);text(str(depth).replace('.',','),(left+right)/2,yt-27,center=True)
        elif kind=='thickness':x=left+depth*s*.6;line(x,yb-thickness*s-15,x,yb+25);arrow(x,yb-thickness*s,0,-1);arrow(x,yb,0,1);text(str(thickness).replace('.',','),x-6,yb+35,center=True)
        elif kind=='radius':hx,hy=left+radius*s*(1-2**-.5),yt+radius*s*(1-2**-.5);line(hx,hy,left-45,yt-30);arrow(hx,hy,-1,-1);text('R'+str(radius).rstrip('0').rstrip('.') if isinstance(radius,str) else 'R'+f'{radius:g}',left-60,yt-38)
    for tol in drawing.get('geometricTolerances',[]):
        if not tol['visible']:continue
        if tol['kind']!='flatness':raise ValueError('Unsupported geometric tolerance')
        y=cy+100;svg.append(f'<rect x="182" y="{y}" width="52" height="21" fill="white" stroke="black" stroke-width=".8"/>');line(203,y,203,y+21)
        svg.append(f'<path d="M188,{y+16} L191,{y+5} L199,{y+5} L196,{y+16} Z" fill="none" stroke="black" stroke-width=".8"/>')
        text(f"{tol['valueMm']:g}".replace('.',','),206,y+15,12.5);line(234,y+10,left,y+10);arrow(left,y+10,-1,0)
    section_spec=drawing.get('section');section_label=section_spec.get('label','A-A') if isinstance(section_spec,dict) else 'A-A'
    mark=section_label.split('-')[0]
    bands=section_bands(data)
    for i,(x,lo,hi) in enumerate(bands):
        lo=max(lo,-data['outerDiameterMm']/2-18/s);hi=min(hi,data['outerDiameterMm']/2+18/s)
        line(cx+x*s,cy-lo*s,cx+x*s,cy-hi*s,True)
        if i<len(bands)-1:line(cx+x*s,cy-hi*s,cx+bands[i+1][0]*s,cy-hi*s,True)
    arrow(cx,cy-r-18,1,0);arrow(cx,cy+r+18,1,0);text(mark,cx+14,cy-r-22,11);text(mark,cx+14,cy+r+35,11)
    text('KESİT '+section_label ,left+20,795,12.5,center=True);text('SECTION '+section_label,left+20,813,12.5,center=True)
    text(data['product'],1350,959,12.5);text(f'1:{denominator:g}',1167,820,10);text('ÖZEL' if dpi!=150 else 'A4',1415,858,9)
    text('OCCT ön görünüş ve koşullu A-A kesiti • Arial ölçüler • İzometrik ölçeksiz',390,855,9)
    text(f'{W}×{H} px • {dpi} DPI • %100 boyutta yazdırın',390,871,9)
    iso=Image.open(out/'occt-preview.png');ib=io.BytesIO();iso.save(ib,format='PNG')
    svg.append(f'<image x="1170" y="65" width="268" height="305" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{base64.b64encode(ib.getvalue()).decode()}"/>');svg.append('</svg>')
    (out/'technical-sheet.svg').write_text(''.join(svg));cairosvg.svg2png(url=str(out/'technical-sheet.svg'),write_to=str(out/'technical-sheet.png'))
    with Image.open(out/'technical-sheet.png') as im:im.convert('RGB').save(out/'technical-sheet.jpeg',quality=96,dpi=(dpi,dpi))
    info={'frontGeometry':'OCCT HLRBRep visible edges','sectionGeometry':'OCCT parallel sections + coplanar face union' ,'sectionBands':section_bands(data),'sectionClosedLoops':len(loops),'frontEdgeCount':len(front),'annotations':'SVG paths from actual Arial glyphs, anchored to model coordinates','dimensions':measured,'pixelSize':[W,H],'dpi':dpi,'mainScale':denominator,'physicalSizeMm':[W/dpi*25.4,H/dpi*25.4],'limits':['Profile-specific sheet layout','Parallel stepped sections only; centered endpoints and separated Y bands required','No global dimension collision solver','Font height currently configured, not image-estimated']}
    (out/'drawing-checks.json').write_text(json.dumps(info,ensure_ascii=False,indent=2));return info
