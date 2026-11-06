import math
import cadquery as cq

NECK_LEN = 5.0
TAPER_LEN = 2.5
HEAD_ROUND = 5.0
COLLAR_FILLET = 1.0
SQRT_HALF = 0.7071067811865476


def _params(p):
    vals = {}
    for key in ('A', 'B', 'C', 'D', 'E', 'L'):
        raw = p.get(key)
        if raw is None:
            return None, key + ' ölçüsü eksik'
        vals[key] = float(raw)
    for key in ('A', 'B', 'C', 'D', 'L'):
        if vals[key] <= 0:
            return None, key + ' ölçüsü pozitif olmalı'
    if vals['E'] < 0:
        return None, 'pah ölçüsü negatif'
    ang = p.get('E__angleDeg')
    if vals['E'] > 0:
        if ang is None:
            return None, 'pah açısı eksik'
        ang = float(ang)
        if not (0.0 < ang < 90.0):
            return None, 'pah açısı geçersiz'
        if vals['E'] >= vals['A'] / 2.0:
            return None, 'pah ölçüsü çapa göre çok büyük'
        vals['ang'] = ang
    else:
        vals['ang'] = 0.0
    if vals['B'] <= NECK_LEN + TAPER_LEN:
        return None, 'gövde boyu yetersiz'
    if vals['D'] < HEAD_ROUND:
        return None, 'kafa kalınlığı yuvarlatma için yetersiz'
    if vals['L'] <= 2.0 * HEAD_ROUND:
        return None, 'kafa çapı yuvarlatma için yetersiz'
    if vals['L'] <= vals['C'] + 2.0 * COLLAR_FILLET:
        return None, 'kafa çapı boyun çapına göre yetersiz'
    return vals, None


def build_part(p):
    vals, err = _params(p)
    if err:
        return {'error': err}
    A = vals['A']
    B = vals['B']
    C = vals['C']
    D = vals['D']
    E = vals['E']
    L = vals['L']
    ang = vals['ang']
    rA = A / 2.0
    rC = C / 2.0
    rL = L / 2.0
    zN = -B
    zb = -(B - NECK_LEN)
    za = zb - TAPER_LEN
    zc = zN - (D - HEAD_ROUND)
    zF = zN - D
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    wp = cq.Workplane(plane).moveTo(0.0, 0.0)
    if E > 0:
        ax = E / math.tan(math.radians(ang))
        wp = wp.lineTo(rA - E, 0.0).lineTo(rA, -ax)
    else:
        wp = wp.lineTo(rA, 0.0)
    wp = wp.lineTo(rA, za).lineTo(rC, zb).lineTo(rC, zN + COLLAR_FILLET)
    wp = wp.threePointArc(
        (rC + COLLAR_FILLET - COLLAR_FILLET * SQRT_HALF, zN + COLLAR_FILLET - COLLAR_FILLET * SQRT_HALF),
        (rC + COLLAR_FILLET, zN))
    wp = wp.lineTo(rL, zN)
    if D > HEAD_ROUND:
        wp = wp.lineTo(rL, zc)
    wp = wp.threePointArc(
        (rL - HEAD_ROUND + HEAD_ROUND * SQRT_HALF, zc - HEAD_ROUND * SQRT_HALF),
        (rL - HEAD_ROUND, zc - HEAD_ROUND))
    wp = wp.lineTo(0.0, zF).close()
    solid = wp.revolve(360.0, (0, 0, 0), (0, 1, 0))
    if not solid.val().isValid():
        return {'error': 'geometri geçersiz'}
    return solid
