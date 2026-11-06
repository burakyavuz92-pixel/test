def _num(p, key):
    v = p.get(key)
    if v is None:
        return None
    return float(v)

def build_face_tags(p):
    b = _num(p, 'B')
    if b is None or b <= 0:
        return {'error': 'montaj yuzeyi belirlenemedi'}
    return [
        {
            'name': 'montaj',
            'surface': {
                'kind': 'plane',
                'normal': [0.0, 0.0, 1.0],
                'offset': -b
            }
        }
    ]
