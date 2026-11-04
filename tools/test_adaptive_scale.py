import unittest
from adaptive_scale import select
from drafting_style import PX_PER_MM
class Adaptive(unittest.TestCase):
 def test_short_wide_and_long_narrow(self):
  for ext in ([(259,259),(33,259)],[(25,25),(43.8,25)],[(25,25),(25,43.8)]):
   scale,panels,packages,attempts=select(ext,[(50,40)]*2,[(45,100,1360,730)],lambda *args:[])
   self.assertTrue(attempts[-1]['accepted'])
   for e,p in zip(ext,panels):self.assertLessEqual(e[0]*scale*PX_PER_MM,p[2]+1e-6);self.assertLessEqual(e[1]*scale*PX_PER_MM,p[3]+1e-6)
   self.assertLess(packages[1][0],packages[0][0])
 def test_reject_large_actual_annotation_placement(self):
  scale,_,_,attempts=select([(25,25),(43.8,25)],[(40,40)]*2,[(0,0,1600,750)],lambda s,*args:['text collision'] if s>=1 else [])
  self.assertLess(scale,1);self.assertTrue(any('text collision' in a['reasons'] for a in attempts))
 def test_larger_text_reserves_more_space(self):
  args=([(25,25),(43.8,25)],)
  a=select(*args,[(20,20)]*2,[(0,0,1400,750)],lambda *args:[])[0]
  b=select(*args,[(200,150)]*2,[(0,0,1400,750)],lambda *args:[])[0]
  self.assertGreater(a,b)
 def test_deterministic(self):
  args=([(25,25),(43.8,25)],[(40,40)]*2,[(0,0,1400,750)],lambda *args:[])
  self.assertEqual(select(*args),select(*args))
