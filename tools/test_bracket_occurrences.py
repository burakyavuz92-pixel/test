import unittest
from bracket_content import literal
from inspect_bracket_layout import parse_token
from visual_measurements import merge
from template_layout import bind_dimensions
class Occurrences(unittest.TestCase):
 def test_content_and_semantics(self):
  self.assertEqual(parse_token('[25 ±0,5]'),'25±0,5')
  self.assertEqual(literal(parse_token('[25 ±0,5]'))['tolerance']['lowerDeviationMm'],-.5)
  self.assertEqual(literal(parse_token('[1 X 45°]'))['chamferAngleDeg'],45)
  self.assertEqual(parse_token('[serbest metin]'),'serbestmetin')
  for s in ('25 ±0,5','1 X 45°','[A','[A][B]'):self.assertIsNone(parse_token(s))
 def test_same_text_distinct_occurrences(self):
  cs=[{'id':i,'label':'1X45°','view':'section','centerNormalized':[x,.5]} for i,x in [(1,.1),(2,.4)]]
  ms=[{'id':i,'label':'1 X 45°','view':'section','centerNormalized':[x,.5]} for i,x in [('left',.1),('right',.4)]]
  layout,evidence=merge({'sourcePixels':[100,100],'candidates':cs,'sourceFrames':{'section':{'bboxPixels':[0,0,100,100]}}},ms)
  ds=[{'id':i,'sourceLabel':'1X45°','sourceOccurrenceId':i,'effectiveVisible':True} for i in ('left','right')]
  bound,omitted,unresolved=bind_dimensions(ds,layout)
  self.assertEqual([b['marker']['id'] for b in bound],[1,2]);self.assertFalse(omitted);self.assertFalse(unresolved)
 def test_one_ocr_occurrence_cannot_be_reused(self):
  c={'label':'3','view':'section','centerNormalized':[.1,.5]}
  ms=[{'id':i,'label':'3','view':'section','centerNormalized':[.1,.5]} for i in ('a','b')]
  result,_=merge({'sourcePixels':[100,100],'candidates':[c]},ms)
  self.assertEqual(result['candidates'][0]['occurrenceId'],'a')
  self.assertEqual(result['unconfirmedModelMarkers'][0]['id'],'b')

 def test_closing_bracket_normalization_is_column_bound(self):
  from inspect_bracket_layout import recover_closing_bracket
  self.assertEqual(recover_closing_bracket('[Al',{'A':True}),'A')
  for text in ('Al','A','[Zl','[A','[A]'):
   self.assertIsNone(recover_closing_bracket(text,{'A':True}))

 def test_plus_minus_stroke_detection(self):
  from inspect_bracket_layout import visible_plus_minus
  from PIL import Image,ImageDraw
  im=Image.new('L',(60,100),255);d=ImageDraw.Draw(im)
  d.rectangle((5,35,38,40),fill=0);d.rectangle((19,20,24,55),fill=0)
  word={'left':0,'top':0,'width':60,'height':100}
  self.assertFalse(visible_plus_minus(im,word))
  d.rectangle((5,65,38,70),fill=0)
  self.assertTrue(visible_plus_minus(im,word))

 def test_known_label_survives_other_rotations(self):
  from inspect_bracket_layout import candidate_rank
  self.assertGreater(candidate_rank('A',69,{'A':True}),candidate_rank('v',95,{'A':True}))
