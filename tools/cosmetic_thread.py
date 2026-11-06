"""Section-only symbolic marking of an explicitly named cylindrical STEP face."""
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Line
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section,BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Pnt,gp_Dir,gp_Pln,gp_Ax2
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from drafting_style import patterned_line,PX_PER_MM

def segments(face,section,view_basis):
 if face is None:return []
 surface=BRepAdaptor_Surface(TopoDS.Face_s(face))
 if surface.GetType()!=GeomAbs_Cylinder:raise ValueError('dis tag must select a cylindrical face')
 cylinder=surface.Cylinder();d=cylinder.Axis().Direction();axis=np.array([d.X(),d.Y(),d.Z()]);o=cylinder.Location();origin=np.array([o.X(),o.Y(),o.Z()]);right,up,normal=view_basis
 unit=lambda v:np.asarray(v,dtype=float)/np.linalg.norm(v)
 planes=[]
 if section['kind']=='planar':planes=[(section['cuttingPlanes'][0],None)]
 else:
  sweep=unit(section['sweepDirection'])
  for a,b in zip(section['worldPath'],section['worldPath'][1:]):
   a=np.array(a);delta=np.array(b)-a;n=unit(np.cross(delta,sweep))
   if abs(np.dot(n,normal))>.99:planes.append(({'point':a,'normal':n},(a,unit(delta),np.linalg.norm(delta),sweep)))
 bounds=Bnd_Box();BRepBndLib.AddOptimal_s(face,bounds,False,False);bb=bounds.Get();reach=np.linalg.norm(np.array(bb[3:])-np.array(bb[:3]))*3+10
 result=[];groups={}
 for plane,band in planes:
  n=unit(plane['normal'])
  if abs(np.dot(n,axis))>1e-6:continue # longitudinal section notation only
  part=face
  if band:
   a,along,length,sweep=band;localx=unit(np.cross(along,sweep));corner=a-localx*reach-sweep*reach
   clip=BRepPrimAPI_MakeBox(gp_Ax2(gp_Pnt(*corner),gp_Dir(*sweep),gp_Dir(*localx)),2*reach,length,2*reach).Shape();op=BRepAlgoAPI_Common(part,clip);op.Build();part=op.Shape()
  cut=BRepAlgoAPI_Section(part,gp_Pln(gp_Pnt(*plane['point']),gp_Dir(*n)),False);cut.Build()
  ex=TopExp_Explorer(cut.Shape(),TopAbs_EDGE)
  while ex.More():
   curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
   if curve.GetType()==GeomAbs_Line:
    points=[curve.Value(t) for t in [curve.FirstParameter(),curve.LastParameter()]];xyz=sorted([np.array([p.X(),p.Y(),p.Z()]) for p in points],key=lambda p:np.dot(p-origin,axis))
    key=tuple(round(float(np.dot(p-origin,axis)),5) for p in xyz);groups.setdefault(key,[]).append(xyz)
   ex.Next()
 project=lambda p:np.array([np.dot(p,right),np.dot(p,up)])
 for pair in groups.values():
  if len(pair)!=2:continue
  a,b=pair[0];c,d=pair[1]
  if np.linalg.norm(a-c)<1e-5:continue
  # Symbolic inset is a fraction of the intersected width, not a thread dimension.
  inset=(c-a)*.04
  result.append({'inner':[[project(a+inset),project(b+inset)],[project(c-inset),project(d-inset)]],'ends':[[project(a),project(c)],[project(b),project(d)]]})
 return result

def draw_marking(draw,groups,pix,S):
 for group in groups:
  for a,b in group['inner']:draw.line([pix(a),pix(b)],fill='black',width=max(1,round(.13*PX_PER_MM*S)))
  for a,b in group['ends']:patterned_line(draw,pix(a),pix(b),max(1,round(.13*PX_PER_MM*S)),[5*S,3*S])
 return {'tag':'dis','sectionRegions':len(groups),'parallelLines':2*len(groups),'dashedEnds':2*len(groups)}
