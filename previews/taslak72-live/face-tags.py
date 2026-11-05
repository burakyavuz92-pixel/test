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
    import math
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

def build_face_tags(p):
    v = _params(p)
    if 'error' in v:
        return v
    zs = -(v['C'] + v['M'])
    return [
        {
            'name': 'montaj',
            'surface': {
                'kind': 'plane',
                'normal': [0.0, 0.0, 1.0],
                'offset': zs
            }
        }
    ]
