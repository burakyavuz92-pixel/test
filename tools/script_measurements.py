"""Validate generic model measurement references against the final BRep."""
import math
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Torus,GeomAbs_Circle

def vector(x):
 a=np.asarray(x,dtype=float)
 if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('Reference must be a finite 3D vector')
 return a

def unit(x):
 a=vector(x)
 if abs(np.linalg.norm(a)-1)>1e-6:raise ValueError('Reference direction must be unit length')
 return a

def on_body(shape,p):
 d=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*vector(p))).Vertex(),shape);d.Perform()
 if not d.IsDone() or d.Value()>1e-4:raise ValueError('Measurement endpoint is not on final body')

def cylinders_at_axis(shape,p):
 result=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  s=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
  if s.GetType()==GeomAbs_Cylinder:
   c=s.Cylinder();o=c.Location();v=c.Axis().Direction();axis=np.array([v.X(),v.Y(),v.Z()]);origin=np.array([o.X(),o.Y(),o.Z()])
   if np.linalg.norm(np.cross(p-origin,axis))<1e-5:result.append(axis)
  ex.Next()
 return result

def section_meridian(shape,m,section):
 # Select an equivalent meridian only on a verified analytic torus/cylinder.
 m=dict(m);kind=m['kind'];up=np.array(section[1],dtype=float)
 if kind=='radius':
  center=vector(m['center']);point=vector(m['point']);ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():
   s=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
   if s.GetType()==GeomAbs_Torus:
    t=s.Torus();o=t.Location();a=t.Axis().Direction();axis=np.array([a.X(),a.Y(),a.Z()]);origin=np.array([o.X(),o.Y(),o.Z()]);radial=center-origin
    if abs(t.MinorRadius()-m['radius'])<1e-5 and abs(np.linalg.norm(radial)-t.MajorRadius())<1e-5 and abs(np.dot(radial,axis))<1e-5:
     evidence=m.get('visualEvidence',{});tips=evidence.get('arrowTipsNormalized') or [];middle=evidence.get('viewCenterNormalized',[.5,.5]);sign=-1 if tips and tips[0] is not None and tips[0][1]>middle[1] else 1
     target=up-axis*np.dot(up,axis)
     if np.linalg.norm(target)<1e-7:break
     target=sign*target/np.linalg.norm(target);old=radial/np.linalg.norm(radial);delta=point-center
     m['center']=(origin+target*t.MajorRadius()).tolist();m['point']=(origin+target*(t.MajorRadius()+np.dot(delta,old))+axis*np.dot(delta,axis)).tolist();m['axis']=np.cross(axis,target).tolist();return m
   ex.Next()
 if kind=='thickness':
  a,b=map(vector,m['points']);ex=TopExp_Explorer(shape,TopAbs_FACE);supports=[]
  while ex.More():
   s=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
   if s.GetType()==GeomAbs_Cylinder:
    c=s.Cylinder();o=c.Location();d=c.Axis().Direction();axis=np.array([d.X(),d.Y(),d.Z()]);origin=np.array([o.X(),o.Y(),o.Z()]);supports.append((axis,origin,c.Radius()))
   ex.Next()
  for axis,origin,r in supports:
   ac=origin+axis*np.dot(a-origin,axis);bc=origin+axis*np.dot(b-origin,axis);ra=np.linalg.norm(a-ac);rb=np.linalg.norm(b-bc)
   if np.linalg.norm(ac-bc)<1e-5 and abs(ra-r)<1e-5 and any(abs(rr-rb)<1e-5 and np.linalg.norm(np.cross(oo-origin,axis))<1e-5 for ax,oo,rr in supports):
    v=up-axis*np.dot(up,axis)
    if np.linalg.norm(v)>1e-7:
     v/=np.linalg.norm(v);m['points']=[(ac+v*ra).tolist(),(bc+v*rb).tolist()];m['direction']=(v*(1 if rb>ra else -1)).tolist();return m
 return m

