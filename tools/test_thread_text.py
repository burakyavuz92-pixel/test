import unittest
from cad_recipe_executor import text_value
class Threads(unittest.TestCase):
 def test_thread_replaces_geometric_value(self):
  for callout in ['M22x1,5-6H','1/4"-18 NPT','G1/4']:
   d={'nominal':20.5,'type':'diameter','sourceMeasurement':{'threadCallout':callout,'tolerance':{'upperDeviationMm':.5,'lowerDeviationMm':-.5}}}
   self.assertEqual(text_value(d),callout)
 def test_plain_tolerance_stays(self):
  self.assertEqual(text_value({'nominal':20.5,'type':'diameter','sourceMeasurement':{'diameterSymbol':True,'tolerance':{'upperDeviationMm':.5,'lowerDeviationMm':-.5}}}),'Ø20,5 (±0,5)')
if __name__=='__main__':unittest.main()
