import cadquery as cq


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
    if vals['E'] > 0:
        ang = p.get('E__angleDeg')
        if ang is None:
            return None, 'pah açısı eksik'
        ang = float(ang)
        if not (0.0 < ang < 90.0):
            return None, 'pah açısı geçersiz'
    if vals['B'] <= 7.5:
        return None, 'gövde boyu yetersiz'
    if vals['D'] < 5.0:
        return None, 'kafa kalınlığı yuvarlatma için yetersiz'
    return vals, None


def build_face_tags(p):
    vals, err = _params(p)
    if err:
        return {'error': err}
    return [
        {
            'name': 'dis',
            'surface': {
                'kind': 'cylinder',
                'axisOrigin': [0.0, 0.0, 0.0],
                'axisDirection': [0.0, 0.0, 1.0],
                'radius': vals['A'] / 2.0,
            },
        },
        {
            'name': 'montaj',
            'surface': {
                'kind': 'plane',
                'normal': [0.0, 0.0, 1.0],
                'offset': -vals['B'],
            },
        },
    ]
