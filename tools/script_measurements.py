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
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Torus,GeomAbs_Circle,GeomAbs_Cone,GeomAbs_Plane

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
 if 'points' not in m and 'p1' in m and 'p2' in m:m=dict(m,points=[m['p1'],m['p2']])
 if m.get('unresolved'):raise ValueError(m['unresolved'])
 if not math.isfinite(m['nominal']) or abs(m['nominal']-nominal)>1e-5:raise ValueError('Measurement source/nominal mismatch')
 if view=='section':m=section_meridian(shape,m,section)
 kind=m['kind'];dest=section if view=='section' or kind in ('distance','thickness','radius') and view is None else front
 project=lambda p:np.array([np.dot(p,dest[0]),np.dot(p,dest[1])])
 if kind=='chamfer':
  a,b=map(vector,m['points']);direction=unit(m['direction']);delta=b-a
  leg=abs(np.dot(delta,direction));other=np.linalg.norm(delta-direction*np.dot(delta,direction))
  angle=float(m['angleDeg'])
  if not 0<angle<90 or abs(leg-nominal)>1e-5 or abs(math.degrees(math.atan2(other,leg))-angle)>1e-4:raise ValueError('Chamfer leg or angle differs from specified value')
  on_body(shape,a);on_body(shape,b)
  support=False;cone=None;ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():
   face=TopoDS.Face_s(ex.Current());surface=BRepAdaptor_Surface(face)
   if surface.GetType() in (GeomAbs_Cone,GeomAbs_Plane):
    try:
     for t in (0,.25,.5,.75,1):on_body(face,a+t*delta)
     # Both ends must terminate on boundaries of this same chamfer face.
     for point in (a,b):
      edges=TopExp_Explorer(face,TopAbs_EDGE);hit=False
      while edges.More():
       try:on_body(edges.Current(),point);hit=True;break
       except ValueError:edges.Next()
      if not hit:raise ValueError('Chamfer endpoint is not on supporting face boundary')
     support=True
     if surface.GetType()==GeomAbs_Cone:cone=surface.Cone()
     break
    except ValueError:pass
   ex.Next()
  if not support:raise ValueError('No single chamfer face supports the given endpoints')
  evidence=m.get('visualEvidence')
  if evidence is not None and not any(t is not None for t in evidence.get('arrowTipsNormalized',[])):raise ValueError('Chamfer leader requires a visual arrow')
  if cone is not None and dest is section:
   axis0=cone.Axis().Direction();axis0=np.array([axis0.X(),axis0.Y(),axis0.Z()]);origin=cone.Location();origin=np.array([origin.X(),origin.Y(),origin.Z()])
   target=dest[1]-axis0*np.dot(dest[1],axis0)
   if np.linalg.norm(target)<1e-7:raise ValueError('Chamfer section meridian unavailable')
   target/=np.linalg.norm(target)
   if evidence:
    tips=[t for t in evidence.get('arrowTipsNormalized',[]) if t is not None];middle=evidence.get('viewCenterNormalized',[.5,.5]);source_axis=np.array(evidence.get('sectionAxisNormalized',[0,-1]),dtype=float);source_axis[1]*=-1
    radial=np.array([-source_axis[1],source_axis[0]]);visual=np.array(tips[0])-middle;visual[1]*=-1
    if np.dot(visual,radial)<0:target=-target
   def meridian(point):
    delta=point-origin;axial=origin+axis0*np.dot(delta,axis0);return axial+target*np.linalg.norm(point-axial)
   a,b=meridian(a),meridian(b)
   for point in (a,b,(a+b)/2):on_body(face,point)
  tip=(a+b)/2
  return dict(view='section' if dest is section else 'front',kind='leader',anchor=project(tip).tolist(),anchorOptions=[project(tip).tolist()])
 if kind in ('distance','thickness'):
  a,b=map(vector,m['points']);direction=unit(m['direction'])
  # Linear references may be centres, axes or virtual points in empty space.
  # Keep the supplied coordinates; validate direction, nominal and projection below.
  evidence=m.get('visualEvidence')
  if evidence is not None:
   tips=evidence.get('arrowTipsNormalized')
   if not tips or len(tips)!=2 or any(t is None for t in tips):raise ValueError('Missing visual endpoints for linear measurement')
   visual=np.array(tips[1],dtype=float)-np.array(tips[0],dtype=float);visual[1]*=-1
   predicted=np.array([np.dot(direction,dest[0]),np.dot(direction,dest[1])])
   if view=='section' and evidence.get('sectionAxisNormalized') is not None:
    axial=np.array(evidence['sectionAxisNormalized'],dtype=float);axial[1]*=-1
    axial/=np.linalg.norm(axial)
    radial=np.array([-axial[1],axial[0]])
    predicted=np.dot(direction,[0,0,1])*axial+np.dot(direction,dest[1])*radial
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
 if not found:
  ex=TopExp_Explorer(shape,TopAbs_EDGE)
  while ex.More():
   curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
   if curve.GetType()==GeomAbs_Circle:
    c=curve.Circle();o=c.Location();d=c.Axis().Direction()
    if abs(c.Radius()-radius)<1e-5 and np.linalg.norm(center-[o.X(),o.Y(),o.Z()])<1e-5 and abs(abs(np.dot(axis,[d.X(),d.Y(),d.Z()]))-1)<1e-6 and abs(curve.LastParameter()-curve.FirstParameter()-2*math.pi)<1e-5:found=True;break
   ex.Next()
 if not found:raise ValueError('No matching cylinder or full circular edge at the specified reference')
 if abs(abs(np.dot(axis,dest[2]))-1)<1e-6:return dict(view='section' if dest is section else 'front',kind='circle',center=project(center).tolist(),radius=radius)
 radial=project(axis);perp=np.array([-radial[1],radial[0]])
 if np.linalg.norm(perp)<1e-7:raise ValueError('Unsupported projected diameter')
 return dict(view='section' if dest is section else 'front',kind='sectionDiameter',centerOptions=[project(center).tolist()],radius=radius,radialDirection=perp/np.linalg.norm(perp))
