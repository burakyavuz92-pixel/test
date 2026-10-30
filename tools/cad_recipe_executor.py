"""Local resolved-v7 OCCT executor. No API calls or product-family geometry rules."""
import json,math,sys,pathlib,os,traceback
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from OCP.gp import gp_Pnt,gp_Vec,gp_Dir,gp_Ax1,gp_Ax2,gp_Trsf,gp_Pln
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform,BRepBuilderAPI_MakeVertex
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakePrism,BRepPrimAPI_MakeRevol,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Fuse,BRepAlgoAPI_Common,BRepAlgoAPI_Section
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet,BRepFilletAPI_MakeChamfer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Circle,GeomAbs_Ellipse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs,STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.HLRBRep import HLRBRep_Algo,HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/occt'))
from technical_sheet import curves,closed_wires
from worker import render as render_mesh

def unit(x):
 a=np.array(x,dtype=float);n=np.linalg.norm(a)
 if n<1e-10:raise ValueError('Zero direction')
 return a/n

def box(shape):
 b=Bnd_Box();BRepBndLib.Add_s(shape,b);return b.Get()
def vol(shape):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(shape,p);return p.Mass()
def count_solids(s):
 ex=TopExp_Explorer(s,TopAbs_SOLID);n=0
 while ex.More():n+=1;ex.Next()
 return n

def boolean(cls,a,b):
 op=cls(a,b);op.Build()
 if not op.IsDone():raise RuntimeError('OCCT boolean failed')
 return op.Shape()
def fuse(shapes):
 if not shapes:raise ValueError('Empty shape list')
 s=shapes[0]
 for other in shapes[1:]:s=boolean(BRepAlgoAPI_Fuse,s,other)
 return s

