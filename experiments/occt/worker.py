"""Local OCCT experiment; JSON in, validated STEP/STL plus VTK-rendered JPEG out. No network calls."""
import argparse,json,math,pathlib,os,sys
from OCP.gp import gp_Pnt,gp_Ax1,gp_Ax2,gp_Dir
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol,BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
import vtk
from PIL import Image


def validate(data):
    a,depth,t,r=[float(data[k]) for k in ('outerDiameterMm','depthMm','thicknessMm','outerRadiusMm')]
    if not all(math.isfinite(x) for x in (a,depth,t,r)) or not (a>2*r and depth>r>t>0):
        raise ValueError('Invalid profile dimensions')
    holes=data['holes']
    for i,h in enumerate(holes):
        x,y,d=[float(h[k]) for k in ('xMm','yMm','diameterMm')]
        if not all(math.isfinite(v) for v in (x,y,d)) or d<=0 or math.hypot(x,y)+d/2>=a/2-r:
            raise ValueError('Hole intersects bend or lies outside flat face')
        for other in holes[:i]:
            if math.hypot(x-other['xMm'],y-other['yMm'])<=(d+other['diameterMm'])/2:
                raise ValueError('Overlapping holes')
    return a,depth,t,r


def volume(shape):
    props=GProp_GProps();BRepGProp.VolumeProperties_s(shape,props);return props.Mass()


def build(data):
    a,depth,t,r=validate(data);R=a/2
    def pt(x,z):return gp_Pnt(x,0,-z)
    wire=BRepBuilderAPI_MakeWire()
    def line(x,z,u,v):wire.Add(BRepBuilderAPI_MakeEdge(pt(x,z),pt(u,v)).Edge())
    def arc(start,mid,end):wire.Add(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(pt(*start),pt(*mid),pt(*end)).Value()).Edge())
    line(0,0,R-r,0)
    # Outer R bend from flat closed face into cylindrical side.
    arc((R-r,0),(R-r+r/math.sqrt(2),r-r/math.sqrt(2)),(R,r))
    line(R,r,R,depth);line(R,depth,R-t,depth);line(R-t,depth,R-t,r)
    ri=r-t
    arc((R-t,r),(R-r+ri/math.sqrt(2),r-ri/math.sqrt(2)),(R-r,t))
    line(R-r,t,0,t);line(0,t,0,0)
    face=BRepBuilderAPI_MakeFace(wire.Wire()).Face()
    solid=BRepPrimAPI_MakeRevol(face,gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),2*math.pi,True).Shape()
    before=volume(solid)
    for h in data['holes']:
        tool=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(h['xMm'],h['yMm'],1),gp_Dir(0,0,-1)),h['diameterMm']/2,depth+2).Shape()
        cut=BRepAlgoAPI_Cut(solid,tool);cut.Build()
        if not cut.IsDone():raise RuntimeError('OCCT boolean cut failed')
        solid=cut.Shape()
    if not BRepCheck_Analyzer(solid).IsValid():raise RuntimeError('Invalid OCCT BRep')
    count=0;exp=TopExp_Explorer(solid,TopAbs_SOLID)
    while exp.More():count+=1;exp.Next()
    if count!=1:raise RuntimeError(f'Expected one solid, found {count}')
    actual=volume(solid);expected=before-sum(math.pi*(h['diameterMm']/2)**2*t for h in data['holes'])
    if not math.isclose(actual,expected,rel_tol=1e-7,abs_tol=1e-4):raise RuntimeError('Hole volume verification failed')
    return solid,dict(validBrep=True,solidCount=count,volumeMm3=actual,expectedVolumeMm3=expected,holeCount=len(data['holes']))


