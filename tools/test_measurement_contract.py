import copy,unittest
from cad_v9_compiler import compile_recipe
from cad_recipe_executor import build

def recipe():
 return {'schemaVersion':9,'contractRevision':2,'geometry':{'features':[{'id':'body','op':'add','shape':{'kind':'cylinder','origin':[0,0,0],'direction':[0,0,1],'diameter':20,'length':5}}]},'drawing':{'dimensions':[{'id':'d','type':'distance','axis':'Z','sourceLabel':'E','valueSource':{'kind':'column','column':'E'},'targets':[{'operation':'body','role':'physical end faces'}],'relation':{'kind':'planeDistance','surfaces':[{'kind':'plane','normal':[0,0,1],'offset':0},{'kind':'plane','normal':[0,0,1],'offset':5}]}}]}}
class Measurements(unittest.TestCase):
 def test_final_face_distance(self):
  build(compile_recipe(recipe(),{'E':{'nominalMm':5}},'test'))
 def test_wrong_nominal_rejected_before_output(self):
  with self.assertRaisesRegex(ValueError,'Measurement mismatch'):build(compile_recipe(recipe(),{'E':{'nominalMm':4}},'test'))
 def test_missing_physical_face(self):
  r=recipe();r['drawing']['dimensions'][0]['relation']['surfaces'][1]['offset']=4
  with self.assertRaisesRegex(ValueError,'uniquely match'):build(compile_recipe(r,{'E':{'nominalMm':4}},'test'))
 def test_column_replaced_with_constant(self):
  r=recipe();r['drawing']['dimensions'][0]['valueSource']={'kind':'constant','value':5,'unit':'mm'}
  with self.assertRaisesRegex(ValueError,'numeric sourceLabel'):compile_recipe(r,{},'test')
 def test_role_alone_is_insufficient(self):
  r=recipe();del r['drawing']['dimensions'][0]['relation']
  with self.assertRaisesRegex(ValueError,'explicit measurement'):compile_recipe(r,{'E':{'nominalMm':5}},'test')
 def test_ignored_edge_constraint_rejected(self):
  r=recipe();r['geometry']['features'].append({'id':'f','op':'fillet','size':1,'selectors':[{'operation':'body','near':[10,0,0]}]})
  with self.assertRaisesRegex(ValueError,'support faces'):compile_recipe(r,{'E':{'nominalMm':5}},'test')

class RevolvedMeasurements(unittest.TestCase):
 def test_revolved_wall_and_diameter(self):
  r=recipe();r['geometry']['features'][0]['shape']={'kind':'revolve','profile':{'frame':{'origin':[0,0,0],'u':[1,0,0],'v':[0,0,1]},'outer':{'kind':'polyline','points':[[7,0],[10,0],[10,5],[7,5]]}},'axisOrigin':[0,0,0],'axisDirection':[0,0,1],'angleDeg':360}
  cylinder=lambda radius:{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':radius}
  d=r['drawing']['dimensions'][0];d.update(type='diameter',sourceLabel='A',valueSource={'kind':'column','column':'A'},axis='radial',relation={'kind':'diameter','surfaces':[cylinder(10)]})
  wall=copy.deepcopy(d);wall.update(id='wall',type='thickness',sourceLabel='3',valueSource={'kind':'constant','value':3,'unit':'mm'},relation={'kind':'wallThickness','surfaces':[cylinder(7),cylinder(10)]})
  r['drawing']['dimensions'].append(wall)
  compiled=compile_recipe(r,{'A':{'nominalMm':20}},'test');shape,_,_=build(compiled)
  from dimension_annotations import resolve_anchors
  import numpy as np
  front=tuple(np.array(v) for v in ([1,0,0],[0,1,0],[0,0,1]))
  section=tuple(np.array(v) for v in ([0,0,1],[0,1,0],[1,0,0]))
  anchors,errors,_=resolve_anchors(compiled,shape,front,section,[-10,-10,0,10,10,5])
  self.assertEqual(errors,[]);self.assertEqual(len(anchors),2)

class PhysicalRelations(unittest.TestCase):
 def test_overlap_is_not_measured_as_external_length(self):
  r=recipe();r['geometry']['features'].append({'id':'boss','op':'add','shape':{'kind':'cylinder','origin':[0,0,4],'direction':[0,0,1],'diameter':10,'length':6}})
  d=r['drawing']['dimensions'][0];d['relation']['surfaces'][0]['offset']=5;d['relation']['surfaces'][1]['offset']=10
  build(compile_recipe(r,{'E':{'nominalMm':5}},'test'))
 def test_axis_offset_to_datum(self):
  r=recipe();r['geometry']['features'][0]['shape']['origin']=[3,0,0]
  r['drawing']['dimensions'][0]['relation']={'kind':'axisDistance','direction':[1,0,0],'surfaces':[{'kind':'cylinder','axisOrigin':[3,0,0],'axisDirection':[0,0,1],'radius':10},{'kind':'datumAxis','axisOrigin':[0,0,0],'axisDirection':[0,0,1]}]}
  build(compile_recipe(r,{'E':{'nominalMm':3}},'test'))
