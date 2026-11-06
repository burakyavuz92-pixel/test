import math
import cadquery as cq

NECK_LEN = 5.0
TAPER_LEN = 3.0
EDGE_RADIUS = 5.0
EDGE_INSET = 1.0

def _num(p, key):
    v = p.get(key)
    if v is None:
        return None
    return float(v)

def _read(p):
    vals = {}
    for k in ['A', 'B', 'C', 'D', 'E', 'L']:
        v = _num(p, k)
        if v is None:
            return None, 'eksik olcu: ' + k
        vals[k] = v
    ang = _num(p, 'E__angleDeg')
    if ang is None:
        return None, 'cizim acisi eksik'
    vals['ANG'] = ang
    return vals, None

def build_part(p):
    v, err = _read(p)
    if err:
        return {'error': err}
    A = v['A']
    B = v['B']
    C = v['C']
    D = v['D']
    E = v['E']
    L = v['L']
    ang = v['ANG']
    if min(A, B, C, D, E, L) <= 0 or not (0.0 < ang < 90.0):
        return {'error': 'olcu degerleri gecersiz'}
    axial = E
    radial = E * math.tan(math.radians(ang))
    if radial >= A / 2.0:
        return {'error': 'pah kirma boyutu cok buyuk'}
    zs = -(B - NECK_LEN - TAPER_LEN)
    zn = -(B - NECK_LEN)
    if -zs <= axial:
        return {'error': 'govde boyu yetersiz'}
    Rh = L / 2.0
    rc = Rh - EDGE_RADIUS
    rr = Rh - EDGE_INSET - rc
    if rc <= 0 or rr < 0 or rr >= EDGE_RADIUS:
        return {'error': 'kafa capi uyumsuz'}
    zt = -(B + D)
    dz = math.sqrt(EDGE_RADIUS ** 2 - rr ** 2)
    zc = zt + dz
    ud = -B - zc
    if abs(ud) >= EDGE_RADIUS:
        return {'error': 'kafa kalinligi uyumsuz'}
    ru = rc + math.sqrt(EDGE_RADIUS ** 2 - ud ** 2)
    if ru <= C / 2.0:
        return {'error': 'kafa ile boyun uyumsuz'}
    prof = (
        cq.Workplane('XY')
        .moveTo(0.0, 0.0)
        .lineTo(A / 2.0 - radial, 0.0)
        .lineTo(A / 2.0, -axial)
        .lineTo(A / 2.0, zs)
        .lineTo(C / 2.0, zn)
        .lineTo(C / 2.0, -B)
        .lineTo(ru, -B)
        .threePointArc((Rh, zc), (Rh - EDGE_INSET, zt))
        .lineTo(0.0, zt)
        .close()
    )
    body = prof.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    return body.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
