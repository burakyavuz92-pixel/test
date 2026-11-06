import math
import cadquery as cq

AXIS_DIR = [0.0, 0.0, 1.0]
CHAMFER_DEFAULT_ANGLE_DEG = 45.0

def _rec(rid, mid, src, kind, nominal, **fields):
    r = {'id': rid, 'markerId': mid, 'source': src, 'kind': kind, 'nominal': float(nominal)}
    r.update(fields)
    return r

def _distance(rid, mid, src, z1, z2, nominal):
    return _rec(rid, mid, src, 'distance', nominal, points=[[0.0, 0.0, float(z1)], [0.0, 0.0, float(z2)]], direction=list(AXIS_DIR))

def _diameter(rid, mid, src, zc, nominal):
    return _rec(rid, mid, src, 'diameter', nominal, center=[0.0, 0.0, float(zc)], axis=list(AXIS_DIR), radius=float(nominal) / 2.0)

def build_measurements(p):
    try:
        g = _layout(p)
    except ValueError as exc:
        return {'error': 'Olcu verisi gecersiz: ' + str(exc)}
    A = g['A']
    B = g['B']
    C = g['C']
    D = g['D']
    L = g['L']
    ch_ax = g['ch_ax']
    ch_rad = g['ch_rad']
    s1 = g['s1']
    taper = g['taper']
    neck_start = s1 + taper
    out = []
    out.append(_distance('rec-B', 'occ-B', 'B', 0.0, -B, B))
    out.append(_distance('rec-D', 'occ-D', 'D', -B, -(B + D), D))
    out.append(_distance('rec-neck-5', 'occ-neck-5', ' 5 ', -neck_start, -B, NECK_LEN))
    out.append(_diameter('rec-A', 'occ-A', 'A', -(ch_ax + s1) / 2.0, A))
    out.append(_diameter('rec-C', 'occ-C', 'C', -(neck_start + NECK_LEN / 2.0), C))
    out.append(_diameter('rec-L', 'occ-L', 'L', -(B + D / 2.0), L))
    if ch_ax > 0:
        ang = p.get('E__angleDeg')
        ang = CHAMFER_DEFAULT_ANGLE_DEG if ang is None else float(ang)
        out.append(_rec('rec-E', 'occ-E', 'E', 'chamfer', ch_ax, points=[[0.0, A / 2.0 - ch_rad, 0.0], [0.0, A / 2.0, -ch_ax]], direction=[0.0, 0.0, 1.0], angleDeg=ang))
    else:
        out.append({'id': 'rec-E', 'markerId': 'occ-E', 'source': 'E', 'kind': 'chamfer', 'nominal': 0.0, 'unresolved': 'Pah olcusu sifir oldugu icin pah yok'})
    return out
