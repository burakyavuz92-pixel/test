import sys,json,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cad_script_runner as runner
resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024*1024,16*1024*1024))
root=Path(sys.argv[1]);source=(root/'measurements.py').read_text();build=runner.load_script(source,'build_measurements');refs={}
for row in json.loads((root/'rows.json').read_text()):
 runner.ACTIVE=True
 try:refs[row['outputId']]=build(dict(row['parameters']))
 finally:runner.ACTIVE=False
(root/'measurement-references.json').write_text(json.dumps(refs,indent=2,allow_nan=False));print('References evaluated for',len(refs),'rows')
