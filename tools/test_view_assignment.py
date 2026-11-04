import unittest,numpy as np
from visual_measurements import merge
from script_measurements import anchor
from cad_recipe_executor import text_value
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
class ViewAssignment(unittest.TestCase):
 def test_outside_label_uses_geometry_frame(self):
  layout={'sourcePixels':[1000,500],'candidates':[{'label':'E','view':'front','centerNormalized':[.8,.5]}]}
  marker={'id':'e','label':'E','view':'section','centerNormalized':[.8,.5],'arrowTipsNormalized':[[.75,.3],[.75,.7]],'viewFrameNormalized':[.1,.3,.4,.7],'sectionAxisNormalized':[1,0]}
  result,_=merge(layout,[marker]);self.assertEqual(result['candidates'][0]['view'],'section');self.assertEqual(result['candidates'][0]['ocrRegionView'],'front')
  self.assertEqual(result['sourceFrames']['section']['bboxPixels'],[100,150,400,350])
  self.assertEqual(layout['candidates'][0]['view'],'front')
 def test_frame_needs_arrow_evidence(self):
  with self.assertRaisesRegex(ValueError,'arrow evidence'):merge({'sourcePixels':[100,100],'candidates':[{'label':'A','view':'front'}]},[{'label':'A','view':'section','centerNormalized':[.2,.3],'viewFrameNormalized':[0,0,.5,.5]}])
 def test_horizontal_section_direction(self):
  shape=BRepPrimAPI_MakeCylinder(10,5).Shape();front=tuple(np.array(v) for v in ([1,0,0],[0,1,0],[0,0,1]));section=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
  m={'kind':'distance','nominal':5,'points':[[0,0,0],[0,0,5]],'direction':[0,0,1],'visualEvidence':{'arrowTipsNormalized':[[.1,.2],[.4,.2]],'sectionAxisNormalized':[1,0]}}
  self.assertEqual(anchor(shape,m,5,front,section,'section')['kind'],'linear')
 def test_diameter_text_is_explicit_user_choice(self):
  for flag,expected in [(False,'20,9'),(True,'Ø20,9')]:
   self.assertEqual(text_value({'type':'diameter','nominal':20.9,'sourceMeasurement':{'diameterSymbol':flag}}),expected)
  self.assertEqual(text_value({'type':'diameter','nominal':20.9,'sourceMeasurement':{'displayText':'E metni','diameterSymbol':True}}),'E metni')
  self.assertEqual(text_value({'type':'diameter','nominal':20.9,'sourceMeasurement':{'displayText':'özel metin','diameterSymbol':False}}),'özel metin')
