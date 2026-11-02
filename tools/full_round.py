"""Exact full-round construction for two concentric circular edges of an annular end.

Only used when the ordinary equal-radius fillet fails. No radius perturbation,
product names or inferred dimensional changes are permitted here.
"""
import math
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve,BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Circle,GeomAbs_Plane,GeomAbs_Cylinder
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE,TopAbs_IN,TopAbs_OUT
from OCP.TopoDS import TopoDS
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakeTorus
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2

def xyz(p):return np.array([p.X(),p.Y(),p.Z()])
def cut(a,b):
 op=BRepAlgoAPI_Cut(a,b);op.Build()
 if not op.IsDone():raise ValueError('Full-round boolean failed')
 return op.Shape()

def annular_full_round(shape,edges,radius):
 if len(edges)!=2 or edges[0].IsSame(edges[1]):raise ValueError('Full round requires two distinct edges')
 curves=[BRepAdaptor_Curve(e) for e in edges]
 if any(c.GetType()!=GeomAbs_Circle or abs(c.LastParameter()-c.FirstParameter()-2*math.pi)>1e-6 for c in curves):raise ValueError('Full round requires complete circular edges')
 circles=[c.Circle() for c in curves];center=xyz(circles[0].Location());axis=xyz(circles[0].Axis().Direction());radii=sorted(c.Radius() for c in circles);inner,outer=radii
 if inner<=0 or radius<=0 or abs(outer-inner-2*radius)>1e-6:raise ValueError('Fillet radii do not exactly fill annular thickness')
 if np.linalg.norm(xyz(circles[1].Location())-center)>1e-6 or abs(abs(np.dot(axis,xyz(circles[1].Axis().Direction())))-1)>1e-7:raise ValueError('Circular edges are not concentric and coplanar')
 # Require their shared planar face to be precisely the annular end, not a
 # partial ring or a face with extra holes/steps.
 faces=[];supports=[False,False];ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  face=TopoDS.Face_s(ex.Current());surface=BRepAdaptor_Surface(face)
  if surface.GetType()==GeomAbs_Cylinder:
   cylinder=surface.Cylinder();d=xyz(cylinder.Axis().Direction())
   ee=TopExp_Explorer(face,TopAbs_EDGE)
   while ee.More():
    for i,edge in enumerate(edges):
     if edge.IsSame(ee.Current()) and abs(cylinder.Radius()-circles[i].Radius())<1e-6 and abs(abs(np.dot(axis,d))-1)<1e-7 and np.linalg.norm(np.cross(xyz(cylinder.Location())-center,axis))<1e-6:supports[i]=True
    ee.Next()
  if surface.GetType()==GeomAbs_Plane:
   found=[False,False];boundary=[];ee=TopExp_Explorer(face,TopAbs_EDGE)
   while ee.More():
    edge=TopoDS.Edge_s(ee.Current())
    if not any(edge.IsSame(e) for e in boundary):boundary.append(edge)
    for i,selected in enumerate(edges):found[i]|=edge.IsSame(selected)
    ee.Next()
   props=GProp_GProps();BRepGProp.SurfaceProperties_s(face,props)
   if all(found) and len(boundary)==2 and abs(props.Mass()-math.pi*(outer**2-inner**2))<1e-5:faces.append(face)
  ex.Next()
 if len(faces)!=1 or not all(supports):raise ValueError('Edges must bound one plain annular end between coaxial cylindrical sides')
 radial=xyz(circles[0].XAxis().Direction());mid=(inner+outer)/2
 def state(p):return BRepClass3d_SolidClassifier(shape,gp_Pnt(*p),1e-7).State()
 forward=state(center+radial*mid+axis*radius*.5);backward=state(center+radial*mid-axis*radius*.5)
 if forward==TopAbs_IN and backward==TopAbs_OUT:inward=axis
 elif backward==TopAbs_IN and forward==TopAbs_OUT:inward=-axis
 else:raise ValueError('Annular end does not have one unambiguous material side')
 frame=gp_Ax2(gp_Pnt(*center),gp_Dir(*inward))
 slab=cut(BRepPrimAPI_MakeCylinder(frame,outer,radius).Shape(),BRepPrimAPI_MakeCylinder(frame,inner,radius).Shape())
 missing=GProp_GProps();BRepGProp.VolumeProperties_s(cut(slab,shape),missing)
 if abs(missing.Mass())>max(1e-7,math.pi*(outer**2-inner**2)*radius*1e-9):raise ValueError('Full-round zone is interrupted or cylindrical walls are too short')
 # A full torus is the exact envelope; only its endward half intersects the
 # slab. Subtract the slab outside that envelope, preserving all other faces.
 torus=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(*(center+inward*radius)),gp_Dir(*inward)),mid,radius).Shape()
 result=cut(shape,cut(slab,torus))
 if result.IsNull() or not BRepCheck_Analyzer(result).IsValid():raise ValueError('Invalid full-round result')
 return result
