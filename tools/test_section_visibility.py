import unittest
from cad_recipe_executor import build,section_lines
import test_cad_recipe_executor as fixtures
class SectionVisibilityTests(unittest.TestCase):
 def test_hole_boundaries_extend_across_wall_thickness(self):
  shape,_,_=build(fixtures.NativeRecipeTests().recipe())
  lines,loops=section_lines(shape,{'kind':'planar','cuttingPlanes':[{'point':[0,0,0],'normal':[1,0,0]}]}, {'direction':[1,0,0],'up':[0,1,0]})
  # In this side projection the through-hole edges run across z=0..5
  # at y=-2 and y=+2, rather than leaving unconnected cut profiles.
  for y in (-2,2):
   self.assertTrue(any(max(p[0] for p in line)-min(p[0] for p in line)>4.99 and all(abs(p[1]-y)<1e-5 for p in line) for line in lines),f'Missing wall edge at {y}')
  self.assertTrue(loops)
if __name__=='__main__':unittest.main()
