import unittest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from cad_script_sheet import dimensions
class ScriptDrawing(unittest.TestCase):
 def test_diameter_and_tolerance_preserved(self):
  tolerance={'kind':'symmetric','upperDeviationMm':0.1,'lowerDeviationMm':-0.1}
  d=dimensions(BRepPrimAPI_MakeCylinder(10,5).Shape(),{'A':{'nominalMm':20,'diameterSymbol':True,'tolerance':tolerance}})[0]
  self.assertEqual(d['relation']['surfaces'][0]['radius'],10);self.assertEqual(d['sourceMeasurement']['tolerance'],tolerance)
 def test_same_size_at_distinct_axes_is_not_guessed(self):
  from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
  a=BRepPrimAPI_MakeCylinder(10,5).Shape();b=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(30,0,0),gp_Dir(0,0,1)),10,5).Shape()
  shape=BRepAlgoAPI_Fuse(a,b).Shape();self.assertNotIn('relation',dimensions(shape,{'A':{'nominalMm':20,'diameterSymbol':True}})[0])
 def test_distance_not_attached_by_equal_number(self):
  d=dimensions(BRepPrimAPI_MakeCylinder(10,5).Shape(),{'E':{'nominalMm':5,'diameterSymbol':False}})[0];self.assertNotIn('relation',d)
 def test_blank_skipped_and_zero_retained(self):
  ds=dimensions(BRepPrimAPI_MakeCylinder(10,5).Shape(),{'B':{'nominalMm':0},'C':{'nominalMm':None}});self.assertEqual(len(ds),1);self.assertEqual(ds[0]['nominal'],0)
