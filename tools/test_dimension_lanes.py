import unittest
from PIL import Image,ImageFont,ImageDraw
from dimension_lanes import render,side_for

class Bands(unittest.TestCase):
 def draw(self,size,measurements,text='12 (±0,5)'):
  image=Image.new('RGB',(1754,1236),'white');x0,y0,x1,y1=size;ImageDraw.Draw(image).rectangle(size,outline='black')
  layout={'sourcePixels':[1754,1236]};box={'front':[x0,y0,x1,y1]};items=[]
  for i,(span,where) in enumerate(measurements):
   binding={'view':'front','marker':{'label':str(i),'centerPixels':list(where)},'sourceFrame':{'bboxPixels':list(size)}}
   items.append({'id':str(i),'kind':'linear','view':'front','points':[[x0,y0],[x0+span,y0]],'axis':'X','templateBinding':binding,'dimension':{}})
  pix=lambda p:(p[0],y0+y1-p[1]);r=render(image,lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n),1,items,pix,pix,layout,box,lambda d:text)
  return r
 def test_bottom_total_is_outside_and_further_than_small(self):
  for width in (120,250,480):
   r=self.draw([400,250,400+width,600],[(width,[450,650]),(15,[450,640])]);self.assertFalse(r['failed']);records={v['id']:v for v in r['templatePlacements']};self.assertGreater(records['0']['bandCoordinate'],records['1']['bandCoordinate']);self.assertGreater(records['1']['bandCoordinate'],600)
 def test_narrow_dimension_uses_external_text(self):
  r=self.draw([400,250,700,600],[(5,[450,650])]);self.assertFalse(r['failed']);self.assertTrue(r['templatePlacements'][0]['narrow']);self.assertGreater(r['templatePlacements'][0]['placedLabelPixels'][0],405)
 def test_long_tolerance_consumes_space(self):
  r=self.draw([400,250,700,600],[(10,[450,650]),(300,[450,650])],'10,5 (+1,25/-0,75)');self.assertFalse(r['failed'])
 def test_full_page_fails_instead_of_entering_geometry(self):
  r=self.draw([400,250,700,870],[(300,[450,890])]);self.assertTrue(r['failed'])
 def test_side_does_not_depend_on_dimension_label(self):
  self.assertEqual(side_for(False,[100,300],[200,200,500,600]),'left')

class SeparateHoles(unittest.TestCase):
 def test_same_diameter_remains_two_labels(self):
  image=Image.new('RGB',(1754,1236),'white');items=[]
  for i,y in enumerate((350,500)):
   items.append({'id':str(i),'kind':'circle','view':'front','center':[600,y],'radius':8,'dimension':{},'templateBinding':{'view':'front','marker':{'label':str(i),'centerPixels':[760,850-y]},'sourceFrame':{'bboxPixels':[400,250,800,600]}}})
  pix=lambda p:(p[0],850-p[1])
  r=render(image,lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n),1,items,pix,pix,{'sourcePixels':[1754,1236]},{'front':[400,250,800,600]},lambda d:'Ø16')
  self.assertFalse(r['failed']);self.assertEqual(len(r['placed']),2);self.assertNotEqual(r['templatePlacements'][0]['placedLabelPixels'],r['templatePlacements'][1]['placedLabelPixels'])
 def test_crossing_penalty_ignores_shared_endpoints(self):
  import numpy as np
  from dimension_lanes import crossing
  p=lambda x:np.array(x,dtype=float)
  self.assertTrue(crossing(p([0,0]),p([10,10]),p([0,10]),p([10,0])))
  self.assertFalse(crossing(p([0,0]),p([10,10]),p([10,10]),p([20,10])))
