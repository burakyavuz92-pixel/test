"""Bounded geometry-only CadQuery script runner; no network/API use."""
import ast,json,pathlib,sys,math,os,subprocess,traceback,hashlib,time,resource,builtins,re
import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
ALLOWED_MODULES={'cadquery':cq,'math':math}
SAFE_BUILTINS={n:getattr(builtins,n) for n in ['abs','min','max','sum','range','len','float','int','bool','dict','list','tuple','set','enumerate','zip','round','sorted','isinstance','ValueError','RuntimeError','Exception']}
DENIED={'open','eval','exec','compile','getattr','setattr','delattr','globals','locals','vars','dir','help','input','breakpoint','type','object','super','os','sys','subprocess','socket','pathlib','requests','builtins','importlib','inspect','ctypes','exporters','importers'}

def load_script(source):
 tree=ast.parse(source)
 for statement in tree.body:
  if not isinstance(statement,(ast.Import,ast.ImportFrom,ast.FunctionDef)):raise ValueError('Only imports and function definitions are allowed at module level')
 for node in ast.walk(tree):
  if isinstance(node,(ast.Import,ast.ImportFrom)):
   names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module]
   if any(n not in ALLOWED_MODULES for n in names):raise ValueError('Only cadquery/math imports are supported')
  if isinstance(node,ast.Name) and (node.id in DENIED or node.id.startswith('__')):raise ValueError('Forbidden script name: '+node.id)
  if isinstance(node,ast.Attribute) and (node.attr in DENIED or node.attr.startswith('_') or node.attr.lower().startswith(('export','import','write','read','save','dump'))):raise ValueError('Forbidden script attribute: '+node.attr)
  if isinstance(node,ast.FunctionDef) and node.decorator_list:raise ValueError('Decorators not supported')
  if isinstance(node,(ast.ClassDef,ast.With,ast.AsyncWith,ast.Global,ast.Nonlocal)):raise ValueError('Unsupported Python construct')
 def importer(name,globals=None,locals=None,fromlist=(),level=0):
  if name not in ALLOWED_MODULES or level:raise ImportError('Only cadquery/math imports')
  return ALLOWED_MODULES[name]
 env={'__builtins__':dict(SAFE_BUILTINS,__import__=importer),'cq':cq,'math':math};exec(compile(tree,'generated_geometry.py','exec'),env)
 if not callable(env.get('build_part')):raise ValueError('build_part(p) missing')
 return env['build_part']

# Defense in depth for Python IO during generated function execution; not a general OS sandbox.
ACTIVE=False
def audit(event,args):
 if ACTIVE and (event=='open' or event.startswith(('socket.','subprocess.','os.system','os.exec','os.spawn'))):raise RuntimeError('Script IO is not permitted')
sys.addaudithook(audit)

def run(folder,validate_only=False):
 global ACTIVE
 root=pathlib.Path(folder).resolve();source=(root/'part.py').read_text();rows=json.loads((root/'rows.json').read_text());result=[]
 resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024*1024,128*1024*1024))
 try:build=load_script(source)
 except Exception as e:
  (root/'script-results.json').write_text(json.dumps({'apiCalls':0,'scriptAccepted':False,'error':str(e),'results':[]},indent=2));return False
 for row in rows:
  id=row['outputId']
  if not re.fullmatch(r'[A-Za-z0-9_-]+',id):raise ValueError('Invalid output identifier')
  out=root/id;out.mkdir(exist_ok=True);start=time.monotonic()
  try:
   ACTIVE=True
   try:part=build(dict(row['parameters']))
   finally:ACTIVE=False
   if isinstance(part,cq.Workplane):part=part.val()
   if not isinstance(part,cq.Shape):raise ValueError('build_part must return a CadQuery Shape/Workplane')
   solids=part.Solids()
   if len(solids)!=1 or not BRepCheck_Analyzer(part.wrapped).IsValid() or part.Volume()<=0:raise ValueError('Expected one valid positive-volume solid')
   if validate_only:
    result.append({'outputId':id,'status':'geometry-validated','validBrep':True,'solidCount':1,'volumeMm3':part.Volume(),'seconds':time.monotonic()-start});continue
   step=out/(id+'.step');cq.exporters.export(part,str(step));cq.exporters.export(part,str(out/'mesh.stl'),tolerance=.08,angularTolerance=.15)
   rd=STEPControl_Reader()
   if rd.ReadFile(str(step))!=IFSelect_RetDone:raise ValueError('STEP read failed')
   rd.TransferRoots();restored=cq.Shape.cast(rd.OneShape())
   if not restored.isValid() or not math.isclose(restored.Volume(),part.Volume(),rel_tol=1e-6):raise ValueError('STEP roundtrip mismatch')
   (out/'parameters.json').write_text(json.dumps(row,indent=2))
   preview=subprocess.run([os.getenv('OCCT_PYTHON','/workspace/occt-venv/bin/python'),str(pathlib.Path(__file__).with_name('cad_script_preview.py')),str(out)],capture_output=True,text=True,timeout=90)
   (out/'preview.log').write_text(preview.stdout+preview.stderr)
   if preview.returncode:raise ValueError('Geometry preview failed; see preview.log')
   result.append({'outputId':id,'status':'geometry-preview-produced','validBrep':True,'solidCount':1,'volumeMm3':part.Volume(),'stepRoundtrip':True,'seconds':time.monotonic()-start})
  except Exception as e:ACTIVE=False;traceback.print_exc();result.append({'outputId':id,'status':'failed','error':str(e)})
 report={'apiCalls':0,'validationOnly':validate_only,'cadqueryVersion':cq.__version__,'scriptSha256':hashlib.sha256(source.encode()).hexdigest(),'scriptAccepted':True,'results':result}
 (root/'script-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return len(result)>0 and all(r['status']==('geometry-validated' if validate_only else 'geometry-preview-produced') for r in result)
if __name__=='__main__':sys.exit(0 if run(sys.argv[1],'--validate-only' in sys.argv[2:]) else 1)
