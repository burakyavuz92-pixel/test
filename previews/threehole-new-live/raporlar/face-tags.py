T_BASE = 3.0


def build_face_tags(p):
    if p.get('A') is None or p.get('J') is None:
        return {'error': 'montaj yuzeyi icin olcu eksik'}
    # @montaj: inner flat face of the closed end, at z = -T_BASE, material on +Z side
    return [{'name': 'montaj',
             'surface': {'kind': 'plane',
                         'normal': [0.0, 0.0, -1.0],
                         'offset': T_BASE}}]
