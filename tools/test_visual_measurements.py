import unittest,numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from script_measurements import anchor
from visual_measurements import merge,canonical
class VisualReferences(unittest.TestCase):
 def test_equal_numbers_do_not_make_equal_relations(self):
  front=tuple(np.array(v) for v in ([1,0,0],[0,1,0],[0,0,1]));section=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
  for t in (1.5,2,3.2):
   r=t*4;body=BRepAlgoAPI_Cut(BRepPrimAPI_MakeCylinder(r,12).Shape(),BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,t),gp_Dir(0,0,1)),r-t,12).Shape()).Shape()
   evidence={'arrowTipsNormalized':[[.2,.2],[.2,.3]]}
   good={'kind':'thickness','nominal':t,'points':[[0,r,6],[0,r-t,6]],'direction':[0,1,0],'visualEvidence':evidence}
   self.assertEqual(anchor(body,good,t,front,section,'section')['kind'],'linear')
   bad=dict(good,points=[[0,0,0],[0,0,t]],direction=[0,0,1])
   with self.assertRaisesRegex(ValueError,'Visual arrow direction'):anchor(body,bad,t,front,section,'section')
 def test_decimal_label_normalization(self):self.assertEqual(canonical('[R1,5]'),canonical('R1.5'))
 def test_model_cannot_authorize_unbracketed_label(self):
  layout={'sourcePixels':[1000,500],'candidates':[]};new,e=merge(layout,[{'label':'R7','view':'section','centerNormalized':[.2,.4],'arrowTipsNormalized':[[.3,.5]]}]);self.assertEqual(len(new['candidates']),0);self.assertEqual(layout['candidates'],[])
 def test_view_conflict_not_silently_replaced(self):
  layout={'sourcePixels':[1000,500],'candidates':[{'label':'Q','view':'front'}]}
  with self.assertRaisesRegex(ValueError,'disagree'):merge(layout,[{'label':'Q','view':'section','centerNormalized':[.2,.4]}])
 def test_invalid_coordinates_rejected(self):
  with self.assertRaises(ValueError):merge({'sourcePixels':[100,100],'candidates':[]},[{'label':'X','view':'section','centerNormalized':[2,.4]}])

class SectionProjection(unittest.TestCase):
 def test_radius_uses_visual_side_on_verified_torus(self):
  from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
  from script_measurements import section_meridian
  shape=BRepPrimAPI_MakeTorus(12,2).Shape();section=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
  for side,y in ((1,.2),(-1,.8)):
   m={'kind':'radius','radius':2,'center':[12,0,0],'point':[14,0,0],'axis':[0,1,0],'visualEvidence':{'arrowTipsNormalized':[[.2,y]],'viewCenterNormalized':[.2,.5]}}
   r=section_meridian(shape,m,section);self.assertAlmostEqual(r['center'][1],side*12);self.assertAlmostEqual(r['point'][1],side*14)
 def test_axis_distance_does_not_require_material_at_axis(self):
  from script_measurements import anchor
  front=tuple(np.array(v) for v in ([1,0,0],[0,1,0],[0,0,1]));section=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
  body=BRepPrimAPI_MakeCylinder(20,5).Shape()
  for x in (-7,7):body=BRepAlgoAPI_Cut(body,BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,0,-1),gp_Dir(0,0,1)),2,7).Shape()).Shape()
  m={'kind':'distance','nominal':14,'points':[[-7,0,2],[7,0,2]],'direction':[1,0,0]}
  self.assertEqual(anchor(body,m,14,front,section,'front')['kind'],'linear')
