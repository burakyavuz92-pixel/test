import unittest
from PIL import Image,ImageFont
from dimension_annotations import Annotations
class AnnotationTextTests(unittest.TestCase):
 def painter(self):return Annotations(Image.new('RGB',(1754,1236),'white'),lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n),1)
 def test_asymmetric_tolerance_is_stacked_and_narrower(self):
  p=self.painter();a=p.text_layer('0,5 (+0,5/-0,2)');b=p.text_layer('0,5 (+0,5 | -0,2)')
  self.assertLess(a.width,b.width);self.assertGreater(a.height,p.text_layer('0,5').height)
 def test_glyph_mask_excludes_empty_rotated_corners(self):
  p=self.painter();layer=p.text_layer('LONG TEXT').rotate(45,expand=True,fillcolor='white');mask=p.text_mask(layer)
  self.assertEqual(mask.getpixel((0,0)),0);self.assertIsNotNone(mask.getbbox())
 def test_identical_labels_collide(self):
  p=self.painter();p.label('25',(200,200))
  with self.assertRaisesRegex(ValueError,'collide'):p.label('25',(200,200))
 def test_thread_label_stays_single_line(self):
  p=self.painter();self.assertLess(p.text_layer('M22x1,5-6H').height,p.text_layer('0,5 (+0,5/-0,2)').height)
if __name__=='__main__':unittest.main()
