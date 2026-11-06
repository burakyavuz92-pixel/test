def _pt(x, y, z):
    return [float(x), float(y), float(z)]


def _unres(rid, mid, source, kind, nominal, reason):
    return {'id': rid, 'markerId': mid, 'source': source, 'kind': kind, 'nominal': nominal, 'unresolved': reason}


def build_measurements(p):
    try:
        g = _geometry(p)
    except DataError as exc:
        return {'error': str(exc)}
    A = g['A']
    B = g['B']
    C = g['C']
    D = g['D']
    L = g['L']
    E = g['E']
    rA = g['rA']
    rC = g['rC']
    rH = g['rH']
    chAx = g['chAx']
    z_head = -B
    z_head_end = -(B + D)
    z_neck = -(B - NECK_LENGTH)
    z_shaft = -chAx
    out = []
    out.append({'id': 'dim-B', 'markerId': 'mk-B', 'source': 'B', 'kind': 'distance', 'nominal': B,
                'points': [_pt(0, 0, 0), _pt(0, 0, z_head)], 'direction': _pt(0, 0, 1)})
    out.append({'id': 'dim-D', 'markerId': 'mk-D', 'source': 'D', 'kind': 'distance', 'nominal': D,
                'points': [_pt(0, 0, z_head), _pt(0, 0, z_head_end)], 'direction': _pt(0, 0, 1)})
    out.append({'id': 'dim-C', 'markerId': 'mk-C', 'source': 'C', 'kind': 'diameter', 'nominal': C,
                'center': _pt(0, 0, z_neck), 'axis': _pt(0, 0, 1), 'radius': rC})
    out.append({'id': 'dim-A', 'markerId': 'mk-A', 'source': 'A', 'kind': 'diameter', 'nominal': A,
                'center': _pt(0, 0, z_shaft), 'axis': _pt(0, 0, 1), 'radius': rA})
    if E > 0:
        ang = float(p['E__angleDeg'])
        out.append({'id': 'chm-E', 'markerId': 'mk-E', 'source': 'E', 'kind': 'chamfer', 'nominal': E,
                    'points': [_pt(rA - E, 0, 0), _pt(rA, 0, -chAx)], 'direction': _pt(1, 0, 0),
                    'angleDeg': ang})
    else:
        out.append(_unres('chm-E', 'mk-E', 'E', 'chamfer', E, 'pah yok'))
    out.append({'id': 'dim-L', 'markerId': 'mk-L', 'source': 'L', 'kind': 'diameter', 'nominal': L,
                'center': _pt(0, 0, -B), 'axis': _pt(0, 0, 1), 'radius': rH})
    return out
