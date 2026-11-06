import math


def build_face_tags(p):
    a = p.get('A')
    b = p.get('B')
    if a is None or b is None:
        return {'error': 'A veya B ölçüsü eksik'}
    try:
        a = float(a)
        b = float(b)
    except Exception:
        return {'error': 'A veya B ölçüsü sayısal değil'}
    if not (math.isfinite(a) and math.isfinite(b)) or a <= 0 or b <= 0:
        return {'error': 'A veya B ölçüsü geçersiz'}
    return [
        {'name': 'dis', 'surface': {'kind': 'cylinder', 'axisOrigin': [0.0, 0.0, 0.0], 'axisDirection': [0.0, 0.0, -1.0], 'radius': a / 2.0}},
        {'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': -b}},
    ]
