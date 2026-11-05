import math

def build_measurements(p):
    A = _num(p, 'A')
    D = _num(p, 'D')
    E = _num(p, 'E')
    J = _num(p, 'J')
    if A is None or D is None or E is None or J is None:
        return {'error': 'Gerekli ölçüler eksik'}
    chk = build_part(p)
    if isinstance(chk, dict):
        return chk
    R = A / 2.0
    ri = R - WALL
    zr = J - RIM_R
    s = math.sqrt(0.5)
    recs = []
    recs.append({'id': 'rec-A', 'markerId': 'sec-A-1', 'source': 'A', 'kind': 'diameter', 'nominal': A, 'center': [0.0, 0.0, -(D + zr) / 2.0], 'axis': [0.0, 0.0, 1.0], 'radius': R})
    if D > 0:
        recs.append({'id': 'rec-D', 'markerId': 'sec-D-1', 'source': 'D', 'kind': 'radius', 'nominal': D, 'center': [R - D, 0.0, -D], 'axis': [0.0, 1.0, 0.0], 'radius': D, 'point': [R - D + D * s, 0.0, -D + D * s]})
    zm = -(max(D, WALL + E) + zr) / 2.0
    recs.append({'id': 'rec-3', 'markerId': 'sec-3-1', 'source': '3', 'kind': 'distance', 'nominal': WALL, 'points': [[0.0, R, zm], [0.0, ri, zm]], 'direction': [0.0, 1.0, 0.0]})
    rm = (ri + R - RIM_R) / 2.0
    recs.append({'id': 'rec-J', 'markerId': 'sec-J-1', 'source': 'J', 'kind': 'distance', 'nominal': J, 'points': [[0.0, 0.0, 0.0], [rm, 0.0, -J]], 'direction': [0.0, 0.0, -1.0]})
    if E > 0:
        recs.append({'id': 'rec-E', 'markerId': 'sec-E-1', 'source': 'E', 'kind': 'radius', 'nominal': E, 'center': [ri - E, 0.0, -(WALL + E)], 'axis': [0.0, 1.0, 0.0], 'radius': E, 'point': [ri - E + E * s, 0.0, -(WALL + E) + E * s]})
    return recs
