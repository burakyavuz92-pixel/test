import math
import cadquery as cq

COLLAR_TOTAL_MM = 5.0
LAND_MM = 1.0


def _val(p, key):
    v = p.get(key)
    if v is None:
        return None
    return float(v)


def _dims(p):
    out = {}
    for k in ['A', 'B', 'C', 'D', 'E', 'J', 'K', 'L', 'M', 'N']:
        v = _val(p, k)
        if v is None:
            return None
        out[k] = v
    return out


def _leg(p, key):
    leg = _val(p, key)
    if leg is None:
        return None, None
    if leg == 0.0:
        return 0.0, 0.0
    ang = p.get(key + '__angleDeg')
    if ang is None:
        return None, None
    return leg, leg * math.tan(math.radians(float(ang)))


def _profile(p):
    v = _dims(p)
    if v is None:
        return None, 'eksik ölçü'
    fl, fr = _leg(p, 'F')
    gl, gr = _leg(p, 'G')
    jl, jr = _leg(p, 'J')
    if fl is None or gl is None or jl is None:
        return None, 'açı verisi eksik'
    RA = v['A'] / 2.0
    RB = v['B'] / 2.0
    RK = v['K'] / 2.0
    RE = v['E'] / 2.0
    RL = v['L'] / 2.0
    RN = v['N'] / 2.0
    C = v['C']
    D = v['D']
    M = v['M']
    if C <= 0 or M <= 0 or D < 0:
        return None, 'ölçü değerleri geçersiz'
    if D > 0 and fl >= D:
        return None, 'kademe derinliği yetersiz'
    bore_left = RB if D > 0 else RK
    if RA - jr <= bore_left + fr:
        return None, 'duvar kalınlığı yetersiz'
    if RN <= RK + gr or RL <= RN:
        return None, 'kollar çapı geçersiz'
    zC = -C
    zM = -(C + M)
    zL = zM - LAND_MM
    zE = -(C + M + COLLAR_TOTAL_MM)
    pts = []
    pts.append((bore_left + fr, 0.0))
    pts.append((bore_left, -fl))
    if D > 0:
        pts.append((RB, -D))
        pts.append((RK, -D))
    if gl > 0:
        pts.append((RK, zE + gl))
        pts.append((RK + gr, zE))
    else:
        pts.append((RK, zE))
    pts.append((RN, zE))
    pts.append((RL, zL))
    pts.append((RL, zM))
    pts.append((RE, zM))
    pts.append((RE, zC))
    pts.append((RA, zC))
    pts.append((RA, -jl))
    pts.append((RA - jr, 0.0))
    return pts, None


def _build(p):
    pts, err = _profile(p)
    if err is not None:
        return None, err
    try:
        wp = cq.Workplane('XZ').polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
        solid = wp.val()
        if (not solid.isValid()) or solid.Volume() <= 0:
            return None, 'geometri geçersiz'
    except Exception:
        return None, 'geometri oluşturulamadı'
    return wp, None


def build_part(p):
    wp, err = _build(p)
    if err is not None:
        return {'error': err}
    return wp


def build_face_tags(p):
    v = _dims(p)
    if v is None:
        return {'error': 'eksik ölçü'}
    z_shoulder = -(v['C'] + v['M'])
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': z_shoulder}}]
