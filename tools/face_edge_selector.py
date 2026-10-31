"""Resolve a boundary edge from its two incident analytic support surfaces."""
import math
import numpy as np
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane,GeomAbs_Cylinder


def unit(v):
    a=np.asarray(v,dtype=float)
    if a.shape!=(3,) or not np.isfinite(a).all() or np.linalg.norm(a)<1e-12:raise ValueError('Invalid surface direction')
    return a/np.linalg.norm(a)


def matches(face,spec):
    surface=BRepAdaptor_Surface(face)
    if spec['kind']=='plane':
        if surface.GetType()!=GeomAbs_Plane:return False
        plane=surface.Plane();n=unit(spec['normal']);axis=plane.Axis().Direction();p=plane.Location()
        return abs(abs(np.dot(n,[axis.X(),axis.Y(),axis.Z()]))-1)<1e-7 and abs(np.dot(n,[p.X(),p.Y(),p.Z()])-spec['offset'])<1e-5
    if spec['kind']=='cylinder':
        if surface.GetType()!=GeomAbs_Cylinder:return False
        c=surface.Cylinder();d=unit(spec['axisDirection']);axis=c.Axis().Direction();p=c.Location()
        delta=np.asarray([p.X(),p.Y(),p.Z()])-np.asarray(spec['axisOrigin'])
        return abs(c.Radius()-spec['radius'])<1e-5 and abs(abs(np.dot(d,[axis.X(),axis.Y(),axis.Z()]))-1)<1e-7 and np.linalg.norm(np.cross(delta,d))<1e-5
    raise ValueError('Unsupported support surface '+str(spec['kind']))


def edges(face):
    result=[];ex=TopExp_Explorer(face,TopAbs_EDGE)
    while ex.More():result.append(TopoDS.Edge_s(ex.Current()));ex.Next()
    return result


def select_edge(shape,specs):
    if len(specs)!=2:raise ValueError('Exactly two support surfaces required')
    groups=[[],[]];ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        face=TopoDS.Face_s(ex.Current())
        for i,spec in enumerate(specs):
            if matches(face,spec):groups[i].append(face)
        ex.Next()
    result=[]
    for a in groups[0]:
        for b in groups[1]:
            if a.IsSame(b):continue
            for ea in edges(a):
                if any(ea.IsSame(eb) for eb in edges(b)) and not any(ea.IsSame(e) for e in result):result.append(ea)
    if len(result)!=1:raise ValueError('Support surfaces must identify one shared edge; found '+str(len(result)))
    return result[0]
