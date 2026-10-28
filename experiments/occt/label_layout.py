"""Deterministic placement of oriented text envelopes; no changes to dimensions."""
import math

def polygon(box,x,y,angle,pad=0):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    l,t,r,b=box;l-=pad;t-=pad;r+=pad;b+=pad
    return [(x+u*c-v*s,y+u*s+v*c) for u,v in [(l,t),(r,t),(r,b),(l,b)]]

def overlap(a,b):
    for points in (a,b):
        for p,q in zip(points,points[1:]+points[:1]):
            axis=(-(q[1]-p[1]),q[0]-p[0]);pa=[x*axis[0]+y*axis[1] for x,y in a];pb=[x*axis[0]+y*axis[1] for x,y in b]
            if max(pa)<min(pb) or max(pb)<min(pa):return False
    return True

def hits_segment(poly,p,q):
    # Segment versus convex polygon, including endpoints inside.
    sign=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        cross=lambda v:(b[0]-a[0])*(v[1]-a[1])-(b[1]-a[1])*(v[0]-a[0])
        u,v=cross(p),cross(q);sign.append(u)
        if u*v<=0:
            dx,dy=q[0]-p[0],q[1]-p[1];ex,ey=b[0]-a[0],b[1]-a[1];den=dx*ey-dy*ex
            if abs(den)>1e-9:
                t=((a[0]-p[0])*ey-(a[1]-p[1])*ex)/den;w=((a[0]-p[0])*dy-(a[1]-p[1])*dx)/den
                if 0<=t<=1 and 0<=w<=1:return True
    for pt in (p,q):
        values=[(b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0]) for a,b in zip(poly,poly[1:]+poly[:1])]
        if all(v>=0 for v in values) or all(v<=0 for v in values):return True
    return False

class LabelLayout:
    def __init__(self,bounds):self.bounds=bounds;self.segments=[];self.labels=[];self.records=[]
    def segment(self,p,q):self.segments.append((p,q))
    def clear(self,poly,leader=None):
        l,t,r,b=self.bounds
        if any(not(l<=x<=r and t<=y<=b) for x,y in poly):return False
        if any(overlap(poly,old) for old in self.labels):return False
        if any(hits_segment(poly,p,q) for p,q in self.segments):return False
        if leader and (hits_segment(poly,*leader) or any(hits_segment(old,*leader) for old in self.labels)):return False
        return True
    def choose(self,id,box,candidates):
        for index,(x,y,angle,leader) in enumerate(candidates):
            poly=polygon(box,x,y,angle,3)
            if self.clear(poly,leader):
                self.labels.append(poly)
                if leader:self.segment(*leader)
                self.records.append(dict(id=id,candidate=index,polygon=poly,clearance=3))
                return x,y,angle,leader
        raise ValueError('No collision-free dimension label placement: '+id)
