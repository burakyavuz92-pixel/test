def build_face_tags(p):
    C = p.get('C')
    M = p.get('M')
    if C is None or M is None:
        return {'error': 'Montaj yüzeyi için ölçü eksik'}
    zs = -(float(C) + float(M))
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': zs}}]