def anchor(shape,m,nominal,front,section,view=None):
 if m.get('unresolved'):raise ValueError(m['unresolved'])
 if not math.isfinite(m['nominal']) or abs(m['nominal']-nominal)>1e-5:raise ValueError('Measurement source/nominal mismatch')
 if view=='section':m=section_meridian(shape,m,section)
 kind=m['kind'];dest=section if view=='section' or kind in ('distance','thickness','radius') and view is None else front
 project=lambda p:np.array([np.dot(p,dest[0]),np.dot(p,dest[1])])
 if kind in ('distance','thickness'):
  a,b=map(vector,m['points']);direction=unit(m['direction'])
  try:on_body(shape,a);on_body(shape,b)
  except ValueError:
   aa=cylinders_at_axis(shape,a);bb=cylinders_at_axis(shape,b)
   if kind!='distance' or not any(abs(abs(np.dot(x,y))-1)<1e-6 and abs(np.dot(direction,x))<1e-6 for x in aa for y in bb):raise
  evidence=m.get('visualEvidence')
  if evidence is not None:
   tips=evidence.get('arrowTipsNormalized')
   if not tips or len(tips)!=2 or any(t is None for t in tips):raise ValueError('Missing visual endpoints for linear measurement')
   visual=np.array(tips[1],dtype=float)-np.array(tips[0],dtype=float);visual[1]*=-1
   predicted=np.array([np.dot(direction,dest[0]),np.dot(direction,dest[1])])
   if np.linalg.norm(visual)<1e-6 or np.linalg.norm(predicted)<1e-6:raise ValueError('Degenerate visual measurement direction')
   # Orthogonal image axes are checked categorically; do not measure mm from schematic pixels.
   if abs(np.dot(visual/np.linalg.norm(visual),predicted/np.linalg.norm(predicted)))<0.9:raise ValueError('Visual arrow direction conflicts with geometric measurement direction')

  if abs(abs(np.dot(b-a,direction))-nominal)>1e-5:raise ValueError('Measured boundary separation differs from nominal')
  # Offset endpoints can be projected onto the measurement axis for drawing.
  b=a+direction*np.dot(b-a,direction);pa,pb=project(a),project(b)
  if abs(np.linalg.norm(pb-pa)-nominal)>1e-5:raise ValueError('Measurement hidden in selected view')
  return dict(view='section' if dest is section else 'front',kind='linear',points=[pa.tolist(),pb.tolist()],axis='X' if abs(pb[0]-pa[0])>abs(pb[1]-pa[1]) else 'Y')
 center=vector(m['center']);axis=unit(m['axis']);radius=float(m['radius'])
 if radius<=0 or not math.isfinite(radius):raise ValueError('Positive finite radius required')
 if kind=='radius':
  p=vector(m['point']);on_body(shape,p)
  if abs(np.linalg.norm(p-center)-radius)>1e-5 or abs(np.dot(p-center,axis))>1e-5 or abs(radius-nominal)>1e-5:raise ValueError('Invalid circular radius reference')
  curved=False;ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():
   surface=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
   if surface.GetType()==GeomAbs_Torus:
    t=surface.Torus();o=t.Location();d=t.Axis().Direction();n=np.array([d.X(),d.Y(),d.Z()]);delta=center-np.array([o.X(),o.Y(),o.Z()])
    if abs(t.MinorRadius()-radius)<1e-5 and abs(np.linalg.norm(delta)-t.MajorRadius())<1e-5 and abs(np.dot(delta,n))<1e-5 and abs(np.dot(axis,n))<1e-5 and abs(np.dot(axis,delta))<1e-5:curved=True
   ex.Next()
  ex=TopExp_Explorer(shape,TopAbs_EDGE)
  while ex.More():
   c=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
   if c.GetType()==GeomAbs_Circle:
    circle=c.Circle();o=circle.Location();d=circle.Axis().Direction()
    if abs(circle.Radius()-radius)<1e-5 and np.linalg.norm(center-[o.X(),o.Y(),o.Z()])<1e-5 and abs(abs(np.dot(axis,[d.X(),d.Y(),d.Z()]))-1)<1e-5:curved=True
   ex.Next()
  if not curved:raise ValueError('Radius reference does not match an actual circular edge or torus arc')
  # A supplied circular arc must exist: nearby angular samples also lie on the body.
  radial=(p-center)/radius;tangent=np.cross(axis,radial)
  for t in (-0.05,0.05):on_body(shape,center+radius*(radial*math.cos(t)+tangent*math.sin(t)))
  return dict(view='section' if dest is section else 'front',kind='leader',anchor=project(p).tolist(),anchorOptions=[project(p).tolist()])
 if kind!='diameter' or abs(2*radius-nominal)>1e-5:raise ValueError('Invalid diameter reference')
 found=False;ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  s=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
  if s.GetType()==GeomAbs_Cylinder:
   c=s.Cylinder();o=c.Location();d=c.Axis().Direction()
   if abs(c.Radius()-radius)<1e-5 and abs(abs(np.dot(axis,[d.X(),d.Y(),d.Z()]))-1)<1e-6 and np.linalg.norm(np.cross(np.array([o.X(),o.Y(),o.Z()])-center,axis))<1e-5:found=True
  ex.Next()
 if not found:raise ValueError('No matching cylindrical support on final body')
 if abs(abs(np.dot(axis,dest[2]))-1)<1e-6:return dict(view='section' if dest is section else 'front',kind='circle',center=project(center).tolist(),radius=radius)
 radial=project(axis);perp=np.array([-radial[1],radial[0]])
 if np.linalg.norm(perp)<1e-7:raise ValueError('Unsupported projected diameter')
 return dict(view='section' if dest is section else 'front',kind='sectionDiameter',centerOptions=[project(center).tolist()],radius=radius,radialDirection=perp/np.linalg.norm(perp))
