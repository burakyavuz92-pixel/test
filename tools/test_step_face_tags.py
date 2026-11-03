import unittest,tempfile
from pathlib import Path
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox,BRepPrimAPI_MakeCylinder
from step_face_tags import write_named,read_tags
class Tags(unittest.TestCase):
 def test_plane_name_roundtrip(self):
  for size in (5,11):
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'part.step';tag={'name':'mount_surface','surface':{'kind':'plane','normal':[0,0,1],'offset':size},'point':[1,1,size]};report=write_named(BRepPrimAPI_MakeBox(20,30,size).Shape(),[tag],path);self.assertTrue(report[0]['roundtripVerified']);self.assertEqual(set(read_tags(path,['mount_surface'])),{'mount_surface'})
 def test_cylinder_name_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   tag={'name':'bore_axis','surface':{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':8},'point':[8,0,3]};self.assertTrue(write_named(BRepPrimAPI_MakeCylinder(8,9).Shape(),[tag],Path(d)/'part.step'))
 def test_unknown_face_fails_without_output(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'part.step'
   with self.assertRaises(ValueError):write_named(BRepPrimAPI_MakeBox(20,30,5).Shape(),[{'name':'bad','surface':{'kind':'plane','normal':[0,0,1],'offset':99},'point':[0,0,99]}],path)
   self.assertFalse(path.exists())
 def test_duplicate_name_rejected(self):
  tag={'name':'same','surface':{'kind':'plane','normal':[0,0,1],'offset':0},'point':[1,1,0]}
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):write_named(BRepPrimAPI_MakeBox(20,30,5).Shape(),[tag,tag],Path(d)/'part.step')
 def test_unique_surface_ignores_historical_point_in_hole(self):
  from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
  from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
  body=BRepAlgoAPI_Cut(BRepPrimAPI_MakeBox(20,30,5).Shape(),BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10,15,-1),gp_Dir(0,0,1)),3,7).Shape()).Shape()
  with tempfile.TemporaryDirectory() as d:
   self.assertTrue(write_named(body,[{'name':'hole_void','surface':{'kind':'plane','normal':[0,0,1],'offset':5},'point':[10,15,5]}],Path(d)/'part.step'))

 def test_pointless_plane_selection(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertTrue(write_named(BRepPrimAPI_MakeBox(20,30,5).Shape(),[{'name':'mount','surface':{'kind':'plane','normal':[0,0,1],'offset':5}}],Path(d)/'part.step'))
