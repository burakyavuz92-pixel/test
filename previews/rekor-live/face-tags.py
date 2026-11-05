import cadquery as cq


def _num(p, key, default=0.0):
    v = p.get(key)
    return float(default if v is None else v)


def build_face_tags(p):
    C = _num(p, 'C')
    M = _num(p, 'M')
    E = _num(p, 'E')
    L = _num(p, 'L')
    if L / 2.0 <= E / 2.0:
        return {'error': 'Montaj yüzeyi tanımlanamadı'}
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': -(C + M)}}]
