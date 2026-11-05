import json,tempfile,unittest,subprocess,sys
from pathlib import Path
from product_failures import model_value,ModelProductError,record_failure,active_rows,failures

class ProductFailures(unittest.TestCase):
 def test_success_is_data_only(self):
  value=[{'id':'a'}];self.assertIs(model_value(value),value)
 def test_model_reason_is_preserved(self):
  with self.assertRaisesRegex(ModelProductError,'ölçü eksik'):model_value({'error':'ölçü eksik'})
 def test_failure_blocks_only_its_product_and_retains_first_cause(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'rows.json').write_text(json.dumps([{'outputId':str(i)} for i in range(6)]))
   record_failure(root,'1','geometry',ModelProductError('neden'))
   record_failure(root,'4','measurements',ValueError('runtime'))
   record_failure(root,'1','sheets',ValueError('secondary'))
   self.assertEqual([r['outputId'] for r in active_rows(root)],['0','2','3','5'])
   self.assertEqual([r['origin'] for r in failures(root)],['model','software'])
   self.assertEqual(failures(root)[0]['reason'],'neden')
 def test_measurement_errors_do_not_stop_remaining_rows(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'rows.json').write_text(json.dumps([{'outputId':str(i),'parameters':{'i':i}} for i in range(6)]))
   (root/'measurements.py').write_text('def build_measurements(p):\n if p["i"]==1:return {"error":"eksik bilgi"}\n if p["i"]==4:raise ValueError("runtime")\n return []\n')
   result=subprocess.run([sys.executable,str(Path(__file__).with_name('evaluate_script_measurements.py')),d],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertEqual(set(json.loads((root/'measurement-references.json').read_text())),{'0','2','3','5'})
   self.assertEqual([r['origin'] for r in failures(root)],['model','software'])
 def test_geometry_keeps_successful_rows_and_classifies_failures(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'rows.json').write_text(json.dumps([{'outputId':str(i),'parameters':{'i':i}} for i in range(6)]))
   (root/'part.py').write_text('import cadquery as cq\ndef build_part(p):\n if p["i"]==1:return {"error":"eksik bilgi"}\n if p["i"]==4:raise ValueError("runtime")\n return cq.Workplane("XY").box(2,3,4)\n')
   result=subprocess.run([sys.executable,str(Path(__file__).with_name('cad_script_runner.py')),d,'--validate-only'],capture_output=True,text=True)
   self.assertEqual(result.returncode,1,result.stderr)
   rows=json.loads((root/'script-results.json').read_text())['results']
   self.assertEqual(sum(r['status']=='geometry-validated' for r in rows),4)
   self.assertEqual([r['origin'] for r in failures(root)],['model','software'])
if __name__=='__main__':unittest.main()
