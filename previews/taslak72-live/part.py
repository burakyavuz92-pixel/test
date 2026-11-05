import math
import cadquery as cq

LAND_MM = 1.0
HEAD_MM = 5.0
EPS = 1e-9

def _err(msg):
    return {'error': msg}

def _chamfer(p, key):
    leg = p.get(key)
    if leg is None:
        return None
    leg = float(leg)
    if leg == 0.0:
        return (0.0, 0.0)
    ang = p.get(key + '__angleDeg')
    if ang is None:
        return None
    ang = float(ang)
    if ang <= 0.0 or ang >= 90.0:
        return None
    return (leg, leg * math.tan(math.radians(ang)))

def _params(p):
    for k in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'J', 'K', 'L', 'M', 'N']:
        if p.get(k) is None:
            return _err('Eksik ölçü: ' + k)
    A = float(p['A']); B = float(p['B']); C = float(p['C']); D = float(p['D'])
    E = float(p['E']); K = float(p['K']); L = float(p['L'])
    M = float(p['M']); N = float(p['N'])
    if min(A, B, C, E, K, L) <= 0.0 or min(D, M, N) < 0.0:
        return _err('Geçersiz ölçü değerleri')
    fc = _chamfer(p, 'F')
    gc = _chamfer(p, 'G')
    jc = _chamfer(p, 'J')
    if fc is None or gc is None or jc is None:
        return _err('Pah ölçüsü veya açısı eksik')
    F, Fr = fc
    G, Gr = gc
    J, Jr = jc
    total = C + M + HEAD_MM
    if N <= 0.0:
        return _err('Koni uç çapı sıfır, geçerli koni oluşmuyor')
    if N / 2.0 <= K / 2.0 + Gr + EPS:
        return _err('Koni ucu iç delik pahına yetmiyor')
    if D >= total:
        return _err('Sayac derinliği parça boyunu aşıyor')
    if D > 0.0 and F >= D:
        return _err('Sol pah sayac derinliğini aşıyor')
    Rl = B / 2.0 if D > 0.0 else K / 2.0
    if Rl + Fr >= A / 2.0 - Jr - EPS:
        return _err('Sol yüz genişliği kalmıyor')
    return {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'K': K, 'L': L, 'M': M, 'N': N,
            'F': F, 'Fr': Fr, 'G': G, 'Gr': Gr, 'J': J, 'Jr': Jr}

def _dedupe(pts):
    out = []
    for q in pts:
        if not out or abs(q[0] - out[-1][0]) > 1e-9 or abs(q[1] - out[-1][1]) > 1e-9:
            out.append(q)
    while len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out

def _points(v):
    A = v['A']; B = v['B']; C = v['C']; D = v['D']; E = v['E']
    K = v['K']; L = v['L']; M = v['M']; N = v['N']
    F = v['F']; Fr = v['Fr']; G = v['G']; Gr = v['Gr']; J = v['J']; Jr = v['Jr']
    zc = -C
    zs = -(C + M)
    zl = -(C + M + LAND_MM)
    ze = -(C + M + HEAD_MM)
    Rl = B / 2.0 if D > 0.0 else K / 2.0
    pts = [
        (Rl + Fr, 0.0),
        (A / 2.0 - Jr, 0.0),
        (A / 2.0, -J),
        (A / 2.0, zc),
        (E / 2.0, zc),
        (E / 2.0, zs),
        (L / 2.0, zs),
        (L / 2.0, zl),
        (N / 2.0, ze),
        (K / 2.0 + Gr, ze),
        (K / 2.0, ze + G),
    ]
    if D > 0.0:
        pts += [(K / 2.0, -D), (B / 2.0, -D), (B / 2.0, -F)]
    else:
        pts += [(K / 2.0, -F)]
    return _dedupe(pts)

def build_part(p):
    v = _params(p)
    if 'error' in v:
        return v
    pts = _points(v)
    if len(pts) < 3:
        return _err('Profil oluşturulamadı')
    try:
        solid = cq.Workplane('XZ').polyline(pts).close().revolve(360, (0, 0), (0, 1))
    except Exception:
        return _err('Geometri oluşturulamadı')
    return solid
