import cadquery as cq
import math

FACE_D = 22.0
CONE_BIG_D = 25.0
CONE_LEN = 5.0
NECK_LEN = 2.8
CH = 1.0

def _need(p, key):
    v = p.get(key)
    if v is None:
        raise ValueError('missing ' + key)
    return float(v)

def _revolve(pts):
    pl = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    return cq.Workplane(pl).polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))

def build_part(p):
    A = _need(p, 'A')
    B = _need(p, 'B')
    C = _need(p, 'C')
    D = _need(p, 'D')
    E = _need(p, 'E')
    Ro = A / 2.0
    Rb = B / 2.0
    Rm = Rb + CH
    Rn = E / 2.0
    Rf = FACE_D / 2.0
    Rc = CONE_BIG_D / 2.0
    zc = -CONE_LEN
    zn = -(CONE_LEN + NECK_LEN)
    zl = zn - C
    L = -zl
    e = CH
    outer = [(0, 0), (Rf, 0), (Rc, zc), (Rn, zc), (Rn, zn), (Ro, zn),
             (Ro, zl + CH), (Ro - CH, zl), (0, zl)]
    if D >= L - 1e-9:
        void = [(0, zl - e), (Rm + CH + e, zl - e), (Rm + CH, zl), (Rm, zl + CH),
                (Rm, -CH), (Rm + CH, 0), (Rm + CH + e, e), (0, e)]
    else:
        zd = zl + D
        if D <= CH or zd > -CH:
            raise ValueError('thread depth incompatible with body')
        void = [(0, zl - e), (Rm + CH + e, zl - e), (Rm + CH, zl), (Rm, zl + CH),
                (Rm, zd), (Rb, zd), (Rb, -CH), (Rb + CH, 0), (Rb + CH + e, e), (0, e)]
    return _revolve(outer).cut(_revolve(void))

def _rec(rid, mid, source, kind, nominal, **geom):
    rec = {'id': rid, 'markerId': mid, 'source': source, 'kind': kind, 'nominal': float(nominal)}
    rec.update(geom)
    return rec

def build_measurements(p):
    A = _need(p, 'A')
    B = _need(p, 'B')
    C = _need(p, 'C')
    D = _need(p, 'D')
    E = _need(p, 'E')
    Ro = A / 2.0
    Rb = B / 2.0
    Rm = Rb + CH
    Rn = E / 2.0
    Rc = CONE_BIG_D / 2.0
    zc = -CONE_LEN
    zn = -(CONE_LEN + NECK_LEN)
    zl = zn - C
    zd = zl + D
    zm = (zc + zn) / 2.0
    L = -zl
    zax = [0.0, 0.0, 1.0]
    zdir = [0.0, 0.0, 1.0]
    recs = []
    recs.append(_rec('R-A', 'M-A', 'A', 'diameter', A,
                     center=[0.0, 0.0, (zl + zn) / 2.0], axis=zax, radius=Ro))
    if D >= L - 1e-9 or zd > -CH:
        recs.append(_rec('R-B', 'M-B', 'B', 'diameter', B,
                         unresolved='bore reference unavailable for this depth'))
    else:
        recs.append(_rec('R-B', 'M-B', 'B', 'diameter', B,
                         center=[0.0, 0.0, (zd - CH) / 2.0], axis=zax, radius=Rb))
    recs.append(_rec('R-C', 'M-C', 'C', 'distance', C,
                     p1=[Ro - CH, 0.0, zl], p2=[Ro, 0.0, zn], direction=zdir))
    recs.append(_rec('R-D', 'M-D', 'D', 'distance', D,
                     p1=[Rm + CH, 0.0, zl], p2=[Rm, 0.0, zd], direction=zdir))
    recs.append(_rec('R-E', 'M-E', 'E', 'distance', E,
                     p1=[0.0, Rn, zm], p2=[0.0, -Rn, zm], direction=[0.0, 1.0, 0.0]))
    recs.append(_rec('R-CH-L', 'M-CH-L', '1 X 45°', 'distance', CH,
                     p1=[Ro, 0.0, zl + CH], p2=[Ro - CH, 0.0, zl], direction=zdir))
    recs.append(_rec('R-CH-R', 'M-CH-R', '1 X 45°', 'distance', CH,
                     p1=[Rb, 0.0, -CH], p2=[Rb + CH, 0.0, 0.0], direction=zdir))
    recs.append(_rec('R-CONE', 'M-CONE', '25 ±0,5', 'diameter', CONE_BIG_D,
                     center=[0.0, 0.0, zc], axis=zax, radius=Rc))
    return recs
