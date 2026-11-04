import unittest
from visual_measurements import merge
class Alternatives(unittest.TestCase):
 def test_model_matches_observed_five_not_high_confidence_nine(self):
  candidates=[{'label':t,'view':'unassigned','centerNormalized':[.2,.3],'observationGroup':1,'confidence':score} for t,score in [('9',93),('5',34)]]
  result,_=merge({'sourcePixels':[1000,700],'candidates':candidates},[{'id':'m5','label':'5','view':'section','centerNormalized':[.2,.3]}])
  self.assertEqual(result['candidates'][1]['occurrenceId'],'m5');self.assertNotIn('occurrenceId',result['candidates'][0]);self.assertEqual(result['unconfirmedModelMarkers'],[])
 def test_far_reading_is_not_reused(self):
  result,_=merge({'sourcePixels':[1000,700],'candidates':[{'label':'C','view':'unassigned','centerNormalized':[.8,.8]}]},[{'id':'c','label':'C','view':'section','centerNormalized':[.1,.1]}])
  self.assertEqual(len(result['unconfirmedModelMarkers']),1);self.assertNotIn('occurrenceId',result['candidates'][0])
 def test_missing_label_does_not_abort_other_labels(self):
  r,_=merge({'sourcePixels':[1000,700],'candidates':[{'label':'A','view':'unassigned','centerNormalized':[.2,.3]}]},[{'id':'a','label':'A','view':'section','centerNormalized':[.2,.3]},{'id':'c','label':'C','view':'section','centerNormalized':[.5,.3]}])
  self.assertEqual(r['candidates'][0]['occurrenceId'],'a');self.assertEqual(r['unconfirmedModelMarkers'][0]['label'],'C')
