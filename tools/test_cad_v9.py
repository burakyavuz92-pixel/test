import copy,unittest
from cad_v9_compiler import Expressions,compile_recipe
from cad_recipe_executor import build,vol

def recipe():
 return {'schemaVersion':9,'geometry':{'features':[{'id':'base','op':'add','shape':{'kind':'box','size':[20,20,5]}}]},'drawing':{}}
def compile(r,cells=None):return compile_recipe(r,cells or {},'test')
class V9Tests(unittest.TestCase):
 def test_local_color_palette(self):
  for color,visible in [('#008000',False),('#000000',True),('green',False),('black',True)]:
   r=recipe();r['drawing']['dimensions']=[dict(id='d',type='distance',valueSource=dict(kind='constant',value=20,unit='mm'),targets=[dict(operation='base',role='length')],axis='X',sourceColor=color)]
   d=compile(r)['drawing']['dimensions'][0]
   self.assertEqual(d['effectiveVisible'],visible)
   self.assertEqual(d['canonicalSourceColor'],'#000000' if visible else '#008000')
 def test_missing_color_does_not_hide_measurement(self):
  r=recipe();r['drawing']['dimensions']=[dict(id='d',type='distance',valueSource=dict(kind='constant',value=20,unit='mm'),targets=[dict(operation='base',role='length')],axis='X')]
  self.assertTrue(compile(r)['drawing']['dimensions'][0]['effectiveVisible'])
 def test_lazy(self):
  e=Expressions({'A':{'nominalMm':None}},{'x':'=if(isblank(A),3,A/0)'})
  self.assertEqual(e.value('=x'),3);self.assertEqual(e.value('=false and A/0>1'),False)
 def test_unsafe_and_cycle(self):
  for s in ['=__import__(1)','=A.real','=2**4','=1/0']:
   with self.assertRaises(Exception):Expressions({'A':{'nominalMm':2}},{}).value(s)
  with self.assertRaises(Exception):Expressions({},{'x':'=y','y':'=x'}).value('=x')
 def test_hole_and_through_all(self):
  r=recipe();r['geometry']['features'].append({'id':'bore','op':'cut','shape':{'kind':'extrude','profile':{'outer':{'kind':'circle','center':[10,10],'diameter':4}},'extent':'throughAll'}})
  final,_,_=build(compile(r));self.assertAlmostEqual(vol(final),2000-3.141592653589793*20,places=5)
 def test_profile_holes(self):
  r=recipe();r['geometry']['features'][0]['shape']={'kind':'extrude','profile':{'outer':{'kind':'circle','center':[0,0],'diameter':20},'holes':[{'kind':'circle','center':[0,0],'diameter':10}]},'extent':{'from':2,'to':7}}
  final,_,_=build(compile(r));self.assertAlmostEqual(vol(final),375*3.141592653589793,places=5)
 def test_optional_zero(self):
  r=recipe();r['geometry']['features'].append({'id':'bore','op':'cut','when':'=not isblank(E)','shape':{'kind':'cylinder','origin':['=F',10,0],'direction':[0,0,1],'diameter':'=E','length':5}})
  a=compile(r,{'E':{'nominalMm':None},'F':{'nominalMm':None}});self.assertFalse(a['geometry']['featureApplied']['bore'])
  b=compile(r,{'E':{'nominalMm':2},'F':{'nominalMm':0}});self.assertTrue(b['geometry']['featureApplied']['bore'])
 def test_polar_seed_offset(self):
  r=recipe();r['geometry']['features'][0]['shape']={'kind':'cylinder','origin':[0,0,0],'direction':[0,0,1],'diameter':40,'length':5}
  r['geometry']['features'].append({'id':'holes','op':'cut','shape':{'kind':'cylinder','origin':[10,0,0],'direction':[0,0,1],'diameter':2,'length':5},'instances':{'kind':'polar','count':4,'axisOrigin':[0,0,0],'axisDirection':[0,0,1],'startAngleDeg':0,'stepAngleDeg':90}})
  final,_,_=build(compile(r));self.assertAlmostEqual(vol(final),1980*3.141592653589793,places=5)
 def test_no_material_cut(self):
  r=recipe();r['geometry']['features'].append({'id':'miss','op':'cut','shape':{'kind':'cylinder','origin':[100,100,0],'direction':[0,0,1],'diameter':2,'length':5}})
  with self.assertRaisesRegex(ValueError,'does not remove'):build(compile(r))
 def test_dimension_binding(self):
  r=recipe();r['drawing']['dimensions']=[dict(id='d',type='distance',valueSource=dict(kind='column',column='A'),targets=[dict(operation='base',role='length')],axis='X',sourceColor='black')]
  tol=dict(kind='symmetric',upperDeviationMm=1,lowerDeviationMm=-1)
  d=compile(r,{'A':dict(nominalMm=20,tolerance=tol)})['drawing']['dimensions'][0]
  self.assertEqual(d['nominal'],20);self.assertEqual(d['sourceMeasurement']['tolerance'],tol)
 def test_detail_request_rejected(self):
  r=recipe();r['drawing']['details']=[{'id':'B'}]
  with self.assertRaisesRegex(ValueError,'Detail views are not supported'):compile(r)
 def test_no_detail_field(self):
  self.assertNotIn('details',compile(recipe())['drawing'])
 def test_source_untouched(self):
  r=recipe();before=copy.deepcopy(r);compile(r);self.assertEqual(r,before)
if __name__=='__main__':unittest.main()
