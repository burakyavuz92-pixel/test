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
 def test_empty_custom_exception_preserves_product_reason(self):
  f=r.load_script('class _RowError(Exception):\n pass\ndef build_part(p):\n try: raise _RowError("Ölçü geçersiz")\n except _RowError as e: return {"error":str(e)}\n')
  self.assertEqual(f({}),{'error':'Ölçü geçersiz'})
 def test_exception_class_cannot_execute_code_or_use_custom_bases(self):
  for definition in ('class X(Exception):\n x=1', 'class X(Exception):\n def method(self): return 1', 'class X(object):\n pass', 'class X(Exception, ValueError):\n pass', 'class X(Exception, metaclass=Exception):\n pass', '@Exception\nclass X(Exception):\n pass'):
   with self.subTest(definition=definition),self.assertRaises(ValueError):r.load_script(definition+'\ndef build_part(p):return None')
 def test_class_builder_is_not_directly_accessible(self):
  with self.assertRaises(ValueError):r.load_script('def build_part(p):return __build_class__')
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
  for expr in ('float(5)','True'):
   with self.assertRaises(ValueError):r.load_script('R='+expr+'\ndef build_part(p): return R')

class NumericContainers(unittest.TestCase):
 def test_vector_and_matrix_literals(self):
  source='AXIS=[0.,0.,1.]\nMATRIX=((1,0),(0,1))\ndef build_measurements(p): return list(AXIS), MATRIX'
  self.assertEqual(r.load_script(source,'build_measurements')({}),([0.,0.,1.],((1,0),(0,1))))
 def test_non_numeric_or_executable_containers_are_rejected(self):
  for expr in ('[True,0,1]','[0,"axis",1]','[0,None,1]','{"x":1}','[float(1)]','[1e999]','[[[[[1]]]]]'):
   with self.subTest(expr=expr),self.assertRaises(ValueError):r.load_script('AXIS='+expr+'\ndef build_part(p): return AXIS')

class StandardBuiltins(unittest.TestCase):
 def test_predicates_and_data_exceptions(self):
  f=r.load_script('def build_part(p):\n try:\n  if any(v is None for v in p.values()): return False\n  return all(v>0 for v in p.values()) and p["required"]\n except (TypeError,KeyError): return "invalid"')
  self.assertFalse(f({'required':None}));self.assertTrue(f({'required':1}));self.assertEqual(f({'other':1}),'invalid');self.assertEqual(f({'required':'x'}),'invalid')

if __name__=='__main__':unittest.main()
