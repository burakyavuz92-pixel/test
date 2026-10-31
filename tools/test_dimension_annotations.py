import unittest
from PIL import Image,ImageFont
from dimension_annotations import resolve_anchors,render_dimensions
from cad_recipe_executor import build,basis,box
from cad_v9_compiler import compile_recipe

class Dimensions(unittest.TestCase):
 def setup_recipe(self,value=20):
  r={'schemaVersion':9,'geometry':{'features':[{'id':'stock','op':'add','shape':{'kind':'cylinder','origin':[0,0,-5],'direction':[0,0,1],'diameter':20,'length':5}}]},'drawing':{'dimensions':[{'id':'outside','type':'diameter','valueSource':{'kind':'constant','value':value,'unit':'mm'},'targets':[{'operation':'stock','role':'arbitrary text'}],'axis':'radial'}]}}
  return compile_recipe(r,{},'test')
 def anchors(self,r):
  shape,_,_=build(r)
  return resolve_anchors(r,shape,basis({'direction':[0,0,1],'up':[0,1,0]}),basis({'direction':[1,0,0],'up':[0,1,0]}),box(shape))
 def test_reference_is_independent_of_column_and_feature_names(self):
  a,u,o=self.anchors(self.setup_recipe());self.assertFalse(u);self.assertEqual(a[0]['radius'],10)
 def test_false_dimension_binding_is_reported(self):
  a,u,o=self.anchors(self.setup_recipe(25));self.assertFalse(a);self.assertIn('differs',u[0]['reason'])
 def test_unsupported_relation_is_not_guessed(self):
  r=self.setup_recipe();r['drawing']['dimensions'][0].update(type='angle',axis='Z')
  a,u,o=self.anchors(r);self.assertFalse(a);self.assertTrue(u)
 def test_failed_placement_leaves_no_anonymous_lines(self):
  im=Image.new('RGB',(1754,1236),'white');before=im.tobytes()
  item={'id':'test','kind':'circle','view':'front','center':[0,0],'radius':5,'dimension':{}}
  result=render_dimensions(im,lambda n:ImageFont.load_default(),1,[item],lambda p:p,lambda p:p,lambda d:'25')
  self.assertTrue(result['failed']);self.assertEqual(im.tobytes(),before)
if __name__=='__main__':unittest.main()
