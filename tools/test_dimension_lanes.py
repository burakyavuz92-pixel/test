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
 def test_narrow_dimension_stays_centered(self):
  r=self.draw([400,250,700,600],[(5,[450,650])]);self.assertFalse(r['failed']);self.assertTrue(r['templatePlacements'][0]['narrow']);self.assertAlmostEqual(r['templatePlacements'][0]['placedLabelPixels'][0],402.5)
 def test_sub_5mm_can_move_outside_but_5mm_stays_centered(self):
  for span in (2.8,5):
   r=self.draw([400,250,700,600],[(span,[450,650])],'2,8' if span<5 else '5')
   self.assertFalse(r['failed']);record=r['templatePlacements'][0]
   self.assertEqual(record['textPosition'],'outside-left' if span<5 else 'centered')
 def test_bottom_text_is_above_dimension_line(self):
  r=self.draw([400,250,700,600],[(300,[450,650])],'30')
  record=r['templatePlacements'][0];self.assertLess(record['placedLabelPixels'][1],record['bandCoordinate'])
 def test_first_band_is_3_5_mm_from_geometry(self):
  from drafting_style import PX_PER_MM
  r=self.draw([400,250,700,600],[(300,[450,650])],'30')
  self.assertFalse(r['failed']);self.assertAlmostEqual(r['templatePlacements'][0]['innerExtentMm'],3.5)
 def test_adjacent_bands_have_1_5mm_clearance(self):
  r=self.draw([400,250,700,600],[(150,[450,650]),(300,[450,650])],'20,9 (+0/-0,1)')
  self.assertFalse(r['failed']);a,b=r['templatePlacements']
  self.assertGreaterEqual(a['innerExtentMm'],3.5-1e-9)
  self.assertGreaterEqual(b['innerExtentMm']-a['outerExtentMm'],1.5-1e-9)
 def test_vertical_bands_reserve_text_and_tolerances_on_both_sides(self):
  for marker_x in (300,800):
   image=Image.new('RGB',(1754,1236),'white');bounds=[400,250,700,600]
   ImageDraw.Draw(image).rectangle(bounds,outline='black');items=[]
   for i,span in enumerate((150,300)):
    items.append({'id':str(i),'kind':'linear','points':[[400,280],[400,280+span]],'axis':'Y','dimension':{},'templateBinding':{'view':'front','marker':{'centerPixels':[marker_x,400]},'sourceFrame':{'bboxPixels':bounds}}})
   r=render(image,lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n),1,items,lambda p:p,lambda p:p,{'sourcePixels':[1754,1236]},{'front':bounds},lambda d:'20,9 (+0/-0,1)')
   self.assertFalse(r['failed']);a,b=r['templatePlacements']
   self.assertGreaterEqual(a['innerExtentMm'],3.5-1e-9)
   self.assertGreaterEqual(b['innerExtentMm']-a['outerExtentMm'],1.5-1e-9)
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

class ChamferClearance(unittest.TestCase):
 def test_chamfer_text_stays_outside_view(self):
  image=Image.new('RGB',(1754,1236),'white');bounds=[400,250,700,600]
  ImageDraw.Draw(image).rectangle(bounds,outline='black')
  item={'id':'pah','kind':'leader','view':'front','anchor':[410,400],'dimension':{'sourceMeasurement':{'chamferAngleDeg':35}},'templateBinding':{'view':'front','marker':{'centerPixels':[420,400]},'sourceFrame':{'bboxPixels':bounds}}}
  font=lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n)
  r=render(image,font,1,[item],lambda p:p,lambda p:p,{'sourcePixels':[1754,1236]},{'front':bounds},lambda d:'3x35°')
  self.assertFalse(r['failed']);x,y=r['templatePlacements'][0]['placedLabelPixels']
  self.assertTrue(x<bounds[0]-32 or x>bounds[2]+32 or y<bounds[1]-32 or y>bounds[3]+32)

class LeaderAlignment(unittest.TestCase):
 def test_chamfer_and_radius_align_with_existing_dimensions(self):
  for kind in ('chamfer','radius'):
   image=Image.new('RGB',(1754,1236),'white');bounds=[400,250,700,600]
   ImageDraw.Draw(image).rectangle(bounds,outline='black')
   binding=lambda xy:{'view':'front','marker':{'centerPixels':xy},'sourceFrame':{'bboxPixels':bounds}}
   items=[{'id':'base','kind':'linear','view':'front','points':[[400,600],[700,600]],'axis':'X','dimension':{},'templateBinding':binding([550,200])},
    {'id':'leader','kind':'leader','view':'front','anchor':[410,300],'dimension':{'type':kind,'scriptReference':{'kind':kind}},'templateBinding':binding([350,300])}]
   r=render(image,lambda n:ImageFont.truetype('/workspace/fonts/arial/arial.ttf',n),1,items,lambda p:(p[0],850-p[1]),lambda p:p,{'sourcePixels':[1754,1236]},{'front':bounds},lambda d:'R2' if d else '30')
   self.assertFalse(r['failed']);base,leader=r['templatePlacements'];self.assertEqual(leader['mode'],'aligned-leader')
   self.assertTrue(abs(base['placedLabelPixels'][0]-leader['placedLabelPixels'][0])<1e-6 or abs(base['placedLabelPixels'][1]-leader['placedLabelPixels'][1])<1e-6)
