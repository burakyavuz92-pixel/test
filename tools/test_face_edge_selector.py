import unittest,sys,math
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from face_edge_selector import select_edge

class Selection(unittest.TestCase):
 def test_inner_outer_are_distinct(self):
  outer=BRepPrimAPI_MakeCylinder(15,5).Shape()
  bore=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,-1),gp_Dir(0,0,1)),10,7).Shape()
  body=BRepAlgoAPI_Cut(outer,bore).Shape()
  for radius in (10,15):
   edge=select_edge(body,[{'kind':'plane','normal':[0,0,1],'offset':0},{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':radius}])
   self.assertAlmostEqual(BRepAdaptor_Curve(edge).Circle().Radius(),radius)
 def test_full_compiler_and_native_fillet(self):
  from cad_v9_compiler import compile_recipe
  from cad_recipe_executor import build,vol
  r={'schemaVersion':9,'geometry':{'features':[
   {'id':'body','op':'add','shape':{'kind':'cylinder','origin':[0,0,0],'direction':[0,0,1],'diameter':30,'length':5}},
   {'id':'bore','op':'cut','shape':{'kind':'cylinder','origin':[0,0,-1],'direction':[0,0,1],'diameter':20,'length':7}},
   {'id':'round','op':'fillet','size':1,'selectors':[{'faces':[{'kind':'plane','normal':[0,0,1],'offset':0},{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':10}]}]}]},'drawing':{}}
  shape,_,checks=build(compile_recipe(r,{},'test'))
  self.assertTrue(checks[-1]['validBrep'])
  self.assertLess(vol(shape),math.pi*(225-100)*5)
 def test_ambiguous_pair_rejected(self):
  with self.assertRaisesRegex(ValueError,'found 0'):select_edge(BRepPrimAPI_MakeCylinder(15,5).Shape(),[{'kind':'plane','normal':[0,0,1],'offset':0},{'kind':'plane','normal':[0,0,1],'offset':0}])
 def test_wrong_pair_rejected(self):
  with self.assertRaisesRegex(ValueError,'found 0'):select_edge(BRepPrimAPI_MakeCylinder(15,5).Shape(),[{'kind':'plane','normal':[0,0,1],'offset':2},{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':15}])
if __name__=='__main__':unittest.main()