def build(recipe):
 g=recipe['geometry'];frames={f['id']:f for f in g['frames']};shapes={};records={};checks=[]
 for op in g['operations']:
  name=op['op'];id=op['id'];a=op.get('args',{});records[id]=op
  if name=='alias':shapes[id]=shapes[op['inputs'][0]];continue
  if name=='passThrough':shapes[id]=shapes[op['target']];continue
  f=frames[op['frame']];x=np.array(f['xAxis']);z=np.array(f['zAxis']);basis=np.column_stack((x,np.cross(z,x),z));origin=np.array(f['origin'])
  def pt(p):return origin+basis@np.array(p,dtype=float)
  def direction(v):return unit(basis@np.array(v,dtype=float))
  def profile(p,plane):
   return pt({'XY':[p[0],p[1],0],'XZ':[p[0],0,p[1]],'YZ':[0,p[0],p[1]]}[plane])
  if name=='sketch':
   faces=[]
   for loop in a['loops']:
    wire=BRepBuilderAPI_MakeWire();kind=loop['kind'];plane=a['plane']
    def line(p,q):wire.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*profile(p,plane)),gp_Pnt(*profile(q,plane))).Edge())
    def arc(p,m,q):wire.Add(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(gp_Pnt(*profile(p,plane)),gp_Pnt(*profile(m,plane)),gp_Pnt(*profile(q,plane))).Value()).Edge())
    if kind=='circle':
     from OCP.Geom import Geom_Circle
     normal=direction({'XY':[0,0,1],'XZ':[0,-1,0],'YZ':[1,0,0]}[plane])
     wire.Add(BRepBuilderAPI_MakeEdge(Geom_Circle(gp_Ax2(gp_Pnt(*profile(loop['center'],plane)),gp_Dir(*normal)),loop['diameter']/2)).Edge())
    elif kind=='polyline':
     p=loop['points']
     if not loop['closed']:raise ValueError('Open profile')
     for u,v in zip(p,p[1:]+p[:1]):line(u,v)
    elif kind=='path':
     for seg in loop['segments']:
      if seg['kind']=='line':line(seg['start'],seg['end'])
      elif seg['kind']=='arc':arc(seg['start'],seg['mid'],seg['end'])
      else:raise ValueError('Unknown segment')
    elif kind=='roundedSlot':
     r=loop['width']/2;h=(loop['length']-loop['width'])/2
     if r<=0 or h<=0:raise ValueError('Slot length must exceed width')
     ang=math.radians(loop['angleDeg']);c=np.array(loop['center']);rot=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
     def p(x,y):return (c+rot@np.array([x,y])).tolist()
     line(p(-h,r),p(h,r));arc(p(h,r),p(h+r,0),p(h,-r));line(p(h,-r),p(-h,-r));arc(p(-h,-r),p(-h-r,0),p(-h,r))
    else:raise ValueError('Unsupported profile '+kind)
    if not wire.IsDone():raise RuntimeError('Invalid wire')
    face=BRepBuilderAPI_MakeFace(wire.Wire(),True).Face();faces.append(face)
   if a.get('profileHoles'):
    body=faces[0]
    for hole in faces[1:]:body=boolean(BRepAlgoAPI_Cut,body,hole)
    shapes[id]=[body];continue
   # Multiple disjoint profiles supported; nested contours must be explicit cuts.
   for i,s in enumerate(faces):
    for t in faces[:i]:
     common=boolean(BRepAlgoAPI_Common,s,t)
     ex=TopExp_Explorer(common,TopAbs_EDGE)
     if ex.More():raise ValueError('Overlapping/nested profile loops need explicit cut')
   shapes[id]=faces;continue
  if name in ('extrude','revolve','throughExtrude'):
   faces=shapes[op['inputs'][0]]
   if name=='throughExtrude':
    target=shapes[op['target']];b=box(target);d=direction(a['direction']);corners=[np.array([x,y,z]) for x in (b[0],b[3]) for y in (b[1],b[4]) for z in (b[2],b[5])];extent=[np.dot(c-origin,d) for c in corners];margin=max(1,np.linalg.norm(np.array(b[3:])-np.array(b[:3]))*.01);lo=min(extent)-margin;hi=max(extent)+margin;tr=gp_Trsf();tr.SetTranslation(gp_Vec(*(d*lo)));s=fuse([BRepPrimAPI_MakePrism(BRepBuilderAPI_Transform(face,tr,True).Shape(),gp_Vec(*(d*(hi-lo)))).Shape() for face in faces])
   elif name=='extrude':s=fuse([BRepPrimAPI_MakePrism(face,gp_Vec(*(direction(a['direction'])*a['length']))).Shape() for face in faces])
   else:s=fuse([BRepPrimAPI_MakeRevol(face,gp_Ax1(gp_Pnt(*pt(a['axisOrigin'])),gp_Dir(*direction(a['axisDirection']))),math.radians(a['angleDeg']),True).Shape() for face in faces])
  elif name=='cylinder':s=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*pt(a['origin'])),gp_Dir(*direction(a['direction']))),a['diameter']/2,a['length']).Shape()
  elif name=='cut':
   target=shapes[op['target']];s=boolean(BRepAlgoAPI_Cut,target,shapes[op['tool']])
   if vol(s)>=vol(target)-1e-7:raise ValueError('Cut does not remove material: '+id)
  elif name in ('fuse','join'):s=fuse(([shapes[op['target']]] if op.get('target') else [])+[shapes[i] for i in op['inputs']])
  elif name=='hole':
   target=shapes[op['target']];b=box(target);reach=np.linalg.norm(np.array(b[3:])-np.array(b[:3]))+1;d=direction(a['direction']);p=pt(a['origin'])
   if a['throughAll']:p=p-d*reach;length=2*reach
   else:length=a['depth']
   tool=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*p),gp_Dir(*d)),a['diameter']/2,length).Shape();s=boolean(BRepAlgoAPI_Cut,target,tool)
   if vol(s)>=vol(target)-1e-7:raise ValueError('Hole does not remove material: '+id)
  elif name in ('circularPattern','linearPattern'):
   seed=shapes[op['inputs'][0]];copies=[];n=int(a['count'])
   for i in range(n):
    tr=gp_Trsf()
    if name=='circularPattern':
     center=pt(a['center']);axis=direction(a['axis']);right=direction([1,0,0]);right=right-axis*np.dot(right,axis)
     if np.linalg.norm(right)<1e-8:right=direction([0,1,0]);right=right-axis*np.dot(right,axis)
     right=unit(right);up=np.cross(axis,right);theta=math.radians(a['startAngleDeg']+i*a['totalAngleDeg']/n)
     rotation=gp_Trsf();rotation.SetRotation(gp_Ax1(gp_Pnt(*center),gp_Dir(*axis)),theta)
     translation=gp_Trsf();translation.SetTranslation(gp_Vec(*(a['pitchDiameter']/2*(right*math.cos(theta)+up*math.sin(theta)))))
     tr=translation.Multiplied(rotation)
    else:tr.SetTranslation(gp_Vec(*(direction(a['direction'])*i*a['spacing'])))
    copies.append(BRepBuilderAPI_Transform(seed,tr,True).Shape())
   s=fuse(copies)
  elif name in ('fillet','chamfer'):
   target=shapes[op['target']];builder=(BRepFilletAPI_MakeFillet if name=='fillet' else BRepFilletAPI_MakeChamfer)(target)
   for sel in a['selectors']:
    near=pt(sel['near']);wanted=direction(sel['direction']);vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*near)).Vertex();candidates=[];ex=TopExp_Explorer(target,TopAbs_EDGE)
    while ex.More():
     edge=TopoDS.Edge_s(ex.Current());dist=BRepExtrema_DistShapeShape(vertex,edge);dist.Perform();curve=BRepAdaptor_Curve(edge)
     direction_kind=sel.get('directionKind','tangent')
     if direction_kind not in ('axis','tangent'):raise ValueError('Unknown selector directionKind')
     try:
      if direction_kind=='axis':
       kind=curve.GetType()
       if kind==GeomAbs_Circle:vec=curve.Circle().Axis().Direction()
       elif kind==GeomAbs_Ellipse:vec=curve.Ellipse().Axis().Direction()
       else:raise ValueError('Curve has no supported axis')
       candidate_direction=unit([vec.X(),vec.Y(),vec.Z()])
      else:
       try:parameter=dist.ParOnEdgeS2(1)[0]
       except Exception:
        parameter=min(np.linspace(curve.FirstParameter(),curve.LastParameter(),129),key=lambda t:curve.Value(float(t)).Distance(gp_Pnt(*near)))
       pnt=gp_Pnt();tangent=gp_Vec();curve.D1(float(parameter),pnt,tangent);candidate_direction=unit([tangent.X(),tangent.Y(),tangent.Z()])
      alignment=abs(np.dot(candidate_direction,wanted))
     except Exception:alignment=0
     if alignment>.9 and not any(edge.IsSame(existing) for _,existing in candidates):candidates.append((dist.Value(),edge))
     ex.Next()
    candidates.sort(key=lambda t:t[0])
    if not candidates or candidates[0][0]>1e-3:raise ValueError('No edge matches geometric selector '+id)
    if len(candidates)>1 and abs(candidates[1][0]-candidates[0][0])<1e-7:raise ValueError('Ambiguous edge selector '+id)
    builder.Add(a['size'],candidates[0][1])
   builder.Build()
   if not builder.IsDone():raise RuntimeError('Native edge modification failed '+id)
   s=builder.Shape()
  else:raise ValueError('Unsupported native operation '+name)
  if s.IsNull() or not BRepCheck_Analyzer(s).IsValid():raise RuntimeError('Invalid BRep '+id)
  shapes[id]=s;checks.append({'id':id,'op':name,'validBrep':True,'solidCount':count_solids(s),'volumeMm3':vol(s)})
 final=shapes[g['result']]
 if count_solids(final)!=1 or vol(final)<=0:raise RuntimeError('Final shape must be one positive-volume solid')
 return final,shapes,checks

