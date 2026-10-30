import unittest,math,copy
from cad_recipe_executor import build,vol
class NativeRecipeTests(unittest.TestCase):
 def recipe(self):
  return {'geometry':{'frames':[{'id':'world','origin':[0,0,0],'xAxis':[1,0,0],'zAxis':[0,0,1]}],'operations':[
   {'id':'base','op':'cylinder','frame':'world','args':{'origin':[0,0,0],'direction':[0,0,1],'diameter':20,'length':5}},
   {'id':'hole','op':'hole','frame':'world','target':'base','args':{'origin':[0,0,0],'direction':[0,0,1],'diameter':4,'throughAll':True,'depth':None}}],'result':'hole'}}
 def test_through_hole_volume(self):
  s,_,_=build(self.recipe());self.assertAlmostEqual(vol(s),math.pi*(100-4)*5,places=5)
 def test_translated_frame_volume(self):
  r=self.recipe();r['geometry']['frames'][0]['origin']=[100,-20,30];s,_,_=build(r);self.assertAlmostEqual(vol(s),math.pi*(100-4)*5,places=5)
 def test_nonintersecting_hole_rejected(self):
  r=self.recipe();r['geometry']['operations'][1]['args']['origin']=[50,0,0]
  with self.assertRaisesRegex(ValueError,'does not remove'):build(r)
 def test_unknown_operation_not_reinterpreted(self):
  r=self.recipe();r['geometry']['operations'][1]['op']='unknown'
  with self.assertRaisesRegex(ValueError,'Unsupported'):build(r)
if __name__=='__main__':unittest.main()
