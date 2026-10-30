import unittest,math,copy
from cad_recipe_executor import build,vol,clipped_lines,detail_region,sheet
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
class DetailTests(unittest.TestCase):
 def test_line_crossing_crop_keeps_visible_segment(self):
  self.assertEqual(clipped_lines([[(-2.,0.),(2.,0.)]],[-1.,-1.,1.,1.]),[[(-1.,0.),(1.,0.)]])
 def test_line_outside_crop_is_removed(self):
  self.assertEqual(clipped_lines([[(2.,2.),(3.,3.)]],[-1.,-1.,1.,1.]),[])
 def test_detail_reuses_focus_solid_not_whole_modified_body(self):
  r=NativeRecipeTests().recipe();_,shapes,_=build(r)
  r['geometry']['operations'].insert(1,{'id':'boss','op':'cylinder','frame':'world','args':{'origin':[0,0,0],'direction':[0,0,1],'diameter':4,'length':2}})
  _,shapes,_=build(r)
  roi=detail_region(r,shapes,{'features':['boss','hole']},{'direction':[0,0,1],'up':[0,1,0]})
  self.assertLess(roi[2]-roi[0],6)
 def test_detail_preview_is_rendered_from_existing_shape(self):
  import tempfile,pathlib
  from PIL import Image
  r=NativeRecipeTests().recipe();r['outputId']='detail-test';shape,shapes,_=build(r)
  r['drawing']={'dimensions':[],'views':[{'id':'front','direction':[0,0,1],'up':[0,1,0],'projection':'orthographic'},{'id':'cut','direction':[1,0,0],'up':[0,1,0],'projection':'orthographic'},{'id':'iso','direction':[1,-1,1],'up':[0,0,1],'projection':'orthographic'}],
   'sections':[{'id':'AA','view':'cut','kind':'planar','cuttingPlanes':[{'point':[0,0,0],'normal':[1,0,0]}]}],
   'details':[{'id':'B','label':'B','sourceView':'cut','features':['base'],'sheetBox':[.3,.64,.12,.16]}]}
  with tempfile.TemporaryDirectory() as temp:
   folder=pathlib.Path(temp);source=folder/'source.jpg';Image.new('RGB',(20,20),'white').save(source)
   report=sheet(r,shape,shapes,folder,source)
   self.assertEqual(report['details'][0]['sourceView'],'cut');self.assertTrue((folder/'detail-test.jpeg').exists())
if __name__=='__main__':unittest.main()
