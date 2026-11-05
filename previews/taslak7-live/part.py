import math
import cadquery as cq

# Fixed dimensions read from the drawing (not Excel columns)
COLLAR_LEN = 2.8   # [2,8] collar length beside the head
HEAD_LEN = 5.0     # [5] total head length (lip band + cone)
LIP_BAND = 1.0     # '1' cylindrical band at the head lip
END_DIA = 22.0     # Ø22 diameter at the cone end

# Chamfer convention: leg value is axial; radial leg = leg * tan(angle measured from axis).
# Z = -s, where s is distance from the left end face (origin).

def _num(p, key):
    v = p.get(key)
    return 0.0 if v is None else float(v)

def _angle(p, key, default=45.0):
    v = p.get(key)
    return float(default) if v is None else float(v)

def _chamfer_radial(p, key):
    v = _num(p, key)
    if v <= 0:
        return 0.0
    return v * math.tan(math.radians(_angle(p, key + '__angleDeg', 45.0)))

def _check(p):
    for k in ('A', 'C', 'E', 'K', 'L'):
        if _num(p, k) <= 0:
            return 'Temel ölçü ' + k + ' pozitif olmalı'
    D = _num(p, 'D')
    if D < 0 or D >= _num(p, 'C'):
        return 'Delik derinliği D, gövde boyu C değerinden küçük olmalı'
    if D > 0 and _num(p, 'B') <= 0:
        return 'Derinlik D var ama B çapı tanımsız'
    L = _num(p, 'L')
    if L <= END_DIA:
        return 'Kafa çapı L=' + format(L, 'g') + ' mm, 22 mm konik uçtan büyük olmalı'
    return None

def _profile(p):
    A = _num(p, 'A'); B = _num(p, 'B'); C = _num(p, 'C'); D = _num(p, 'D')
    E = _num(p, 'E'); K = _num(p, 'K'); L = _num(p, 'L')
    F = _num(p, 'F'); G = _num(p, 'G'); J = _num(p, 'J')
    Jr = _chamfer_radial(p, 'J')
    Fr = _chamfer_radial(p, 'F')
    Gr = _chamfer_radial(p, 'G')
    Ro = A / 2.0
    Rc = E / 2.0
    Rh = L / 2.0
    Re = END_DIA / 2.0
    Rk = K / 2.0
    Rb = B / 2.0
    s_lip = C + COLLAR_LEN
    s_cone = s_lip + LIP_BAND
    T = s_lip + HEAD_LEN
    pts = []
    # outer left chamfer J, body, collar, head lip, cone, right end face
    pts.append((Ro - Jr, 0.0))
    if J > 0:
        pts.append((Ro, J))
    pts.append((Ro, C))
    pts.append((Rc, C))
    pts.append((Rc, s_lip))
    pts.append((Rh, s_lip))
    pts.append((Rh, s_cone))
    pts.append((Re, T))
    # right-end internal chamfer G
    if G > 0:
        pts.append((Rk + Gr, T))
        pts.append((Rk, T - G))
    else:
        pts.append((Rk, T))
    # bore back toward left end
    if D > 0:
        pts.append((Rk, D))
        pts.append((Rb, D))
        if F > 0:
            pts.append((Rb, F))
            pts.append((Rb + Fr, 0.0))
        else:
            pts.append((Rb, 0.0))
    else:
        if F > 0:
            pts.append((Rk, F))
            pts.append((Rk + Fr, 0.0))
        else:
            pts.append((Rk, 0.0))
    out = []
    for r, s in pts:
        if not out or abs(out[-1][0] - r) > 1e-9 or abs(out[-1][1] - s) > 1e-9:
            out.append((r, s))
    while len(out) > 2 and abs(out[-1][0] - out[0][0]) < 1e-9 and abs(out[-1][1] - out[0][1]) < 1e-9:
        out.pop()
    return out

def build_part(p):
    err = _check(p)
    if err is not None:
        return {'error': err}
    pts = _profile(p)
    # XZ workplane: local x = global X (radius), local y = global Z
    wp = (cq.Workplane('XZ')
          .polyline([(r, -s) for r, s in pts])
          .close()
          .revolve(360, (0, 0, 0), (0, 1, 0)))
    return wp
