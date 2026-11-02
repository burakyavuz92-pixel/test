import unittest
from PIL import Image,ImageFont
from dimension_annotations import render_template_dimensions
class TemplatePositionTests(unittest.TestCase):
 def test_short_span_keeps_template_text_center(self):
  # The full label is wider than the 8px measured span, but the template
  # intentionally places its center between those endpoints.
  frame={'bboxPixels':[100,100,500,500]}
  binding={'view':'section','marker':{'label':'J','centerPixels':[250,300]},'sourceFrame':frame}
  item={'id':'j','kind':'linear','axis':'Y','view':'section','points':[[300,296],[300,304]],'dimension':{},'templateBinding':binding}
  pix=lambda p:(p[0],600-p[1])
  im=Image.new('RGB',(1754,1236),'white')
  result=render_template_dimensions(im,lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n),1,[item],pix,pix,{'sourcePixels':[1754,1236]},{'section':[100,100,500,500]},lambda d:'Ø20,5 (±0,5)')
  self.assertFalse(result['failed'])
  record=result['templatePlacements'][0]
  self.assertEqual(record['placedLabelPixels'],record['templateLabelPixels'])
  # Vertical dimension line should sit just beyond the rotated text's ink edge.
  from dimension_annotations import Annotations
  height=Annotations(im,lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n),1).text_layer('Ø20,5 (±0,5)').height
  expected=round(250+height/2+2)
  self.assertTrue(any(im.getpixel((x,300))==(0,0,0) for x in range(expected-1,expected+2)))
if __name__=='__main__':unittest.main()
