import unittest
from drafting_style import choose_scale,scale_label,PIXELS,PAPER_MM,PX_PER_MM
class Drafting(unittest.TestCase):
 def test_paper_ratio(self):
  self.assertLess(abs(PIXELS[0]/PIXELS[1]-PAPER_MM[0]/PAPER_MM[1]),.001)
 def test_shared_scale_fits_both_views(self):
  panels=[(330,140,890,710),(55,140,240,710)]
  extents=[(259,259),(33,259)]
  scale=choose_scale(extents,panels)
  for (w,h),(_,_,pw,ph) in zip(extents,panels):
   self.assertLessEqual(w*scale*PX_PER_MM,pw-30+.001)
   self.assertLessEqual(h*scale*PX_PER_MM,ph-30+.001)
  self.assertEqual(scale_label(scale),'1:4')
 def test_smaller_parts_have_larger_scale(self):
  panels=[(330,140,890,710),(55,140,240,710)]
  self.assertGreater(choose_scale([(114,114),(33,114)],panels),choose_scale([(259,259),(33,259)],panels))
if __name__=='__main__':unittest.main()
