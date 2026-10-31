"""Data-only v9 lowering. No model code or Python eval is executed."""
import ast,json,math,re,sys,copy

class Expressions:
 def __init__(self,cells,variables):
  self.cells=cells;self.vars=variables;self.cache={};self.stack=set()
  if set(cells)&set(variables):raise ValueError('Variable shadows column')
 def name(self,k):
  if k in self.cells:return self.cells[k].get('nominalMm')
  if k in self.cache:return self.cache[k]
  if k not in self.vars:raise ValueError('Unknown variable '+k)
  if k in self.stack:raise ValueError('Cyclic variable '+k)
  self.stack.add(k)
  try:self.cache[k]=self.value(self.vars[k]);return self.cache[k]
  finally:self.stack.remove(k)
 def value(self,x):
  if not isinstance(x,str) or not x.startswith('='):return x
  if len(x)>4096:raise ValueError('Expression too long')
  text=re.sub(r'\bif\s*\(','choose(',x[1:]);text=re.sub(r'\btrue\b','True',text);text=re.sub(r'\bfalse\b','False',text);text=re.sub(r'\bnull\b','None',text)
  tree=ast.parse(text,mode='eval')
  if sum(1 for _ in ast.walk(tree))>512:raise ValueError('Expression too complex')
  def walk(n):
   if isinstance(n,ast.Constant) and (n.value is None or type(n.value) in (int,float,bool)):return n.value
   if isinstance(n,ast.Name):return self.name(n.id)
   if isinstance(n,ast.BoolOp):
    for a in n.values:
     v=walk(a)
     if type(v)!=bool:raise ValueError('Boolean operand required')
     if isinstance(n.op,ast.And) and not v:return False
     if isinstance(n.op,ast.Or) and v:return True
    return v
   if isinstance(n,ast.UnaryOp):
    a=walk(n.operand)
    if isinstance(n.op,ast.Not):
     if type(a)!=bool:raise ValueError('Boolean required')
     return not a
    if type(a) not in (int,float):raise ValueError('Numeric operand required')
    return -a if isinstance(n.op,ast.USub) else +a if isinstance(n.op,ast.UAdd) else fail()
   if isinstance(n,ast.BinOp):
    a,b=walk(n.left),walk(n.right)
    if type(a) not in (int,float) or type(b) not in (int,float):raise ValueError('Blank/non-numeric arithmetic')
    if isinstance(n.op,ast.Add):return a+b
    if isinstance(n.op,ast.Sub):return a-b
    if isinstance(n.op,ast.Mult):return a*b
    if isinstance(n.op,ast.Div):return a/b
   if isinstance(n,ast.Compare) and len(n.ops)==1:
    a,b=walk(n.left),walk(n.comparators[0]);op=n.ops[0]
    if isinstance(op,ast.Eq):return a==b
    if isinstance(op,ast.NotEq):return a!=b
    if a is None or b is None:raise ValueError('Blank ordering')
    if isinstance(op,ast.Lt):return a<b
    if isinstance(op,ast.LtE):return a<=b
    if isinstance(op,ast.Gt):return a>b
    if isinstance(op,ast.GtE):return a>=b
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and not n.keywords:
    f=n.func.id
    if f=='choose' and len(n.args)==3:
     condition=walk(n.args[0])
     if type(condition)!=bool:raise ValueError('if condition must be boolean')
     return walk(n.args[1] if condition else n.args[2])
    if f=='isblank' and len(n.args)==1:return walk(n.args[0]) is None
    arity={'sqrt':1,'abs':1,'min':2,'max':2,'sin':1,'cos':1}
    if f in arity and len(n.args)==arity[f]:
     args=[walk(a) for a in n.args]
     if any(type(a) not in (int,float) for a in args):raise ValueError('Numeric function argument required')
     return {'sqrt':math.sqrt,'abs':abs,'min':min,'max':max,'sin':lambda a:math.sin(math.radians(a)),'cos':lambda a:math.cos(math.radians(a))}[f](*args)
   raise ValueError('Unsupported expression')
  result=walk(tree.body)
  if type(result) in (int,float) and not math.isfinite(result):raise ValueError('Non-finite expression')
  return result
 def bind(self,x):
  if isinstance(x,dict):return {k:self.bind(v) for k,v in x.items()}
  if isinstance(x,list):return [self.bind(v) for v in x]
  return self.value(x)

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(a,b):return [x+y for x,y in zip(a,b)]
def mul(a,b):return [x*b for x in a]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(a):
 if len(a)!=3 or not all(type(x) in (int,float) and math.isfinite(x) for x in a):raise ValueError('Invalid vector')
 n=math.sqrt(dot(a,a))
 if n<1e-12:raise ValueError('Zero direction')
 return mul(a,1/n)

