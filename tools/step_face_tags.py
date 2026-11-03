"""Named STEP faces via XDE. No geometry or face indices are rewritten."""
import math,os,tempfile
from pathlib import Path
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_LabelSequence
from OCP.STEPCAFControl import STEPCAFControl_Writer,STEPCAFControl_Reader
from OCP.Interface import Interface_Static
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from face_edge_selector import matches

def props(shape,surface=False):
 p=GProp_GProps()
 (BRepGProp.SurfaceProperties_s if surface else BRepGProp.VolumeProperties_s)(shape,p)
 c=p.CentreOfMass();return p.Mass(),[c.X(),c.Y(),c.Z()]

def select(shape,tag):
 if tag.get('unresolved'):raise ValueError(tag['unresolved'])
 point=tag['point']
 if len(point)!=3 or not all(math.isfinite(v) for v in point):raise ValueError('Invalid face point')
 result=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  f=TopoDS.Face_s(ex.Current())
  if matches(f,tag['surface']):
   d=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex(),f);d.Perform()
   if d.IsDone() and d.Value()<1e-5:result.append(f)
  ex.Next()
 if len(result)!=1:raise ValueError('Face tag must select exactly one trimmed face; found '+str(len(result)))
 return result[0]

def read_tags(path,names):
 doc=TDocStd_Document(TCollection_ExtendedString('BinXCAF'));r=STEPCAFControl_Reader();r.SetNameMode(True);Interface_Static.SetIVal_s('read.stepcaf.subshapes.name',1)
 if r.ReadFile(str(path))!=IFSelect_RetDone or not r.Transfer(doc):raise ValueError('Named STEP read failed')
 tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());roots=TDF_LabelSequence();tool.GetFreeShapes(roots);found={}
 for i in range(1,roots.Length()+1):
  subs=TDF_LabelSequence();tool.GetSubShapes_s(roots.Value(i),subs)
  for j in range(1,subs.Length()+1):
   label=subs.Value(j);a=TDataStd_Name()
   if label.FindAttribute(TDataStd_Name.GetID_s(),a):
    name=a.Get().ToExtString()
    if name in names:
     if name in found:raise ValueError('Duplicate STEP face name')
     shape=tool.GetShape_s(label)
     if shape.ShapeType()!=TopAbs_FACE:raise ValueError('Tag was not restored as a face')
     found[name]=shape
 return found

def write_named(shape,tags,path):
 names=[t['name'] for t in tags]
 if any(not isinstance(n,str) or not n.strip() or len(n)>128 or any(ord(c)<32 for c in n) for n in names) or len(set(names))!=len(names):raise ValueError('Face names must be nonempty and unique')
 selected={t['name']:select(shape,t) for t in tags}
 if any(a.IsSame(b) for i,a in enumerate(selected.values()) for b in list(selected.values())[i+1:]):raise ValueError('Multiple names on the same face are not supported')
 doc=TDocStd_Document(TCollection_ExtendedString('BinXCAF'));tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main());root=tool.AddShape(shape,False)
 for name,face in selected.items():
  label=tool.AddSubShape(root,face)
  if label.IsNull():raise ValueError('Face does not belong to STEP root')
  TDataStd_Name.Set_s(label,TCollection_ExtendedString(name))
 writer=STEPCAFControl_Writer();writer.SetNameMode(True);Interface_Static.SetIVal_s('write.stepcaf.subshapes.name',1)
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(suffix='.step',dir=path.parent);os.close(fd)
 try:
  if not writer.Transfer(doc) or writer.Write(tmp)!=IFSelect_RetDone:raise ValueError('Named STEP export failed')
  recovered=read_tags(tmp,names)
  if set(recovered)!=set(names):raise ValueError('STEP face names did not survive roundtrip')
  for name,f in selected.items():
   mass,center=props(f,True);m,c=props(recovered[name],True)
   if not math.isclose(mass,m,rel_tol=1e-7,abs_tol=1e-7) or math.dist(center,c)>1e-5:raise ValueError('STEP named face geometry changed')
  from OCP.STEPControl import STEPControl_Reader
  r=STEPControl_Reader()
  if r.ReadFile(tmp)!=IFSelect_RetDone:raise ValueError('STEP geometry read failed')
  r.TransferRoots();restored=r.OneShape()
  if not BRepCheck_Analyzer(restored).IsValid() or not math.isclose(props(shape)[0],props(restored)[0],rel_tol=1e-7):raise ValueError('Named STEP solid geometry mismatch')
  os.replace(tmp,path);return [{'name':n,'areaMm2':props(f,True)[0],'centroidMm':props(f,True)[1],'roundtripVerified':True} for n,f in selected.items()]
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
