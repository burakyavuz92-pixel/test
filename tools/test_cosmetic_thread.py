import unittest,numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from cosmetic_thread import segments
class Cosmetic(unittest.TestCase):
 def setUp(self):
  s=BRepPrimAPI_MakeCylinder(5,20).Shape();ex=TopExp_Explorer(s,TopAbs_FACE)
  while ex.More():
   f=TopoDS.Face_s(ex.Current())
   if BRepAdaptor_Surface(f).GetType()==GeomAbs_Cylinder:self.face=f;break
   ex.Next()
  self.basis=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
 def cut(self,x):return segments(self.face,{'kind':'planar','cuttingPlanes':[{'point':[x,0,0],'normal':[1,0,0]}]},self.basis)
 def test_full_face_length_and_two_ends(self):
  g=self.cut(0);self.assertEqual(len(g),1);self.assertEqual(len(g[0]['ends']),2)
  for line in g[0]['inner']:self.assertEqual(sorted(p[0] for p in line),[0,20])
 def test_off_axis_and_outside(self):
  self.assertEqual(len(self.cut(3)),1);self.assertFalse(self.cut(6));self.assertFalse(self.cut(5))
 def test_untagged(self):self.assertFalse(segments(None,{},self.basis))
 def test_stepped_band_clips_actual_region(self):
  s={'kind':'stepped','sweepDirection':[0,0,1],'worldPath':[[0,10,0],[0,2,0],[3,2,0],[3,-2,0],[0,-2,0],[0,-10,0]]}
  self.assertEqual(len(segments(self.face,s,self.basis)),1) # paired generators from the two outer bands
