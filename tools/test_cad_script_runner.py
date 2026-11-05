import unittest,math
import cad_script_runner as r
class ScriptTests(unittest.TestCase):
 def test_one_function_accepts_eighty_rows(self):
  f=r.load_script('import cadquery as cq\ndef build_part(p):\n return cq.Workplane("XY").circle(p["A"]/2).extrude(p["T"])\n')
  for i in range(80):
   d=10+i/10;p=f({'A':d,'T':3});self.assertAlmostEqual(p.val().Volume(),math.pi*(d/2)**2*3,places=5)
 def test_model_can_format_a_short_product_error(self):
  f=r.load_script('def build_part(p): return {"error":"Çap " + format(p["A"], "g") + " uygun değil"}')
  self.assertEqual(f({'A':20})['error'],'Çap 20 uygun değil')
 def test_forbidden_import(self):
  with self.assertRaises(ValueError):r.load_script('import os\ndef build_part(p): return None')
 def test_file_io_name_rejected(self):
  with self.assertRaises(ValueError):r.load_script('def build_part(p): return open("x","w")')
 def test_export_from_model_rejected(self):
  with self.assertRaises(ValueError):r.load_script('import cadquery as cq\ndef build_part(p): return cq.exporters.export(None,"x")')
 def test_no_toplevel_build(self):
  with self.assertRaises(ValueError):r.load_script('import cadquery as cq\nx=cq.Workplane("XY").box(1,1,1)\ndef build_part(p): return x')

 def test_numeric_module_constants(self):
  f=r.load_script('R=5.0\ndef build_part(p): return R')
  self.assertEqual(f({}),5)
  for expr in ('float(5)','[1,2]','True'):
   with self.assertRaises(ValueError):r.load_script('R='+expr+'\ndef build_part(p): return R')

if __name__=='__main__':unittest.main()
