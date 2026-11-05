import math


def _f(p, k, default=0.0):
    v = p.get(k)
    if v is None:
        return float(default)
    return float(v)


def _cham(p, label):
    leg = _f(p, label, 0.0)
    if leg <= 0.0:
        return 0.0, 0.0
    ang = p.get(label + '__angleDeg')
    if ang is None:
        ang = 45.0
    return leg, leg * math.tan(math.radians(float(ang)))


def _dims(p):
    A = _f(p, 'A')
    B = _f(p, 'B')
    C = _f(p, 'C')
    D = _f(p, 'D')
    E = _f(p, 'E')
    K = _f(p, 'K')
    L = _f(p, 'L')
    M = _f(p, 'M')
    N = _f(p, 'N')
    if min(A, C, K, L, N) <= 0.0:
        return None, 'Ana ölçüler eksik veya sıfır'
    if D < 0.0 or D > C or M < 0.0:
        return None, 'Derinlik ölçüsü gövde boyuna uymuyor'
    if D > 0.0 and B <= 0.0:
        return None, 'Sayaç çapı eksik'
    if M > 0.0 and E <= 0.0:
        return None, 'Boyun çapı eksik'
    RA = A / 2.0
    RK = K / 2.0
    RB = B / 2.0 if D > 0.0 else RK
    RE = E / 2.0
    RL = L / 2.0
    RN = N / 2.0
    if RN >= RL:
        return None, 'Flanş konisi çapı kolye çapından büyük'
    if RK >= RA or RB >= RA or RK >= RN:
        return None, 'Delik çapı dış çapa göre çok büyük'
    if M > 0.0 and RE <= RK:
        return None, 'Boyun çapı delikten küçük'
    Jx, Jr = _cham(p, 'J')
    Fx, Fr = _cham(p, 'F')
    Gx, Gr = _cham(p, 'G')
    if Jx > C:
        return None, 'Dış pah gövde boyunu aşıyor'
    if D > 0.0 and Fx > D:
        return None, 'Giriş pahı sayaç derinliğini aşıyor'
    if RA - Jr - (RB + Fr) <= 0.0:
        return None, 'Sol yüzde pahlar çakışıyor'
    if Gx > 0.0 and RN - (RK + Gr) <= 0.0:
        return None, 'Sağ yüzde iç pah çakışıyor'
    g = {'C': C, 'M': M}
    return g, None


def build_face_tags(p):
    g, err = _dims(p)
    if err is not None:
        return {'error': err}
    zc = -(g['C'] + g['M'])
    return [{'name': 'montaj',
             'surface': {'kind': 'plane',
                         'normal': [0.0, 0.0, 1.0],
                         'offset': zc}}]
