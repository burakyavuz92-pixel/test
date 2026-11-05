import sys,json,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cad_script_runner as runner
from product_failures import active_rows,model_value,record_failure
resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024*1024,16*1024*1024))
root=Path(sys.argv[1])
# Validate both sources together; only definitions/imports/constants are executed.
# Measurement code can reuse geometry helpers without copying or changing geometry.
geometry=(root/'part.py').read_text() if (root/'part.py').exists() else ''
source=geometry+'\n'+(root/'measurements.py').read_text()
build=runner.load_script(source,'build_measurements');refs={}
for row in active_rows(root):
 runner.ACTIVE=True
 try:refs[row['outputId']]=model_value(build(dict(row['parameters'])))
 except Exception as ex:
  runner.ACTIVE=False;record_failure(root,row['outputId'],'measurements',ex)
 finally:runner.ACTIVE=False
(root/'measurement-references.json').write_text(json.dumps(refs,indent=2,allow_nan=False));print('References evaluated for',len(refs),'rows')
