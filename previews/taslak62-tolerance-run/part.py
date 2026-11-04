import cadquery as cq

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
