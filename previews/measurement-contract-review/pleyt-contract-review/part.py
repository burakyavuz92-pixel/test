import math
import cadquery as cq

WALL_T = 3.0

def build_part(p):
    A = p.get('A')
    D = p.get('D')
    E = p.get('E')
    J = p.get('J')
    if A is None or D is None or E is None or J is None:
        return {'error': 'Eksik ölçü değeri var'}
    R = float(A) / 2.0
    D = float(D)
    E = float(E)
    J = float(J)
    if R <= 0 or J <= 0 or D < 0 or E < 0:
        return {'error': 'Geçersiz ölçü değeri'}
    if R - WALL_T <= 0:
        return {'error': 'Duvar kalınlığı gövde çapından büyük'}
    if D >= R:
        return {'error': 'Dış köşe yarıçapı gövdeye sığmıyor'}
    if R - WALL_T - E <= 0:
        return {'error': 'İç köşe yarıçapı iç boşluğa sığmıyor'}
    if J <= WALL_T + E:
        return {'error': 'Boy taban ve iç köşe için yetersiz'}
    if J <= D:
        return {'error': 'Boy dış köşe yarıçapından kısa'}
    s = math.sqrt(0.5)
    wp = cq.Workplane('XY').moveTo(0, 0)
    if D > 0:
        wp = wp.lineTo(R - D, 0).threePointArc((R - D + D * s, -D + D * s), (R, -D))
    else:
        wp = wp.lineTo(R, 0)
    wp = wp.lineTo(R, -J).lineTo(R - WALL_T, -J)
    if E > 0:
        cr = R - WALL_T - E
        cz = -WALL_T - E
        wp = wp.lineTo(R - WALL_T, cz).threePointArc((cr + E * s, cz + E * s), (cr, -WALL_T))
    else:
        wp = wp.lineTo(R - WALL_T, -WALL_T)
    wp = wp.lineTo(0, -WALL_T).close()
    solid = wp.revolve(360, (0, 0, 0), (0, 1, 0))
    solid = solid.rotate((0, 0, 0), (1, 0, 0), 90)
    return solid

def build_face_tags(p):
    return []
