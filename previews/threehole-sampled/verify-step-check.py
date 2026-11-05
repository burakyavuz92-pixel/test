import sys,json,math
from pathlib import Path
sys.path.insert(0,'tools')
import cadquery as cq
from step_face_tags import read_tags,props
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
root=Path(__file__).resolve().parent; reports=[]
for row in json.loads((root/'rows.json').read_text()):
 id=row['outputId'];p=row['parameters'];path=root/id/(id+'.step');shape=cq.importers.importStep(str(path)).val();bb=shape.BoundingBox();issues=[]
 for key,actual,expected in [('outer diameter X',bb.xlen,p['A']),('outer diameter Y',bb.ylen,p['A']),('depth',bb.zlen,p['J']),('closed end Z',bb.zmax,0),('open end Z',bb.zmin,-p['J'])]:
  if abs(actual-expected)>1e-4:issues.append([key,actual,expected])
 cylinders=[]
 for face in shape.Faces():
  surf=BRepAdaptor_Surface(face.wrapped)
  if surf.GetType()==GeomAbs_Cylinder:
   cyl=surf.Cylinder();o=cyl.Location();v=cyl.Axis().Direction()
   if abs(v.Z())>1-1e-6:cylinders.append((o.X(),o.Y(),cyl.Radius()))
 for label,x,y in [('C',0,p['B']-p['G']),('D',0,-p['G']),('E',-p['F'],0)]:
  if not any(math.dist((x,y,p[label]/2),c)<1e-4 for c in cylinders):issues.append(['hole '+label,x,y,p[label]/2])
 tags=read_tags(path,['montaj']);face=tags.get('montaj')
 if face is None:issues.append('missing montaj')
 else:
  surf=BRepAdaptor_Surface(TopoDS.Face_s(face));area,center=props(face,True)
  if surf.GetType()!=GeomAbs_Plane or abs(center[2]+3)>1e-5:issues.append(['wrong montaj plane',center])
  expected=math.pi*((p['A']/2-8)**2-sum((p[k]/2)**2 for k in ['C','D','E']))
  if not math.isclose(area,expected,abs_tol=1e-4):issues.append(['montaj area',area,expected])
 reports.append({'outputId':id,'passed':not issues,'issues':issues})
(root/'independent-step-check.json').write_text(json.dumps({'scope':'This sketch: bounding dimensions, all three cylindrical hole positions/radii, montaj inner plane and area; not a complete proof of every profile detail.','results':reports},indent=2))
print('Independent STEP checks:',sum(r['passed'] for r in reports),'/',len(reports));print([r for r in reports if not r['passed']])
