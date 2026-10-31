import unittest,math,copy
from cad_recipe_executor import build,vol,sheet
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
class SelectorTests(unittest.TestCase):
 def filleted(self,kind,direction):
  r=NativeRecipeTests().recipe();r['geometry']['operations'].append({'id':'rounded','op':'fillet','frame':'world','target':'hole','args':{'size':1,'selectors':[{'operation':'base','role':'edge','near':[10,0,0],'directionKind':kind,'direction':direction}]}});r['geometry']['result']='rounded';return r
 def test_circle_axis_selector(self):
  s,_,_=build(self.filleted('axis',[0,0,1]));self.assertLess(vol(s),math.pi*96*5)
 def test_circle_tangent_selector(self):
  a,_,_=build(self.filleted('axis',[0,0,1]));t,_,_=build(self.filleted('tangent',[0,1,0]));self.assertAlmostEqual(vol(a),vol(t),places=5)
 def test_axis_is_not_silently_used_as_tangent(self):
  from OCP.Standard import Standard_Failure
  # Z is a cylinder seam tangent, not the circular edge tangent; it must not round the circle.
  with self.assertRaises((ValueError,Standard_Failure)):build(self.filleted('tangent',[0,0,1]))
 def test_rotated_frame_axis(self):
  r=self.filleted('axis',[0,0,1]);r['geometry']['frames'][0]['xAxis']=[0,1,0];r['geometry']['frames'][0]['zAxis']=[1,0,0];s,_,_=build(r);self.assertGreater(vol(s),0)
class PresentationTests(unittest.TestCase):
 def test_legacy_detail_metadata_does_not_request_extra_view(self):
  import tempfile,pathlib
  from PIL import Image
  r=NativeRecipeTests().recipe();r['outputId']='no-detail';shape,shapes,_=build(r)
  r['drawing']={'views':[{'id':'front','direction':[0,0,1],'up':[0,1,0]},{'id':'cut','direction':[1,0,0],'up':[0,1,0]},{'id':'iso','direction':[1,1,1],'up':[0,1,0]}],
   'sections':[{'id':'A','view':'cut','kind':'planar','cuttingPlanes':[{'point':[0,0,0],'normal':[1,0,0]}]}],
   'dimensions':[], 'details':[{'id':'B','sourceView':'missing','features':['missing']}]}
  for view in r['drawing']['views']:view['projection']='orthographic'
  with tempfile.TemporaryDirectory() as t:
   folder=pathlib.Path(t);source=folder/'input.jpg';Image.new('RGB',(20,20),'white').save(source)
   report=sheet(r,shape,shapes,folder,source)
   self.assertNotIn('details',report);self.assertTrue((folder/'no-detail.jpeg').exists())
if __name__=='__main__':unittest.main()
