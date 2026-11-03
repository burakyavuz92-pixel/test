"""Explicit final-body measurement references for contract revision 2."""
import numpy as np
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Torus
from face_edge_selector import matches,unit

def validate(recipe):
    revision=recipe.get('contractRevision')
    if revision is None:return
    if revision!=2:raise ValueError('Unsupported contract revision')
    for feature in recipe['geometry']['features']:
        if feature['op'] in ('fillet','chamfer'):
            for selector in feature['selectors']:
                if set(selector) != {'faces'} or len(selector['faces']) != 2:
                    raise ValueError('Revision 2 edge selection requires exactly two support faces')
    for dim in recipe['drawing']['dimensions']:
        source=dim['valueSource']; marker=dim.get('sourceLabel')
        if not marker or source['kind']=='column' and marker!=source['column']:
            raise ValueError('Dimension sourceLabel must preserve its Excel column')
        if source['kind']=='constant':
            try: numeric=float(marker.removeprefix('R').replace(',','.'))
            except ValueError: raise ValueError('Constant dimension requires a numeric sourceLabel')
            if abs(numeric-source['value'])>1e-7: raise ValueError('Constant marker/value mismatch')
        relation=dim.get('relation',{});kind=relation.get('kind')
        supported={'diameter':('diameter',1),'planeDistance':('distance',2),'wallThickness':('thickness',2),'radius':('radius',1),'axisDistance':('distance',2)}
        if kind not in supported or dim['type']!=supported[kind][0] or len(relation.get('surfaces',[]))!=supported[kind][1]:
            raise ValueError('Unsupported explicit measurement relation')
    if recipe['drawing'].get('geometricTolerances'):
        raise ValueError('Revision 2 geometric tolerances are not implemented')

def surface_matches(face,spec):
    if spec['kind']!='torus': return matches(face,spec)
    s=BRepAdaptor_Surface(face)
    if s.GetType()!=GeomAbs_Torus:return False
    t=s.Torus();p=t.Location();d=t.Axis().Direction()
    return np.linalg.norm(np.array([p.X(),p.Y(),p.Z()])-spec['center'])<1e-5 and abs(abs(np.dot(unit(spec['axisDirection']),[d.X(),d.Y(),d.Z()]))-1)<1e-7 and abs(t.MajorRadius()-spec['majorRadius'])<1e-5 and abs(t.MinorRadius()-spec['minorRadius'])<1e-5

def resolve(shape,relation):
    specs=relation['surfaces']
    for spec in specs:
        if spec.get('kind')=='datumAxis':
            if relation['kind']!='axisDistance' or spec.get('axisOrigin')!=[0,0,0] or spec.get('axisDirection')!=[0,0,1]:raise ValueError('Only world Z datum axis is supported')
            continue
        vector=spec.get('normal',spec.get('axisDirection'))
        if vector is None or not np.isfinite(vector).all() or abs(np.linalg.norm(vector)-1)>1e-7:raise ValueError('Surface direction must be a finite unit vector')
        for name in ('radius','majorRadius','minorRadius'):
            if name in spec and (not np.isfinite(spec[name]) or spec[name]<=0):raise ValueError('Surface radius must be positive and finite')
        count=0;ex=TopExp_Explorer(shape,TopAbs_FACE)
        while ex.More():
            if surface_matches(TopoDS.Face_s(ex.Current()),spec):count+=1
            ex.Next()
        if count!=1:raise ValueError('Measurement surface must uniquely match final body; found '+str(count))
    k=relation['kind'];a=specs[0]
    if k=='diameter':
        if a['kind']!='cylinder':raise ValueError('Diameter requires cylinder')
        return 2*a['radius']
    if k=='radius':
        if a['kind']!='torus':raise ValueError('Radius requires torus')
        return a['minorRadius']
    b=specs[1]
    if k=='axisDistance':
        if a['kind'] not in ('cylinder','datumAxis') or b['kind'] not in ('cylinder','datumAxis') or a['kind']==b['kind']=='datumAxis':raise ValueError('Axis distance requires cylindrical reference')
        direction=unit(relation['direction'])
        for surface in specs:
            if abs(np.dot(direction,unit(surface['axisDirection'])))>1e-7:raise ValueError('Measurement direction must be perpendicular to axes')
        if abs(abs(np.dot(unit(a['axisDirection']),unit(b['axisDirection'])))-1)>1e-7:raise ValueError('Axes must be parallel')
        return abs(np.dot(np.array(a['axisOrigin'])-b['axisOrigin'],direction))
    if k=='planeDistance':
        if a['kind']!='plane' or b['kind']!='plane':raise ValueError('Distance requires planes')
        dot=np.dot(unit(a['normal']),unit(b['normal']))
        if abs(abs(dot)-1)>1e-7:raise ValueError('Distance planes must be parallel')
        return abs(a['offset']-np.sign(dot)*b['offset'])
    if a['kind']!='cylinder' or b['kind']!='cylinder':raise ValueError('Wall requires cylinders')
    axis=unit(a['axisDirection'])
    if abs(abs(np.dot(axis,unit(b['axisDirection'])))-1)>1e-7 or np.linalg.norm(np.cross(np.array(a['axisOrigin'])-b['axisOrigin'],axis))>1e-5:raise ValueError('Wall cylinders must be coaxial')
    return abs(a['radius']-b['radius'])
