def _num(p, key):
    v = p.get(key)
    return 0.0 if v is None else float(v)

COLLAR_LEN = 2.8
HEAD_LEN = 5.0
END_DIA = 22.0

def build_face_tags(p):
    C = _num(p, 'C')
    L = _num(p, 'L')
    if L <= END_DIA:
        return {'error': 'Kafa çapı L=' + format(L, 'g') + ' mm, 22 mm konik uçtan büyük olmalı'}
    # @montaj: annular shoulder face on the head lip, facing the left end (+Z).
    # Located at distance C + 2.8 from the origin, i.e. Z = -(C + 2.8).
    z = -(C + COLLAR_LEN)
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': z}}]
