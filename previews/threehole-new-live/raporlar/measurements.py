import math


def _unresolved(rid, mid, src, kind, nominal, reason):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': kind, 'nominal': nominal, 'unresolved': reason}


def _diameter(rid, mid, src, nominal, center, radius):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': 'diameter', 'nominal': nominal, 'center': center, 'axis': [0.0, 0.0, 1.0], 'radius': radius}


def _distance(rid, mid, src, nominal, points, direction):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': 'distance', 'nominal': nominal, 'points': points, 'direction': direction}


def build_measurements(p):
    chk, err = _check(p)
    if err is not None:
        return {'error': err}
    v, holes = chk
    ro = v['A'] / 2.0
    ri = ro - T_WALL
    J = v['J']
    B = v['B']
    F = v['F']
    zb = (-R_CLOSED_OUT + (-J + R_OPEN_RIM)) / 2.0
    zh = -T_BASE / 2.0
    h = B / 2.0
    out = []
    out.append(_diameter('rec-sec-A', 'sec-A', 'A', v['A'], [0.0, 0.0, zb], ro))
    out.append(_distance('rec-sec-J', 'sec-J', 'J', J, [[0.0, 0.0, 0.0], [ri, 0.0, -J]], [0.0, 0.0, 1.0]))
    out.append(_distance('rec-front-F', 'front-F', 'F', F, [[0.0, 0.0, zh], [-F, 0.0, zh]], [1.0, 0.0, 0.0]))
    for key, rid, mid, x, y in (('C', 'rec-front-C', 'front-C', 0.0, h), ('D', 'rec-front-D', 'front-D', 0.0, -h), ('E', 'rec-front-E', 'front-E', -F, 0.0)):
        d = v[key]
        if d <= 0:
            out.append(_unresolved(rid, mid, key, 'diameter', d, 'delik yok'))
        else:
            out.append(_diameter(rid, mid, key, d, [x, y, zh], d / 2.0))
    if v['C'] <= 0 or v['D'] <= 0:
        out.append(_unresolved('rec-front-B', 'front-B', 'B', 'distance', B, 'delik yok'))
    else:
        out.append(_distance('rec-front-B', 'front-B', 'B', B, [[0.0, h, zh], [0.0, -h, zh]], [0.0, 1.0, 0.0]))
    if v['D'] <= 0:
        out.append(_unresolved('rec-front-G', 'front-G', 'G', 'distance', v['G'], 'delik yok'))
    else:
        out.append(_distance('rec-front-G', 'front-G', 'G', v['G'], [[0.0, 0.0, zh], [0.0, -h, zh]], [0.0, 1.0, 0.0]))
    return out