def compile_recipe(recipe,cells,output_id):
 if recipe.get('schemaVersion')!=9:raise ValueError('Expected v9')
 g=recipe['geometry'];e=Expressions(cells,g.get('variables',{}));ops=[];frames=[];aliases={};applied={};current=None
 ids=[f['id'] for f in g['features']]
 if len(set(ids))!=len(ids) or any(i.startswith('__v9') for i in ids):raise ValueError('Duplicate/reserved feature ID')
 def emit(kind,args,frame='world',inputs=None,target=None,tool=None,id=None):
  id=id or '__v9_'+str(len(ops));ops.append(dict(id=id,op=kind,args=args,frame=frame,inputs=inputs or [],target=target,tool=tool,featureApplied=True));applied[id]=True;return id
 frames.append(dict(id='world',origin=[0,0,0],xAxis=[1,0,0],zAxis=[0,0,1]))
 def shape(s,transform):
  kind=s['kind'];point,vector=transform
  if kind=='cylinder':
   if s['diameter']<=0 or s['length']<=0:raise ValueError('Positive cylinder dimensions required')
   return emit('cylinder',dict(diameter=s['diameter'],length=s['length'],origin=point(s['origin']),direction=unit(vector(s['direction']))))
  if kind=='box':
   a,b,h=s['size']
   if min(a,b,h)<=0:raise ValueError('Positive box sizes required')
   s=dict(kind='extrude',profile=dict(frame=s.get('frame'),outer=dict(kind='polyline',points=[[0,0],[a,0],[a,b],[0,b]],closed=True)),extent=dict(from_=0,to=h));s['extent']['from']=s['extent'].pop('from_');kind='extrude'
  if kind not in ('extrude','revolve'):raise ValueError('Unsupported shape '+kind)
  p=s['profile'];f=p.get('frame') or dict(origin=[0,0,0],u=[1,0,0],v=[0,1,0]);u=unit(vector(f['u']));v=unit(vector(f['v']))
  if abs(dot(u,v))>1e-7:raise ValueError('Nonperpendicular profile frame')
  z=cross(u,v);origin=point(f['origin']);extent=s.get('extent')
  if kind=='extrude' and extent!='throughAll':
   if extent['to']<=extent['from']:raise ValueError('Extrusion extent must increase')
   origin=add(origin,mul(z,extent['from']))
  frame='__v9_frame_'+str(len(frames));frames.append(dict(id=frame,origin=origin,xAxis=u,zAxis=z))
  profile=emit('sketch',dict(plane='XY',loops=[p['outer']]+p.get('holes',[]),profileHoles=True),frame)
  if kind=='extrude':
   if extent=='throughAll':
    if current is None:raise ValueError('throughAll requires current body')
    return emit('throughExtrude',dict(direction=[0,0,1]),frame,[profile],target=current)
   return emit('extrude',dict(length=extent['to']-extent['from'],direction=[0,0,1]),frame,[profile])
  axis_point=point(s['axisOrigin']);d=unit(vector(s['axisDirection']));local=lambda a:[dot(a,u),dot(a,v),dot(a,z)]
  return emit('revolve',dict(axisOrigin=local(add(axis_point,mul(origin,-1))),axisDirection=local(d),angleDeg=s['angleDeg']),frame,[profile])
 def placement(inst,i):
  if not inst:return lambda p:p,lambda v:v
  if inst['kind']=='linear':return lambda p:add(p,mul(inst['step'],i)),lambda v:v
  if inst['kind']!='polar':raise ValueError('Unknown instances')
  axis=unit(inst['axisDirection']);o=inst['axisOrigin'];theta=math.radians(inst['startAngleDeg']+i*inst['stepAngleDeg'])
  def rotate(v):return add(add(mul(v,math.cos(theta)),mul(cross(axis,v),math.sin(theta))),mul(axis,dot(axis,v)*(1-math.cos(theta))))
  return lambda p:add(o,rotate(add(p,mul(o,-1)))),rotate
 for f in g['features']:
  id=f['id'];active=e.value(f.get('when',True))
  if type(active)!=bool:raise ValueError('Feature when must be boolean')
  applied[id]=active
  if not active:continue
  op=f['op']
  if op in ('add','cut'):
   if current is None and op!='add':raise ValueError('First operation must add')
   s=e.bind(f['shape']);inst=e.bind(f.get('instances'));n=inst['count'] if inst else 1
   if type(n) not in (int,float) or n!=int(n) or n<1 or n>1000:raise ValueError('Invalid instance count')
   tools=[shape(s,placement(inst,i)) for i in range(int(n))];aliases[id]=tools
   tool=tools[0] if n==1 else emit('fuse',{},inputs=tools)
   if current is None:
    # Explicit alias preserves public operation IDs without copying shape construction.
    emit('alias',{},inputs=[tool],id=id)
   else:emit('join' if op=='add' else 'cut',{},inputs=[tool] if op=='add' else [],target=current,tool=tool if op=='cut' else None,id=id)
   current=id
  elif op in ('fillet','chamfer'):
   if current is None:raise ValueError('Edge operation needs body')
   selectors=e.bind(f['selectors'])
   for sel in selectors:
    sel.setdefault('operation',current);sel.setdefault('role','edge')
   emit(op,dict(size=e.value(f['size']),selectors=selectors),target=current,id=id);current=id
  else:raise ValueError('Unknown feature op '+op)
 if current is None:raise ValueError('No active body')
 d=copy.deepcopy(recipe['drawing'])
 if d.pop('details',[]):raise ValueError('Detail views are not supported in the current contract')
 for key in ('dimensions','views','sections','geometricTolerances'):d.setdefault(key,[])
 dimensions=[];parameters={k:c.get('nominalMm') for k,c in cells.items()}
 for dim in d['dimensions']:
  if not e.value(dim.pop('when',True)):continue
  dim=e.bind(dim);src=dim['valueSource'];col=src.get('column')
  value=cells[col].get('nominalMm') if src['kind']=='column' else src['value']
  if value is None:raise ValueError('Active dimension uses blank cell')
  if any(t['operation'] not in applied for t in dim['targets']):raise ValueError('Unknown dimension target')
  for t in dim['targets']:
   if 'instance' in t and not 0<=t['instance']<len(aliases.get(t['operation'],[])):raise ValueError('Dimension instance out of range')
  if any(not applied[t['operation']] for t in dim['targets']):continue
  dim.update(nominal=value,parameter=col or dim['id'],unit=src.get('unit','mm'),quantity=dim.get('quantity',1))
  if col:dim['sourceMeasurement']=cells[col]
  color={'black':'#000000','green':'#008000','#000000':'#000000','#008000':'#008000'}.get(dim['sourceColor'].lower())
  if color is None:raise ValueError('Unsupported annotation source color')
  dim['canonicalSourceColor']=color
  dim['effectiveVisible']=dim.get('visible',True) and color=='#000000' and not(dim.get('hideIf',{}).get('kind')=='zero' and value==0)
  dimensions.append(dim)
 d['dimensions']=dimensions
 def ref(r):
  if r['feature'] not in applied:raise ValueError('Unknown section feature')
  if not applied[r['feature']]:return r
  candidates=aliases.get(r['feature'])
  if not candidates:raise ValueError('Section reference has no construction shape')
  index=r.get('instance',0)
  if index<0 or index>=len(candidates):raise ValueError('Section instance out of range')
  return dict(feature=candidates[index],entity=r['entity'])
 for sec in d['sections']:
  if sec['kind']=='featureTrace':sec['main']=ref(sec['main']);sec['through']=[ref(r) for r in sec['through']]
  else:sec['frame']='world'
 for view in d['views']:
  n=unit(view['direction']);up=unit(view['up'])
  if abs(dot(n,up))>.999999:raise ValueError('Parallel view vectors')
  view['direction']=n;view['up']=up
 view_ids=[v['id'] for v in d['views']]
 if len(view_ids)!=len(set(view_ids)):raise ValueError('Duplicate view ID')
 for sec in d['sections']:
  if sec['view'] not in view_ids or ('sourceView' in sec and sec['sourceView'] not in view_ids):raise ValueError('Unknown section view')
 d['sections']=e.bind(d['sections']);d['geometricTolerances']=e.bind(d['geometricTolerances'])
 return dict(schemaVersion=7,outputId=output_id,geometry=dict(parameters=parameters,frames=frames,operations=ops,result=current,featureApplied=applied),drawing=d,executionStatus='recipe-resolved-not-rendered')

if __name__=='__main__':
 try:
  request=json.load(sys.stdin);json.dump(compile_recipe(request['recipe'],request['cells'],request['outputId']),sys.stdout,allow_nan=False)
 except Exception as ex:print(str(ex),file=sys.stderr);sys.exit(1)