def basis(view):
 n=unit(view['direction']);up=unit(np.array(view['up'])-n*np.dot(view['up'],n));return unit(np.cross(up,n)),up,n

def hlr(shape,view):
 right,up,n=basis(view);a=HLRBRep_Algo();a.Add(shape);a.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(*n),gp_Dir(*right))));a.Update();a.Hide();c=HLRBRep_HLRToShape(a)
 return [[(p.X(),p.Y()) for p in line] for shape in [c.VCompound(),c.Rg1LineVCompound()] for line in curves(shape)]

def section_lines(shape,spec,view):
 right,up,n=basis(view);lines=[];loops=[];b=box(shape);reach=np.linalg.norm(np.array(b[3:])-np.array(b[:3]))*3+10
 planes=[]
 if spec['kind']=='planar':planes=[(spec['cuttingPlanes'][0],None)]
 else:
  path=spec['worldPath'];sweep=unit(spec['sweepDirection'])
  for a,b in zip(path,path[1:]):
   a=np.array(a);b=np.array(b);delta=b-a
   # Connector planes are not displayed as separate section bands.
   normal=unit(np.cross(delta,sweep))
   if abs(np.dot(normal,n))<.99:continue
   along=unit(delta);planes.append(({'point':a.tolist(),'normal':normal.tolist()},(a,along,np.linalg.norm(delta))))
 for plane,band in planes:
  part=shape
  if band:
   a,along,length=band;localx=unit(np.cross(along,sweep));origin=a-localx*reach-sweep*reach
   clip=BRepPrimAPI_MakeBox(gp_Ax2(gp_Pnt(*origin),gp_Dir(*sweep),gp_Dir(*localx)),2*reach,length,2*reach).Shape()
   part=boolean(BRepAlgoAPI_Common,part,clip)
  op=BRepAlgoAPI_Section(part,gp_Pln(gp_Pnt(*plane['point']),gp_Dir(*plane['normal'])),False);op.Build()
  if not op.IsDone():raise RuntimeError('Section failed')
  for line in curves(op.Shape()):lines.append([(np.dot([p.X(),p.Y(),p.Z()],right),np.dot([p.X(),p.Y(),p.Z()],up)) for p in line])
  try:
   for _,line in closed_wires(op.Shape()):loops.append([(np.dot([p.X(),p.Y(),p.Z()],right),np.dot([p.X(),p.Y(),p.Z()],up)) for p in line])
  except RuntimeError:pass
 if not lines:raise RuntimeError('Empty section')
 return lines,loops

