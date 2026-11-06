import math

NECK_LENGTH = 5.0
CONE_LENGTH = 2.5
UNDERHEAD_RADIUS = 1.0
HEAD_EDGE_RADIUS = 5.0


class DataError(ValueError):
    pass


def _pos(p, key):
    v = p.get(key)
    if v is None:
        raise DataError(key + ' ölçüsü eksik')
    v = float(v)
    if not math.isfinite(v) or v <= 0:
        raise DataError(key + ' ölçüsü geçersiz')
    return v


def _geometry(p):
    A = _pos(p, 'A')
    B = _pos(p, 'B')
    C = _pos(p, 'C')
    D = _pos(p, 'D')
    L = _pos(p, 'L')
    e = p.get('E')
    E = 0.0 if e is None else float(e)
    if not math.isfinite(E) or E < 0:
        raise DataError('E pah ölçüsü geçersiz')
    rA = A / 2.0
    rC = C / 2.0
    rH = L / 2.0
    chAx = 0.0
    if E > 0:
        ang = p.get('E__angleDeg')
        if ang is None:
            raise DataError('E pah açısı eksik')
        ang = float(ang)
        if not (0 < ang < 90):
            raise DataError('E pah açısı geçersiz')
        if E >= rA:
            raise DataError('pah gövde yarıçapından büyük')
        chAx = E * math.tan(math.radians(ang))
    if D < HEAD_EDGE_RADIUS:
        raise DataError('kafa kalınlığı R5 için yetersiz')
    if rH - HEAD_EDGE_RADIUS <= 0:
        raise DataError('kafa çapı R5 için yetersiz')
    if rH <= rC + UNDERHEAD_RADIUS:
        raise DataError('kafa çapı alt radyüs için yetersiz')
    thread_len = B - NECK_LENGTH - CONE_LENGTH
    if thread_len <= chAx:
        raise DataError('dış çap boyu yetersiz')
    return {'A': A, 'B': B, 'C': C, 'D': D, 'L': L, 'E': E,
            'rA': rA, 'rC': rC, 'rH': rH, 'chAx': chAx}


def build_face_tags(p):
    try:
        g = _geometry(p)
    except DataError as exc:
        return {'error': str(exc)}
    return [
        {'name': 'dis',
         'surface': {'kind': 'cylinder',
                     'axisOrigin': [0.0, 0.0, 0.0],
                     'axisDirection': [0.0, 0.0, 1.0],
                     'radius': g['rA']}},
        {'name': 'montaj',
         'surface': {'kind': 'plane',
                     'normal': [0.0, 0.0, 1.0],
                     'offset': -g['B']}},
    ]
