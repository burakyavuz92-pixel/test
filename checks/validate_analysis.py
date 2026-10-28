"""Offline regression checks. Synthetic mutations are never model results."""
import copy,json,os,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[1]
dotnet=os.environ.get('DOTNET_EXECUTABLE','dotnet')
original=json.loads((root/'samples/clear-analysis.json').read_text())
valid=copy.deepcopy(original)
valid['questions']=[]
valid['mappings'].append(dict(label='E',meaning='Parça numarası',evidence='Synthetic fixture for testing only',confidence='high',nominalMm=None,toleranceText=None,valueText='11-30-10'))
cases=[('valid',valid,True),('missing_E',original,False)]
def mutation(name,fn):
 d=copy.deepcopy(valid);fn(d);cases.append((name,d,False))
mutation('duplicate',lambda d:d['mappings'].append(copy.deepcopy(d['mappings'][0])))
mutation('nominal',lambda d:d['mappings'][0].update(nominalMm=228))
mutation('tolerance_sign',lambda d:d['mappings'][2].update(toleranceText='+0,1/+0,0'))
mutation('missing_tolerance',lambda d:d['mappings'][0].pop('toleranceText'))
mutation('text',lambda d:d['mappings'][-1].update(valueText='11-30-12'))
mutation('text_as_dimension',lambda d:d['mappings'][-1].update(nominalMm=11))
mutation('reference',lambda d:d.update(reference='wrong'))
mutation('unknown_label',lambda d:d['mappings'].append(dict(label='Z')))
mutation('low_confidence',lambda d:d['mappings'][0].update(confidence='low'))
mutation('blocking_question',lambda d:d['questions'].append(dict(question='Unknown',blocking=True)))
normalized=copy.deepcopy(valid);normalized['mappings'][0]['label']="'a'";normalized['mappings'][2]['toleranceText']='(+0.1|-0.0)'
cases.append(('normalization',normalized,True))
with tempfile.TemporaryDirectory(prefix='analysis-tests-') as tmp:
 for name,data,expected in cases:
  source=pathlib.Path(tmp)/'input.json';report=pathlib.Path(tmp)/'report.json'
  source.write_text(json.dumps(data))
  r=subprocess.run([dotnet,str(root/'src/bin/Debug/net8.0/DrawingTool.dll'),'validate-analysis',str(root/'samples/taslak1.xlsx'),'11-30-10',str(source),str(report)],capture_output=True,text=True)
  assert r.returncode==(0 if expected else 1),(name,r.stdout,r.stderr)
  assert json.loads(report.read_text())['Passed']==expected,name
  print('PASS',name)
print(f'{len(cases)} offline checks passed')
