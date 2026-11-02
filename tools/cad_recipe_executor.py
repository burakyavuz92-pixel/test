"""Local resolved-v7 OCCT executor. No API calls or product-family geometry rules."""
from local_drawing import resolve_local_sections
from fixed_template import background,fill_fields
from dimension_annotations import resolve_anchors,render_dimensions,render_template_dimensions
from template_layout import prepare as prepare_layout,bind_dimensions
from drafting_style import PAPER_MM,PIXELS,DPI,PX_PER_MM,choose_scale,scale_label,patterned_line
from face_edge_selector import select_edge
import json,math,sys,pathlib,os,traceback
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from OCP.gp import gp_Pnt,gp_Vec,gp_Dir,gp_Ax1,gp_Ax2,gp_Trsf,gp_Pln
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform,BRepBuilderAPI_MakeVertex
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakePrism,BRepPrimAPI_MakeRevol,BRepPrimAPI_MakeBox,BRepPrimAPI_MakeHalfSpace
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
    if 'faces' in sel:
     builder.Add(a['size'],select_edge(target,sel['faces']));continue
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

def hlr(shape,view,include_outlines=False):
 right,up,n=basis(view);a=HLRBRep_Algo();a.Add(shape);a.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(),gp_Dir(*n),gp_Dir(*right))));a.Update();a.Hide();c=HLRBRep_HLRToShape(a)
 compounds=[c.VCompound(),c.Rg1LineVCompound()]
 if include_outlines:compounds.append(c.OutLineVCompound())
 return [[(p.X(),p.Y()) for p in line] for shape in compounds for line in curves(shape)]

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
  # Retain the material behind the cutting plane and project its visible edges.
  # This supplies real hole-wall boundaries across the material thickness.
  plane_point=np.array(plane['point'],dtype=float)
  face=BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(*plane_point),gp_Dir(*plane['normal']))).Face()
  behind=plane_point-n*reach
  halfspace=BRepPrimAPI_MakeHalfSpace(face,gp_Pnt(*behind)).Solid()
  retained=boolean(BRepAlgoAPI_Common,part,halfspace)
  if not retained.IsNull():lines.extend(hlr(retained,view,include_outlines=True))
  try:
   for _,line in closed_wires(op.Shape()):loops.append([(np.dot([p.X(),p.Y(),p.Z()],right),np.dot([p.X(),p.Y(),p.Z()],up)) for p in line])
  except RuntimeError:pass
 if not lines:raise RuntimeError('Empty section')
 return lines,loops

def text_value(d):
 callout=d.get('sourceMeasurement',{}).get('threadCallout')
 if callout:return (f"{d.get('quantity',1):g}×" if d.get('quantity',1)>1 else '')+callout
 v=f"{d['nominal']:g}".replace('.',',');m=d.get('sourceMeasurement',{});tol=m.get('tolerance');prefix='Ø' if d['type'] in ('diameter','pitchDiameter') else 'R' if d['type']=='radius' else ''
 if d.get('quantity',1)>1:prefix=f"{d['quantity']:g}×"+prefix
 if tol:
  u=tol['upperDeviationMm'];lo=tol['lowerDeviationMm'];fmt=lambda v:f'{v:g}'.replace('.',',')
  v+=f' (±{fmt(u)})' if abs(u+lo)<1e-9 else f' ({u:+g}/{lo:+g})'.replace('.',',')
 return prefix+v

