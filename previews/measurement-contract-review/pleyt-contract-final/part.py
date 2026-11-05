import math
import cadquery as cq

WALL = 3.0
RIM_R = 1.5

def _num(p, k):
    v = p.get(k)
    return None if v is None else float(v)

def build_part(p):
    A = _num(p, 'A')
    D = _num(p, 'D')
    E = _num(p, 'E')
    J = _num(p, 'J')
    if A is None or D is None or E is None or J is None:
        return {'error': 'Gerekli ölçüler eksik'}
    if A <= 0 or J <= 0:
        return {'error': 'Çap veya boy sıfır ya da negatif'}
    if D < 0 or E < 0:
        return {'error': 'Köşe yarıçapı negatif olamaz'}
    R = A / 2.0
    ri = R - WALL
    if ri <= 0:
        return {'error': 'Duvar kalınlığı bu çapa sığmıyor'}
    if D >= R:
        return {'error': 'Dış köşe yarıçapı gövde yarıçapına sığmıyor'}
    if E >= ri:
        return {'error': 'İç köşe yarıçapı iç yarıçapı aşıyor'}
    zr = J - RIM_R
    if D >= zr:
        return {'error': 'Dış köşe yarıçapı boya sığmıyor'}
    if WALL + E >= zr:
        return {'error': 'İç köşe yarıçapı boya sığmıyor'}
    s = math.sqrt(0.5)
    wp = cq.Workplane('XZ').moveTo(0.0, 0.0)
    if D > 0:
        wp = wp.lineTo(R - D, 0.0)
        wp = wp.threePointArc((R - D + D * s, -D + D * s), (R, -D))
        wp = wp.lineTo(R, -zr)
    else:
        wp = wp.lineTo(R, 0.0).lineTo(R, -zr)
    wp = wp.threePointArc((R - RIM_R + RIM_R * s, -zr - RIM_R * s), (R - RIM_R, -J))
    wp = wp.lineTo(ri, -J)
    if E > 0:
        wp = wp.lineTo(ri, -(WALL + E))
        wp = wp.threePointArc((ri - E + E * s, -(WALL + E) + E * s), (ri - E, -WALL))
    else:
        wp = wp.lineTo(ri, -WALL)
    wp = wp.lineTo(0.0, -WALL).close()
    solid = wp.revolve(360.0, (0, 0, 0), (0, 1, 0))
    return solid
