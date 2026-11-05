class _RowError(Exception):
    pass


def _req(p, key):
    v = p.get(key)
    if v is None:
        raise _RowError('Eksik boyut verisi: ' + key)
    return float(v)


def build_face_tags(p):
    try:
        C = _req(p, 'C')
        M = _req(p, 'M')
    except _RowError as e:
        return {'error': str(e)}
    # @montaj: shoulder face between the E-diameter neck and the L-diameter land,
    # located at z = -(C+M), facing +Z (toward the left end of the source section)
    return [{'name': 'montaj', 'surface': {'kind': 'plane', 'normal': [0.0, 0.0, 1.0], 'offset': -(C + M)}}]