def sheet(recipe,shape,shapes,out,source):
 S=2;im=Image.new('RGB',(PIXELS[0]*S,PIXELS[1]*S),'white');draw=ImageDraw.Draw(im);fontpath=os.getenv('ARIAL_FONT', '/workspace/fonts/arial/arial.ttf');font=lambda n:ImageFont.truetype(fontpath,int(n*S))
 template=background(source,im.size)
 if template is not None:im=template;draw=ImageDraw.Draw(im)
 def txt(x,y,s,size=16):draw.text((x*S,y*S),s,font=font(size),fill='black')
 if template is None:
  draw.rectangle((20*S,20*S,1734*S,1220*S),outline='black',width=S)
  txt(45,35,recipe['outputId'],24)
 views=recipe['drawing']['views'];sections=recipe['drawing']['sections'];sectionids={s['view'] for s in sections};front=next(v for v in views if v['id'] not in sectionids);iso=next((v for v in views if 'iso' in v['id'].lower()),views[-1]);sv=next(v for v in views if v['id']==sections[0]['view'])
 def panel(lines,rect,loops=None,trace=None,fixed_k=None,centers=None):
  x,y,w,h=rect;points=[p for line in lines for p in line];xx=[p[0] for p in points];yy=[p[1] for p in points];cx=(min(xx)+max(xx))/2;cy=(min(yy)+max(yy))/2;k=min(w/(max(xx)-min(xx)+1e-5),h/(max(yy)-min(yy)+1e-5))
  if fixed_k is not None:k=fixed_k
  def pix(p):return ((x+w/2+(p[0]-cx)*k)*S,(y+h/2-(p[1]-cy)*k)*S)
  if loops:
   mask=Image.new('1',im.size);md=ImageDraw.Draw(mask)
   # XOR gives holes even with nested section wires.
   from PIL import ImageChops
   for loop in loops:
    layer=Image.new('1',im.size);ImageDraw.Draw(layer).polygon([pix(p) for p in loop],fill=1);mask=ImageChops.logical_xor(mask,layer)
   hatch=Image.new('RGB',im.size,'white');hd=ImageDraw.Draw(hatch)
   for offset in range(-im.height,im.width,max(1,round(2*PX_PER_MM))*S):hd.line((offset,im.height,offset+im.height,0),fill='black',width=max(1,round(.13*PX_PER_MM*S)))
   region=Image.new('1',im.size);ImageDraw.Draw(region).rectangle((int(x*S),int(y*S),int((x+w)*S),int((y+h)*S)),fill=1)
   mask=ImageChops.logical_and(mask,region);im.paste(hatch,(0,0),mask)
  for line in lines:
   if len(line)>1:draw.line([pix(p) for p in line],fill='black',width=max(1,round(.25*PX_PER_MM*S)),joint='curve')
  if centers:
   for center,radius in centers:
    reach=radius+2.5*PX_PER_MM/k
    for delta in [(reach,0),(0,reach)]:
     a=pix((center[0]-delta[0],center[1]-delta[1]));b=pix((center[0]+delta[0],center[1]+delta[1]))
     patterned_line(draw,a,b,max(1,round(.13*PX_PER_MM*S)),[10*S,3*S,1*S,3*S])
  if trace:
   for a,b in zip(trace,trace[1:]):patterned_line(draw,pix(a),pix(b),max(1,round(.35*PX_PER_MM*S)),[16*S,4*S,2*S,4*S])
  return pix
 right,up,n=basis(front)
 trace=None
 sec=sections[0]
 if sec.get('worldPath'):trace=[(np.dot(p,right),np.dot(p,up)) for p in sec['worldPath']]
 front_lines=hlr(shape,front);sl,loops=section_lines(shape,sec,sv)
 panels=[(330,120,850,690),(130 if recipe['drawing'].get('templateLayout') else 55,120,240,690)]
 def extent(lines):
  pts=[p for line in lines for p in line]
  return max(p[0] for p in pts)-min(p[0] for p in pts),max(p[1] for p in pts)-min(p[1] for p in pts)
 scale=choose_scale([extent(front_lines),extent(sl)],panels);fixed_k=scale*PX_PER_MM
 centers={};ex=TopExp_Explorer(shape,TopAbs_EDGE)
 while ex.More():
  curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
  if curve.GetType()==GeomAbs_Circle:
   circle=curve.Circle();axis=circle.Axis().Direction()
   if abs(np.dot([axis.X(),axis.Y(),axis.Z()],n))>.999999:
    p=circle.Location();xyz=[p.X(),p.Y(),p.Z()];xy=(float(np.dot(xyz,right)),float(np.dot(xyz,up)));key=tuple(round(v,5) for v in xy)
    centers[key]=max(centers.get(key,0),circle.Radius())
  ex.Next()
 pix=panel(front_lines,panels[0],trace=trace,fixed_k=fixed_k,centers=list(centers.items()))
 txt(650,835,'Ana görünüş',14)
 section_pix=panel(sl,panels[1],loops,fixed_k=fixed_k);txt(65,835,'KESİT '+sec['id'],14)
 if template is not None:fill_fields(im,{'scale':scale_label(scale),'product':recipe['outputId'],'format':'A5'},fontpath)
 temp=out/'mesh.stl';BRepMesh_IncrementalMesh(shape,.08,False,.3,True).Perform();writer=StlAPI_Writer();writer.Write(shape,str(temp));render_mesh(temp,out,{'camera':iso})
 with Image.open(out/'occt-preview.png') as sourceImage:image=sourceImage.convert('RGB')
 image.thumbnail((450*S,360*S));im.paste(image,(int(1260*S+(450*S-image.width)/2),int(150*S+(360*S-image.height)/2)))
 txt(1300,530,'İzometrik: ölçek dışı',14)
 # Values are taken from the resolved drawing layer, never from geometry deviations.
 annotation_bounds=Bnd_Box();BRepBndLib.AddOptimal_s(shape,annotation_bounds,False,False)
 layout=recipe['drawing'].get('templateLayout')
 if layout:
  bindings,excluded,binding_errors=bind_dimensions(recipe['drawing']['dimensions'],layout)
  subset=json.loads(json.dumps(recipe));subset['drawing']['dimensions']=[b['dimension'] for b in bindings]
  anchors,unresolved,omitted=resolve_anchors(subset,shape,basis(front),basis(sv),annotation_bounds.Get(),bindings)
  def bounds2(lines):
   pts=[p for line in lines for p in line];return [min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
  placement=render_template_dimensions(im,font,S,anchors,pix,section_pix,layout,{'front':bounds2(front_lines),'section':bounds2(sl)},text_value)
  unresolved+=binding_errors;omitted+=excluded
 else:
  anchors,unresolved,omitted=resolve_anchors(recipe,shape,basis(front),basis(sv),annotation_bounds.Get())
  placement=render_dimensions(im,font,S,anchors,pix,section_pix,text_value)
 unresolved+=placement['failed']
 visible=[u['dimension'] for u in unresolved]
 (out/'dimension-placement.json').write_text(json.dumps({'placed':placement['placed'],'templatePlacements':placement.get('templatePlacements',[]),'unresolved':[{'id':u['id'],'reason':u['reason']} for u in unresolved],'omitted':omitted},indent=2))
 y=900
 if visible:txt(45,y,'Bağlantısı çözülemeyen ölçüler (mm) — kontrol gerekli',13)
 tight=y>1030
 if tight:y=min(y,1108)
 columns=max(4,math.ceil(len(visible)/2)) if tight else 4
 if columns>6:raise ValueError('Too many dimensions for preview table')
 rowHeight=28 if tight else 32
 for i,d in enumerate(visible):
  col=i%columns;row=i//columns;label=d.get('valueSource',{}).get('column',d['id']);txt(45+col*(1140/columns),y+28+row*rowHeight,label+': '+text_value(d),12 if tight else 13)
 for i,tol in enumerate(recipe['drawing'].get('geometricTolerances',[])):txt(45+i*300,1065,tol['kind']+': '+f"{tol['value']:g}".replace('.',','),16)
 txt(45,1080,'İnceleme çıktısı • Geometri ve ölçüler kontrol edilmelidir',11)
 im.resize(PIXELS,Image.Resampling.LANCZOS).save(out/(recipe['outputId']+'.jpeg'),quality=95,dpi=(DPI,DPI))
 # A5 PDF provides an exact physical page independently of JPEG viewer DPI rounding.
 im.resize(PIXELS,Image.Resampling.LANCZOS).save(out/(recipe['outputId']+'.pdf'),resolution=DPI)
 return {'templateTitleBlock':template is not None,'paperMm':list(PAPER_MM),'imagePixels':list(PIXELS),'dpi':DPI,'drawingScale':scale,'scaleLabel':scale_label(scale),'centerlineCenters':len(centers),'annotationMode':'geometry-linked-dimensions','placedDimensions':placement['placed'],'unresolvedDimensions':[{'id':u['id'],'reason':u['reason']} for u in unresolved],'limits':['Unresolved dimensions remain in a separate table','Section jog connectors omitted; retained-material edges projected; band outlines may retain seam edges','Geometric tolerance leader placement pending'],'visibleDimensions':[d['id'] for d in recipe['drawing']['dimensions'] if d['effectiveVisible'] and d['nominal']!=0]}

def run(folder,source,excel=None):
 folder=pathlib.Path(folder);results=[]
 layout=prepare_layout(source,excel,folder) if excel else None
 for file in sorted(folder.glob('*.resolved.json')):
  recipe=json.loads(file.read_text())
  if layout is not None:recipe['drawing']['templateLayout']=layout
  out=folder/recipe['outputId'];out.mkdir(exist_ok=True)
  try:
   shape,shapes,checks=build(recipe);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs)
   if w.Write(str(out/(recipe['outputId']+'.step')))!=IFSelect_RetDone:raise RuntimeError('STEP write failed')
   reread=STEPControl_Reader();reread.ReadFile(str(out/(recipe['outputId']+'.step')));reread.TransferRoots();restored=reread.OneShape()
   if not BRepCheck_Analyzer(restored).IsValid() or not math.isclose(vol(restored),vol(shape),rel_tol=1e-6):raise RuntimeError('STEP roundtrip mismatch')
   recipe['drawing']=resolve_local_sections(recipe['drawing'],box(shape))
   (out/'native-drawing.json').write_text(json.dumps(recipe['drawing'],indent=2))
   drafting=sheet(recipe,shape,shapes,out,source)
   results.append({'outputId':recipe['outputId'],'status':'preview-produced','checks':checks,'volumeMm3':vol(shape),'stepRoundtrip':True,'drafting':drafting})
  except Exception as ex:results.append({'outputId':recipe['outputId'],'status':'failed','error':str(ex)});traceback.print_exc()
 (folder/'native-results.json').write_text(json.dumps({'apiCalls':0,'results':results},indent=2));print(json.dumps(results,indent=2));return all(r['status']=='preview-produced' for r in results)
if __name__=='__main__':sys.exit(0 if run(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None) else 1)
