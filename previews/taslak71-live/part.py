import math
import cadquery as cq


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
    g = {'RA': RA, 'RB': RB, 'RK': RK, 'RE': RE, 'RL': RL, 'RN': RN,
         'C': C, 'D': D, 'M': M, 'Jx': Jx, 'Jr': Jr,
         'Fx': Fx, 'Fr': Fr, 'Gx': Gx, 'Gr': Gr}
    return g, None


def _profile(g):
    RA = g['RA']
    RB = g['RB']
    RK = g['RK']
    RE = g['RE']
    RL = g['RL']
    RN = g['RN']
    C = g['C']
    D = g['D']
    M = g['M']
    Jx = g['Jx']
    Jr = g['Jr']
    Fx = g['Fx']
    Fr = g['Fr']
    Gx = g['Gx']
    Gr = g['Gr']
    pts = []

    def add(x, z):
        if pts and abs(pts[-1][0] - x) < 1e-9 and abs(pts[-1][1] - z) < 1e-9:
            return
        pts.append((x, z))

    zc = -(C + M)
    zend = zc - 5.0
    add(RA - Jr, 0.0)
    add(RA, -Jx)
    add(RA, -C)
    if M > 0.0:
        add(RE, -C)
        add(RE, zc)
    add(RL, zc)
    add(RL, zc - 1.0)
    add(RN, zend)
    add(RK + Gr, zend)
    add(RK, zend + Gx)
    if D > 0.0:
        add(RK, -D)
        add(RB, -D)
        add(RB, -Fx)
    else:
        add(RK, -Fx)
    add(RB + Fr, 0.0)
    return pts


def build_part(p):
    g, err = _dims(p)
    if err is not None:
        return {'error': err}
    pts = _profile(g)
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    body = cq.Workplane(plane).polyline(pts).close().revolve(360.0, (0, 0), (0, 1))
    return body
