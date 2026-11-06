import math
import cadquery as cq

NECK_LEN = 5.0
TAPER_HALF_ANGLE_DEG = 10.0
HEAD_EDGE_FILLET = 2.0

def _val(p, key):
    v = p.get(key)
    if v is None:
        return None
    return float(v)

def _layout(p):
    A = _val(p, 'A')
    B = _val(p, 'B')
    C = _val(p, 'C')
    D = _val(p, 'D')
    L = _val(p, 'L')
    if A is None or B is None or C is None or D is None or L is None:
        raise ValueError('Eksik olcu verisi var')
    for name, v in (('A', A), ('B', B), ('C', C), ('D', D), ('L', L)):
        if v <= 0:
            raise ValueError(name + ' olcusu pozitif olmali')
    if L <= C or L <= A:
        raise ValueError('Kafa capi govde capindan buyuk olmali')
    E = _val(p, 'E')
    if E is None or E == 0:
        ch_ax = 0.0
        ch_rad = 0.0
    else:
        ang = p.get('E__angleDeg')
        ang = 45.0 if ang is None else float(ang)
        if E < 0 or ang <= 0 or ang >= 90:
            raise ValueError('Pah olcusu gecersiz')
        ch_ax = E
        ch_rad = E * math.tan(math.radians(ang))
        if ch_rad >= A / 2.0:
            raise ValueError('Pah govde yaricapindan buyuk')
    taper = abs(C - A) / 2.0 / math.tan(math.radians(TAPER_HALF_ANGLE_DEG))
    s1 = B - NECK_LEN - taper
    if s1 <= ch_ax:
        raise ValueError('B boyu govde ve boyun icin yetersiz')
    return {'A': A, 'B': B, 'C': C, 'D': D, 'L': L, 'ch_ax': ch_ax, 'ch_rad': ch_rad, 'taper': taper, 's1': s1}

def build_part(p):
    try:
        g = _layout(p)
    except ValueError as exc:
        return {'error': str(exc)}
    A = g['A']
    B = g['B']
    C = g['C']
    D = g['D']
    L = g['L']
    ax = cq.Vector(0, 0, -1)
    origin = cq.Vector(0, 0, 0)
    parts = []
    if g['ch_ax'] > 0:
        parts.append(cq.Solid.makeCone(A / 2.0 - g['ch_rad'], A / 2.0, g['ch_ax'], origin, ax))
    parts.append(cq.Solid.makeCylinder(A / 2.0, g['s1'] - g['ch_ax'], cq.Vector(0, 0, -g['ch_ax']), ax))
    if g['taper'] > 1e-9:
        parts.append(cq.Solid.makeCone(A / 2.0, C / 2.0, g['taper'], cq.Vector(0, 0, -g['s1']), ax))
    parts.append(cq.Solid.makeCylinder(C / 2.0, NECK_LEN, cq.Vector(0, 0, -(g['s1'] + g['taper'])), ax))
    head = cq.Workplane('XY').workplane(offset=-(B + D)).circle(L / 2.0).extrude(D)
    head = head.faces('<Z').edges().fillet(min(HEAD_EDGE_FILLET, 0.4 * D))
    parts.append(head.val())
    shape = parts[0]
    for part in parts[1:]:
        shape = shape.fuse(part)
    shape = shape.clean()
    return cq.Workplane('XY').newObject([shape])