def clipped_lines(lines,roi):
 result=[]
 for line in lines:
  for a,b in zip(line,line[1:]):
   dx=b[0]-a[0];dy=b[1]-a[1];lo=0.;hi=1.;keep=True
   for p,q in [(-dx,a[0]-roi[0]),(dx,roi[2]-a[0]),(-dy,a[1]-roi[1]),(dy,roi[3]-a[1])]:
    if abs(p)<1e-12:
     if q<0:keep=False;break
    elif p<0:lo=max(lo,q/p)
    else:hi=min(hi,q/p)
   if keep and lo<=hi:result.append([(a[0]+lo*dx,a[1]+lo*dy),(a[0]+hi*dx,a[1]+hi*dy)])
 return result

def detail_region(recipe,shapes,detail,view):
 right,up,n=basis(view);ops={o['id']:o for o in recipe['geometry']['operations']};frames={f['id']:f for f in recipe['geometry']['frames']};projected=[]
 primary=[id for id in detail['features'] if ops[id]['op'] in ('cylinder','extrude','revolve','circularPattern','linearPattern')]
 for id in detail['features']:
  if primary and id not in primary:continue
  op=ops[id];a=op.get('args',{})
  if op['op'] in ('fillet','chamfer'):
   f=frames[op['frame']];x=np.array(f['xAxis']);z=np.array(f['zAxis']);rotation=np.column_stack([x,np.cross(z,x),z]);radius=max(a['size']*3,1.)
   centers=[np.array(f['origin'])+rotation@np.array(s['near']) for s in a['selectors']]
   boxes=[tuple(c-radius)+tuple(c+radius) for c in centers]
  else:boxes=[box(shapes[id])]
  for b in boxes:
   for x in (b[0],b[3]):
    for y in (b[1],b[4]):
     for z in (b[2],b[5]):projected.append((np.dot([x,y,z],right),np.dot([x,y,z],up)))
 xs=[p[0] for p in projected];ys=[p[1] for p in projected];w=max(xs)-min(xs);h=max(ys)-min(ys);pad=max(w,h)*.15+0.1
 return [min(xs)-pad,min(ys)-pad,max(xs)+pad,max(ys)+pad]

def text_value(d):
 v=f"{d['nominal']:g}".replace('.',',');m=d.get('sourceMeasurement',{});tol=m.get('tolerance');prefix='Ø' if d['type'] in ('diameter','pitchDiameter') else 'R' if d['type']=='radius' else ''
 if d.get('quantity',1)>1:prefix=f"{d['quantity']:g}×"+prefix
 if tol:
  u=tol['upperDeviationMm'];lo=tol['lowerDeviationMm'];fmt=lambda v:f'{v:g}'.replace('.',',')
  v+=f' (±{fmt(u)})' if abs(u+lo)<1e-9 else f' ({u:+g}/{lo:+g})'.replace('.',',')
 return prefix+v

