import unittest
from adaptive_scale import select,candidates
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

 def test_plate_intermediate_scales_without_reducing_annotation_padding(self):
  for diameter,expected in ((160,.4),(227,.25)):
   ext=[(diameter,diameter),(33,diameter)]
   scale,_,_,_=select(ext,[(70,54),(66.5,47)],[(45,100,1360,730),(45,360,1660,470)],lambda *args:[])
   self.assertAlmostEqual(scale,expected)
   self.assertGreater(scale,.2)
 def test_long_sections_fit_in_both_orientations_with_original_gap(self):
  for section in ((260,25),(25,260)):
   ext=[(25,25),section];region=(45,100,1360,730)
   scale,panels,packages,_=select(ext,[(70,54),(66.5,47)],[region],lambda *args:[])
   for (w,h),(x,y,pw,ph) in zip(ext,panels):
    self.assertLessEqual(w*scale*PX_PER_MM,pw+1e-6)
    self.assertLessEqual(h*scale*PX_PER_MM,ph+1e-6)
   for x,y,w,h in packages:
    self.assertGreaterEqual(x,region[0]-1e-6);self.assertGreaterEqual(y,region[1]-1e-6)
    self.assertLessEqual(x+w,region[0]+region[2]+1e-6);self.assertLessEqual(y+h,region[1]+region[3]+1e-6)
   gap=packages[0][0]-packages[1][0]-packages[1][2]
   self.assertGreaterEqual(gap,40-1e-6);self.assertLessEqual(gap,120+1e-6)
 def test_new_intermediate_scale_still_rejected_on_annotation_collision(self):
  scale,_,_,attempts=select([(160,160),(33,160)],[(70,54),(66.5,47)],[(45,100,1360,730)],
    lambda s,*args:['annotation collision'] if s>.25 else [])
  self.assertAlmostEqual(scale,.25)
  self.assertTrue(any(a['scale']==.4 and 'annotation collision' in a['reasons'] for a in attempts))

 def test_previous_scale_choices_remain_available(self):
  import math
  ext=[(25,25),(43.8,25)];regions=[(45,100,1360,730)]
  grid=candidates(ext,regions)
  bound=max(min(w/e[0],h/e[1])/PX_PER_MM for _,_,w,h in regions for e in ext)
  top=math.ceil(math.log10(bound))
  for k in range(top-10,top+1):
   for m in (1,2,5):
    previous=m*10.**k
    if previous<=bound+1e-10:self.assertTrue(any(math.isclose(previous,s,rel_tol=1e-12,abs_tol=0) for s in grid))
