import unittest,numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from script_measurements import anchor
class References(unittest.TestCase):
 def setUp(self):
  self.shape=BRepPrimAPI_MakeCylinder(10,5).Shape();self.front=tuple(np.array(x) for x in ([1,0,0],[0,1,0],[0,0,1]));self.section=tuple(np.array(x) for x in ([0,0,1],[0,1,0],[1,0,0]))
 def test_arbitrary_diameter_label(self):
  m={'kind':'diameter','nominal':20,'center':[0,0,2],'axis':[0,0,1],'radius':10};self.assertEqual(anchor(self.shape,m,20,self.front,self.section)['kind'],'circle')
 def test_explicit_endpoint_aliases(self):
  m={'kind':'distance','nominal':5,'p1':[0,0,0],'p2':[0,0,5],'direction':[0,0,1]}
  self.assertEqual(anchor(self.shape,m,5,self.front,self.section)['kind'],'linear')
 def test_distance_boundaries(self):
  m={'kind':'distance','nominal':5,'points':[[0,0,0],[0,0,5]],'direction':[0,0,1]};self.assertEqual(anchor(self.shape,m,5,self.front,self.section)['kind'],'linear')
 def test_wrong_body_endpoint_rejected(self):
  m={'kind':'distance','nominal':5,'points':[[0,0,1],[0,0,6]],'direction':[0,0,1]}
  with self.assertRaisesRegex(ValueError,'endpoint'):anchor(self.shape,m,5,self.front,self.section)
 def test_wrong_value_rejected(self):
  m={'kind':'diameter','nominal':21,'center':[0,0,0],'axis':[0,0,1],'radius':10}
  with self.assertRaises(ValueError):anchor(self.shape,m,20,self.front,self.section)
 def test_false_radius_on_flat_face_rejected(self):
  m={'kind':'radius','nominal':2,'center':[0,0,-2],'axis':[1,0,0],'radius':2,'point':[0,0,0]}
  with self.assertRaises(ValueError):anchor(self.shape,m,2,self.front,self.section)
 def test_other_axis(self):
  shape=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(3,4,5),gp_Dir(1,0,0)),7,12).Shape();m={'kind':'diameter','nominal':14,'center':[6,4,5],'axis':[1,0,0],'radius':7};self.assertEqual(anchor(shape,m,14,self.front,self.section,'section')['kind'],'circle')
