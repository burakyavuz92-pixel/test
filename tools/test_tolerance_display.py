import unittest
from PIL import Image,ImageFont
from cad_recipe_executor import text_value
from dimension_annotations import Annotations
class ToleranceDisplay(unittest.TestCase):
 def dim(self,upper,lower,diameter=False,text=None):
  return {'type':'diameter','nominal':20.9,'sourceMeasurement':{'diameterSymbol':diameter,'displayText':text,'tolerance':{'upperDeviationMm':upper,'lowerDeviationMm':lower}}}
 def test_equal_deviations(self):self.assertEqual(text_value(self.dim(.5,-.5)),'20,9 (±0,5)')
 def test_unequal_deviations(self):self.assertEqual(text_value(self.dim(0,-.1)),'20,9 (+0/-0,1)')
 def test_no_inferred_diameter_symbol(self):
  self.assertEqual(text_value(self.dim(.5,-.5,True)),'Ø20,9 (±0,5)')
  self.assertEqual(text_value(self.dim(.5,-.5,True,'M20')),'M20 (±0,5)')
 def test_asymmetric_is_rendered_stacked(self):
  painter=Annotations(Image.new('RGB',(600,300),'white'),lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n*2),2)
  plain=painter.text_layer('20,9');stacked=painter.text_layer(text_value(self.dim(0,-.1)))
  self.assertGreater(stacked.height,plain.height)
  self.assertGreater(stacked.width,plain.width)

 def test_small_unequal_deviations_still_stack(self):
  self.assertNotIn('±',text_value(self.dim(0,-1e-10)))
