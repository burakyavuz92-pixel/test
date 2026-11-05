import cadquery as cq


def build_face_tags(p):
    C = p.get('C')
    M = p.get('M')
    if C is None or M is None:
        return {'error': 'eksik ölçü'}
    z_shoulder = -(float(C) + float(M))
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': z_shoulder}}]
