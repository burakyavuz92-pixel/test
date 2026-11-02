import math,unittest
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve,BRepAdaptor_Surface
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Circle,GeomAbs_Torus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from full_round import annular_full_round,xyz

def volume(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return p.Mass()

class FullRoundTests(unittest.TestCase):
 def ring(self,axis=(0,0,1),center=(0,0,0)):
  frame=gp_Ax2(gp_Pnt(*center),gp_Dir(*axis));shape=BRepAlgoAPI_Cut(BRepPrimAPI_MakeCylinder(frame,20,10).Shape(),BRepPrimAPI_MakeCylinder(frame,17,10).Shape()).Shape()
  edges=[];ex=TopExp_Explorer(shape,TopAbs_EDGE)
  while ex.More():
   edge=TopoDS.Edge_s(ex.Current());curve=BRepAdaptor_Curve(edge)
   if curve.GetType()==GeomAbs_Circle and np.linalg.norm(xyz(curve.Circle().Location())-center)<1e-6 and not any(edge.IsSame(e) for e in edges):edges.append(edge)
   ex.Next()
  return shape,edges
 def test_exact_radius_and_analytic_removed_volume(self):
  shape,edges=self.ring();result=annular_full_round(shape,edges,1.5)
  removed=2*math.pi*18.5*1.5**2*(2-math.pi/2)
  self.assertAlmostEqual(volume(shape)-volume(result),removed,places=6);self.assertTrue(BRepCheck_Analyzer(result).IsValid())
  radii=[];ex=TopExp_Explorer(result,TopAbs_FACE)
  while ex.More():
   surface=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
   if surface.GetType()==GeomAbs_Torus:radii.append(surface.Torus().MinorRadius())
   ex.Next()
  self.assertTrue(radii);self.assertTrue(all(abs(r-1.5)<1e-9 for r in radii))
 def test_translated_rotated_axis(self):
  s,e=self.ring((1,0,0),(10,-20,30));r=annular_full_round(s,e,1.5)
  self.assertAlmostEqual(volume(s)-volume(r),2*math.pi*18.5*1.5**2*(2-math.pi/2),places=6)
 def test_wrong_radius_is_not_adjusted(self):
  s,e=self.ring()
  with self.assertRaisesRegex(ValueError,'exactly fill'):annular_full_round(s,e,1.49)
 def test_one_edge_cannot_trigger_full_round(self):
  s,e=self.ring()
  with self.assertRaisesRegex(ValueError,'two distinct'):annular_full_round(s,e[:1],1.5)
 def test_executor_records_exact_fallback(self):
  from cad_recipe_executor import build
  recipe={'geometry':{'frames':[{'id':'world','origin':[0,0,0],'xAxis':[1,0,0],'zAxis':[0,0,1]}],'operations':[
   {'id':'outer','op':'cylinder','frame':'world','args':{'origin':[0,0,0],'direction':[0,0,1],'diameter':40,'length':10}},
   {'id':'inner','op':'cylinder','frame':'world','args':{'origin':[0,0,0],'direction':[0,0,1],'diameter':34,'length':10}},
   {'id':'ring','op':'cut','frame':'world','target':'outer','tool':'inner'},
   {'id':'rounded','op':'fillet','frame':'world','target':'ring','args':{'size':1.5,'selectors':[{'near':[r,0,0],'directionKind':'axis','direction':[0,0,1]} for r in (20,17)]}}],'result':'rounded'}}
  shape,_,checks=build(recipe)
  self.assertEqual(checks[-1]['nativeMethod'],'exact-annular-full-round')
  self.assertAlmostEqual(volume(shape),math.pi*(400-289)*10-2*math.pi*18.5*1.5**2*(2-math.pi/2),places=6)
if __name__=='__main__':unittest.main()
