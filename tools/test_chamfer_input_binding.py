import unittest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from cad_script_sheet import dimensions
from template_layout import bind_dimensions
from cad_recipe_executor import text_value
class ChamferInputBinding(unittest.TestCase):
 def test_chamfer_display_metadata_survives(self):
  cell={'nominalMm':3,'chamferAngleDeg':35,'displayText':'3x35°'}
  d=dimensions(BRepPrimAPI_MakeCylinder(10,5).Shape(),{'J':cell})[0]
  self.assertEqual(d['nominal'],3);self.assertEqual(d['sourceMeasurement']['chamferAngleDeg'],35);self.assertEqual(text_value(d),'3x35°')
 def test_geometry_only_column_not_annotated(self):
  ds=dimensions(BRepPrimAPI_MakeCylinder(10,5).Shape(),{'K':{'nominalMm':9.5},'F':{'nominalMm':1,'chamferAngleDeg':45,'displayText':'1x45°'}})
  layout={'candidates':[{'label':'F','view':'section'}],'sourceFrames':{'section':{'bboxPixels':[0,0,100,100]}}}
  bound,omitted,unresolved=bind_dimensions(ds,layout)
  self.assertEqual([b['dimension']['sourceLabel'] for b in bound],['F']);self.assertEqual(len(omitted),1);self.assertEqual(omitted[0]['id'],'column_K');self.assertFalse(unresolved)