def render(stl,out,data):
    reader=vtk.vtkSTLReader();reader.SetFileName(str(stl));reader.MergingOn();reader.Update()
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SetFeatureAngle(50);normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.ScalarVisibilityOff()
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    prop=actor.GetProperty();prop.SetColor(.78,.77,.74);prop.SetInterpolationToPhong();prop.SetAmbient(.40);prop.SetDiffuse(.58);prop.SetSpecular(.15);prop.SetSpecularPower(35)
    renderer=vtk.vtkRenderer();renderer.SetBackground(1,1,1);renderer.AddActor(actor)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1400,1100);window.SetMultiSamples(4);window.AddRenderer(renderer)
    camera=renderer.GetActiveCamera();bounds=reader.GetOutput().GetBounds();center=[(bounds[i]+bounds[i+1])/2 for i in (0,2,4)]
    view=data.get('camera')
    if view is None:raise ValueError('Explicit camera required; no fixed isometric default')
    direction=view['direction'];up=view['up']
    if len(direction)!=3 or len(up)!=3 or view['projection']!='orthographic' or not all(math.isfinite(x) for x in direction+up):raise ValueError('Invalid camera')
    norm=math.sqrt(sum(v*v for v in direction));unorm=math.sqrt(sum(v*v for v in up))
    if norm<1e-8 or unorm<1e-8 or abs(sum(a*b for a,b in zip(direction,up)))/(norm*unorm)>.98:raise ValueError('Degenerate camera')
    camera.SetFocalPoint(*center);camera.SetPosition(*[c+300*d/norm for c,d in zip(center,direction)]);camera.SetViewUp(*up);camera.ParallelProjectionOn();renderer.ResetCamera();camera.Zoom(1.15)
    # True mesh silhouette and sharp feature edges. Depth testing hides occluded rear geometry.
    silhouette=vtk.vtkPolyDataSilhouette();silhouette.SetInputConnection(normals.GetOutputPort());silhouette.SetCamera(camera);silhouette.SetEnableFeatureAngle(1);silhouette.SetFeatureAngle(50)
    sm=vtk.vtkPolyDataMapper();sm.SetInputConnection(silhouette.GetOutputPort());sa=vtk.vtkActor();sa.SetMapper(sm);sa.GetProperty().SetColor(.12,.12,.12);sa.GetProperty().SetLineWidth(1.3);renderer.AddActor(sa)
    window.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update()
    png=out/'occt-preview.png';writer=vtk.vtkPNGWriter();writer.SetFileName(str(png));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    with Image.open(png) as im:
        from PIL import ImageChops
        rgb=im.convert('RGB');mask=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).convert('L').point(lambda x:255 if x>15 else 0)
        box=mask.getbbox()
        if box is None:raise RuntimeError('Render is blank')
        pad=24;box=(max(0,box[0]-pad),max(0,box[1]-pad),min(im.width,box[2]+pad),min(im.height,box[3]+pad))
        cropped=rgb.crop(box);cropped.save(png)
        rgb.save(out/'occt-preview.jpeg',quality=95,dpi=(150,150))
        extrema=im.convert('L').getextrema()
        if extrema[0]>180:raise RuntimeError('Render is blank')
    info={'camera':view,'windowClass':window.GetClassName(),'capabilities':window.ReportCapabilities(),'triangles':reader.GetOutput().GetNumberOfCells(),'meshBoundsMm':list(bounds)}
    window.Finalize();return info


def main():
    parser=argparse.ArgumentParser();parser.add_argument('request');parser.add_argument('output');args=parser.parse_args()
    out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise ValueError('Output directory must be empty')
    data=json.loads(pathlib.Path(args.request).read_text());solid,checks=build(data)
    step=STEPControl_Writer();step.Transfer(solid,STEPControl_AsIs)
    if step.Write(str(out/'plate.step'))!=IFSelect_RetDone:raise RuntimeError('STEP export failed')
    reload=STEPControl_Reader()
    if reload.ReadFile(str(out/'plate.step'))!=IFSelect_RetDone:raise RuntimeError('STEP reload failed')
    reload.TransferRoots();restored=reload.OneShape()
    if not BRepCheck_Analyzer(restored).IsValid() or not math.isclose(volume(restored),checks['volumeMm3'],rel_tol=1e-7):raise RuntimeError('STEP roundtrip verification failed')
    checks['stepRoundtrip']=True
    BRepMesh_IncrementalMesh(solid,.08,False,.08,True).Perform();stl=StlAPI_Writer()
    if not stl.Write(solid,str(out/'plate.stl')):raise RuntimeError('STL export failed')
    os.environ.setdefault("MESA_SHADER_CACHE_DIR",str((out/"mesa-cache").resolve()))
    rendering=render(out/'plate.stl',out,data)
    drawing=None
    if 'drawing' in data:
        from technical_sheet import write_sheet
        drawing=write_sheet(solid,data,out)
    (out/'result.json').write_text(json.dumps({'backend':'OCCT via OCP / VTK','input':data,'checks':checks,'rendering':rendering,'drawing':drawing,'networkCalls':0,'limits':['Experimental model, not approved drawing','Inner radius = outer radius minus thickness','Offscreen mesh rendering; 0.08 mm meshing tolerance','Windows packaging not yet tested']},indent=2))
    print('OCCT prototype complete: '+str(out/'occt-preview.jpeg'))

if __name__=='__main__':main()
