import math
import cadquery as cq


class _RowError(Exception):
    pass


def _req(p, key):
    v = p.get(key)
    if v is None:
        raise _RowError('Eksik boyut verisi: ' + key)
    v = float(v)
    if v < 0:
        raise _RowError('Negatif boyut: ' + key)
    return v


def _chamfer(p, label):
    # leg = axial length; radial leg = leg * tan(angle), angle measured from the axis
    leg = p.get(label)
    if leg is None or float(leg) == 0.0:
        return 0.0, 0.0
    leg = float(leg)
    ang = p.get(label + '__angleDeg')
    if ang is None:
        raise _RowError('Şamfer açısı eksik: ' + label)
    ang = float(ang)
    if not (0.0 < ang < 90.0):
        raise _RowError('Geçersiz şamfer açısı: ' + label)
    return leg, leg * math.tan(math.radians(ang))


def _dedupe(points):
    out = []
    for pt in points:
        if not out or abs(pt[0] - out[-1][0]) > 1e-9 or abs(pt[1] - out[-1][1]) > 1e-9:
            out.append(pt)
    return out


def _profile(p):
    A = _req(p, 'A')
    B = _req(p, 'B')
    C = _req(p, 'C')
    D = _req(p, 'D')
    E = _req(p, 'E')
    K = _req(p, 'K')
    L = _req(p, 'L')
    M = _req(p, 'M')
    N = _req(p, 'N')
    if min(A, C, E, K, L, M, N) <= 0:
        raise _RowError('Geçersiz sıfır veya negatif boyut')
    if D > 0 and B <= 0:
        raise _RowError('Karşıdelik çapı geçersiz')

    RA = A / 2.0
    RE = E / 2.0
    RL = L / 2.0
    RN = N / 2.0
    rK = K / 2.0
    rB = B / 2.0 if D > 0 else rK

    F, Fr = _chamfer(p, 'F')
    G, Gr = _chamfer(p, 'G')
    J, Jr = _chamfer(p, 'J')

    total = C + M + 5.0          # overall length from left end face to right end face
    zf = -total

    if D + G >= total:
        raise _RowError('Sağ taraf duvarı yetersiz')
    if D > 0 and F >= D:
        raise _RowError('Sol şamfer kademe ile çakışıyor')
    if rB + Fr >= RA - Jr:
        raise _RowError('Sol yüz duvarı yetersiz')
    if rK + Gr >= RN:
        raise _RowError('Sağ yüz duvarı yetersiz')

    pts = []
    # outer boundary, left to right (z = 0 at left end face, body toward -Z)
    if J > 0:
        pts += [(RA - Jr, 0.0), (RA, -J)]
    else:
        pts += [(RA, 0.0)]
    pts += [(RA, -C), (RE, -C), (RE, -(C + M)), (RL, -(C + M)), (RL, -(C + M + 1.0)), (RN, zf)]

    # right end face and bore chamfer
    if G > 0:
        pts += [(rK + Gr, zf), (rK, zf + G)]
    else:
        pts += [(rK, zf)]

    # inner bore, right to left
    if D > 0:
        pts += [(rK, -D), (rB, -D)]
    rb = rB if D > 0 else rK

    # left bore chamfer and left end face
    if F > 0:
        pts += [(rb, -F), (rb + Fr, 0.0)]
    else:
        pts += [(rb, 0.0)]

    pts = _dedupe(pts)
    if len(pts) < 3:
        raise _RowError('Profil oluşturulamadı')
    return pts


def build_part(p):
    try:
        pts = _profile(p)
        solid = cq.Workplane('XZ').polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
        if not solid.val().isValid():
            return {'error': 'Geometri geçersiz'}
    except _RowError as e:
        return {'error': str(e)}
    return solid