def sheet(recipe,shape,shapes,out,source):
 S=2;im=Image.new('RGB',(1754*S,1240*S),'white');draw=ImageDraw.Draw(im);fontpath=os.getenv('ARIAL_FONT', '/workspace/fonts/arial/arial.ttf');font=lambda n:ImageFont.truetype(fontpath,int(n*S))
 def txt(x,y,s,size=16):draw.text((x*S,y*S),s,font=font(size),fill='black')
 draw.rectangle((20*S,20*S,1734*S,1220*S),outline='black',width=S)
 txt(45,35,recipe['outputId'],24);txt(1000,40,'OCCT — inceleme önizlemesi',17)
 views=recipe['drawing']['views'];sections=recipe['drawing']['sections'];sectionids={s['view'] for s in sections};front=next(v for v in views if v['id'] not in sectionids);iso=next((v for v in views if 'iso' in v['id'].lower()),views[-1]);sv=next(v for v in views if v['id']==sections[0]['view'])
 def panel(lines,rect,loops=None,trace=None):
  x,y,w,h=rect;points=[p for line in lines for p in line];xx=[p[0] for p in points];yy=[p[1] for p in points];cx=(min(xx)+max(xx))/2;cy=(min(yy)+max(yy))/2;k=min(w/(max(xx)-min(xx)+1e-5),h/(max(yy)-min(yy)+1e-5))
  def pix(p):return ((x+w/2+(p[0]-cx)*k)*S,(y+h/2-(p[1]-cy)*k)*S)
  if loops:
   mask=Image.new('1',im.size);md=ImageDraw.Draw(mask)
   # XOR gives holes even with nested section wires.
   from PIL import ImageChops
   for loop in loops:
    layer=Image.new('1',im.size);ImageDraw.Draw(layer).polygon([pix(p) for p in loop],fill=1);mask=ImageChops.logical_xor(mask,layer)
   hatch=Image.new('RGB',im.size,'white');hd=ImageDraw.Draw(hatch)
   for offset in range(-im.height,im.width,12*S):hd.line((offset,im.height,offset+im.height,0),fill='#777777',width=1)
   region=Image.new('1',im.size);ImageDraw.Draw(region).rectangle((int(x*S),int(y*S),int((x+w)*S),int((y+h)*S)),fill=1)
   mask=ImageChops.logical_and(mask,region);im.paste(hatch,(0,0),mask)
  for line in lines:
   if len(line)>1:draw.line([pix(p) for p in line],fill='black',width=2,joint='curve')
  if trace:
   from PIL import ImageChops
   overlay=Image.new('RGB',im.size,'white');od=ImageDraw.Draw(overlay)
   for a,b in zip(trace,trace[1:]):od.line((pix(a),pix(b)),fill='#444444',width=S)
   bounds=(int((x-20)*S),int((y-20)*S),int((x+w+20)*S),int((y+h+20)*S))
   im.paste(ImageChops.darker(im.crop(bounds),overlay.crop(bounds)),bounds[:2])
  return pix
 right,up,n=basis(front)
 trace=None
 sec=sections[0]
 if sec.get('worldPath'):trace=[(np.dot(p,right),np.dot(p,up)) for p in sec['worldPath']]
 details=recipe['drawing'].get('details',[])
 frontHeight=720
 for detail in details:
  bx,by,bw,bh=detail['sheetBox']
  if bx*1754<980 and (bx+bw)*1754>100 and by*1240>180:frontHeight=min(frontHeight,by*1240-175)
 pix=panel(hlr(shape,front),(100,130,880,max(frontHeight,120)),trace=trace)
 txt(370,150+max(frontHeight,120),'Ana görünüş',16)
 sl,loops=section_lines(shape,sec,sv);panel(sl,(1110,140,470,380),loops);txt(1220,540,'Kesit '+sec['id'],16)
 temp=out/'mesh.stl';BRepMesh_IncrementalMesh(shape,.08,False,.3,True).Perform();writer=StlAPI_Writer();writer.Write(shape,str(temp));render_mesh(temp,out,{'camera':iso})
 with Image.open(out/'occt-preview.png') as sourceImage:image=sourceImage.convert('RGB')
 image.thumbnail((570*S,340*S));im.paste(image,(int(1100*S+(570*S-image.width)/2),int(590*S+(340*S-image.height)/2)))
 detailReports=[]
 for detail in details:
  sourceView=next(v for v in views if v['id']==detail['sourceView']);section=next((s for s in sections if s['view']==sourceView['id']),None)
  if section:sourceLines,sourceLoops=section_lines(shape,section,sourceView)
  else:sourceLines=hlr(shape,sourceView);sourceLoops=[]
  roi=detail_region(recipe,shapes,detail,sourceView);lines=clipped_lines(sourceLines,roi)
  if not lines:raise ValueError('Detail region contains no geometry: '+detail['id'])
  x,y,w,h=detail['sheetBox'];rect=(x*1754,y*1240,w*1754,h*1240)
  panel(lines,rect,sourceLoops);txt(rect[0],rect[1]+rect[3]+6,'DETAY '+detail.get('label',detail['id']),15)
  detailReports.append({'id':detail['id'],'sourceView':detail['sourceView'],'features':detail['features'],'sheetBox':detail['sheetBox'],'roiMm':roi})
 # Values are taken from the resolved drawing layer, never from geometry deviations.
 visible=[d for d in recipe['drawing']['dimensions'] if d['effectiveVisible']]
 y=max([980]+[(d['sheetBox'][1]+d['sheetBox'][3])*1240+36 for d in details]);txt(45,y,'Ölçüler / toleranslar (mm)',16)
 tight=y>1030
 if tight:y=min(y,1108)
 columns=max(4,math.ceil(len(visible)/2)) if tight else 4
 if columns>6:raise ValueError('Too many dimensions for preview table with detail region')
 rowHeight=28 if tight else 40
 for i,d in enumerate(visible):
  col=i%columns;row=i//columns;label=d.get('valueSource',{}).get('column',d['id']);txt(45+col*(1664/columns),y+28+row*rowHeight,label+': '+text_value(d),15 if tight else 17)
 for i,tol in enumerate(recipe['drawing'].get('geometricTolerances',[])):txt(45+i*400,1125,tol['kind']+': '+f"{tol['value']:g}".replace('.',','),16)
 txt(45,1200 if tight else 1170,'Model verisinden üretildi • Görsel kontrol gerektirir',12 if tight else 15)
 with Image.open(source) as inputImage:dpi=inputImage.info.get('dpi',(300,300))
 im.resize((1754,1240),Image.Resampling.LANCZOS).save(out/(recipe['outputId']+'.jpeg'),quality=95,dpi=dpi)
 return {'details':detailReports,'annotationMode':'resolved-dimension-table','limits':['Template title block/layout not reconstructed','Dimensions shown in table, not yet associated leader placement','Section connectors omitted; band outlines may retain seam edges','Geometric tolerance leader placement and section rear-edge visibility pending'],'visibleDimensions':[d['id'] for d in visible]}

