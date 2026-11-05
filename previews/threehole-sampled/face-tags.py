import cadquery as cq

WALL_T = 3.0
END_T = 3.0

class _RowError(Exception):
    pass

def _req(p, k):
    v = p.get(k)
    if v is None:
        raise _RowError('Eksik ölçü: ' + k)
    return float(v)

def _check(p):
    A = _req(p, 'A')
    B = _req(p, 'B')
    G = _req(p, 'G')
    J = _req(p, 'J')
    if A <= 0 or B <= 0 or J <= 0:
        raise _RowError('Geçersiz boyut')
    if abs(B - 2.0 * G) > 1e-6:
        raise _RowError('B ve G ölçüleri uyuşmuyor')
    if A / 2.0 - WALL_T <= 0 or J <= END_T:
        raise _RowError('Yüzey tanımlanamıyor')

def build_face_tags(p):
    try:
        _check(p)
    except _RowError as e:
        return {'error': str(e)}
    # @montaj: inner face of the closed end plate, plane z = -END_T
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, -1.0], 'offset': END_T}}]
