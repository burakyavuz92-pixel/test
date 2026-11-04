import unittest,numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from script_measurements import anchor
class Supports(unittest.TestCase):
 def setUp(self):
  self.s=BRepPrimAPI_MakeCone(10,11,1).Shape();self.front=tuple(np.array(x) for x in ([1,0,0],[0,1,0],[0,0,1]));self.section=tuple(np.array(x) for x in ([0,0,1],[0,1,0],[1,0,0]))
 def chamfer(self):return {'kind':'chamfer','nominal':1,'angleDeg':45,'points':[[10,0,0],[11,0,1]],'direction':[0,0,1],'visualEvidence':{'arrowTipsNormalized':[[.2,.3]]}}
 def test_single_arrow_chamfer(self):
  result=anchor(self.s,self.chamfer(),1,self.front,self.section,'section')
  self.assertEqual(result['kind'],'leader');self.assertAlmostEqual(abs(result['anchor'][1]),10.5)
 def test_wrong_angle_rejected(self):
  m=self.chamfer();m['angleDeg']=30
  with self.assertRaisesRegex(ValueError,'angle'):anchor(self.s,m,1,self.front,self.section,'section')
 def test_no_chamfer_face_rejected(self):
  m=self.chamfer();m['points']=[[9,0,0],[10,0,1]]
  with self.assertRaises(ValueError):anchor(self.s,m,1,self.front,self.section,'section')
 def circle(self):return {'kind':'diameter','nominal':22,'center':[0,0,1],'axis':[0,0,1],'radius':11}
 def test_cone_end_in_front_and_section(self):
  self.assertEqual(anchor(self.s,self.circle(),22,self.front,self.section,'front')['kind'],'circle')
  self.assertEqual(anchor(self.s,self.circle(),22,self.front,self.section,'section')['kind'],'sectionDiameter')
 def test_wrong_circle_location_rejected(self):
  m=self.circle();m['center']=[0,0,.5]
  with self.assertRaisesRegex(ValueError,'reference'):anchor(self.s,m,22,self.front,self.section,'front')
 def test_wrong_axis_rejected(self):
  m=self.circle();m['axis']=[1,0,0]
  with self.assertRaises(ValueError):anchor(self.s,m,22,self.front,self.section,'front')
