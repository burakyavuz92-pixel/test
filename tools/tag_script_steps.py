"""Evaluate optional face-tag function and atomically update named STEP outputs."""
import sys,json,resource
from pathlib import Path
import cad_script_runner as runner
from product_failures import active_rows,model_value,record_failure
from step_face_tags import write_named
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
root=Path(sys.argv[1]);resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024*1024,128*1024*1024))
fn=runner.load_script((root/'face-tags.py').read_text(),'build_face_tags');reports=[]
for row in active_rows(root):
 try:
  runner.ACTIVE=True
  try:tags=model_value(fn(dict(row['parameters'])))
  finally:runner.ACTIVE=False
  path=root/row['outputId']/(row['outputId']+'.step');r=STEPControl_Reader()
  if r.ReadFile(str(path))!=IFSelect_RetDone:raise ValueError('Missing STEP')
  r.TransferRoots();reports.append({'outputId':row['outputId'],'status':'tagged','tags':write_named(r.OneShape(),tags,path) if tags else []})
 except Exception as ex:
  runner.ACTIVE=False;record_failure(root,row['outputId'],'face-tags',ex);reports.append({'outputId':row['outputId'],'status':'failed','error':str(ex)})
(root/'face-tag-results.json').write_text(json.dumps({'results':reports},indent=2));print('Named STEP files verified:',sum(r['status']=='tagged' for r in reports))
sys.exit(0 if all(r['status']=='tagged' for r in reports) else 1)
