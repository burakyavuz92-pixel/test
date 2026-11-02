import unittest
import numpy as np
from template_layout import bind_dimensions, map_source_point

class TemplateLayoutTests(unittest.TestCase):
 def layout(self):
  return {'sourceFrames':{'section':{'bboxPixels':[10,20,30,60]}},'candidates':[{'label':'J','view':'section','centerPixels':[5,40]},{'label':'R2','view':'section','centerPixels':[15,30]},{'label':'3','view':'section','centerPixels':[20,35]}]}
 def dim(self,id,column=None,value=2,kind='radius'):
  return {'id':id,'effectiveVisible':True,'type':kind,'nominal':value,'valueSource':{'kind':'column','column':column} if column else {'kind':'constant','value':value}}
 def test_column_binds_to_template_view_and_bare_column_is_omitted(self):
  b,o,u=bind_dimensions([self.dim('thread','J'),self.dim('hidden','K')],self.layout())
  self.assertEqual(b[0]['view'],'section');self.assertEqual(b[0]['marker']['label'],'J');self.assertEqual(o[0]['id'],'hidden');self.assertFalse(u)
 def test_literals_require_matching_bracket_marker(self):
  b,o,u=bind_dimensions([self.dim('r'),self.dim('wall',value=3,kind='distance'),self.dim('height',value=33,kind='distance')],self.layout())
  self.assertEqual([v['marker']['label'] for v in b],['R2','3']);self.assertEqual(o[0]['id'],'height');self.assertFalse(u)
 def test_ambiguous_marker_is_reported(self):
  layout=self.layout();layout['candidates'].append(dict(layout['candidates'][0]))
  b,o,u=bind_dimensions([self.dim('thread','J')],layout)
  self.assertFalse(b);self.assertFalse(o);self.assertEqual(u[0]['reason'],'Ambiguous template marker')
 def test_missing_view_frame_is_not_guessed(self):
  layout=self.layout();layout['sourceFrames']={}
  b,o,u=bind_dimensions([self.dim('thread','J')],layout)
  self.assertFalse(b);self.assertIn('unavailable',u[0]['reason'])
 def test_inside_affine_outside_preserves_paper_gap(self):
  binding={'sourceFrame':{'bboxPixels':[10,20,30,60]}}
  pix=lambda p:np.array([p[0]*10,100-p[1]*10])
  np.testing.assert_allclose(map_source_point(binding,[0,0,4,8],pix,[20,40],.5),[20,60])
  np.testing.assert_allclose(map_source_point(binding,[0,0,4,8],pix,[0,80],.5),[-5,110])
if __name__=='__main__':unittest.main()