def run(folder,source):
 folder=pathlib.Path(folder);results=[]
 for file in sorted(folder.glob('*.resolved.json')):
  recipe=json.loads(file.read_text());out=folder/recipe['outputId'];out.mkdir(exist_ok=True)
  try:
   shape,shapes,checks=build(recipe);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs)
   if w.Write(str(out/(recipe['outputId']+'.step')))!=IFSelect_RetDone:raise RuntimeError('STEP write failed')
   reread=STEPControl_Reader();reread.ReadFile(str(out/(recipe['outputId']+'.step')));reread.TransferRoots();restored=reread.OneShape()
   if not BRepCheck_Analyzer(restored).IsValid() or not math.isclose(vol(restored),vol(shape),rel_tol=1e-6):raise RuntimeError('STEP roundtrip mismatch')
   drafting=sheet(recipe,shape,shapes,out,source)
   results.append({'outputId':recipe['outputId'],'status':'preview-produced','checks':checks,'volumeMm3':vol(shape),'stepRoundtrip':True,'drafting':drafting})
  except Exception as ex:results.append({'outputId':recipe['outputId'],'status':'failed','error':str(ex)});traceback.print_exc()
 (folder/'native-results.json').write_text(json.dumps({'apiCalls':0,'results':results},indent=2));print(json.dumps(results,indent=2));return all(r['status']=='preview-produced' for r in results)
if __name__=='__main__':sys.exit(0 if run(sys.argv[1],sys.argv[2]) else 1)
