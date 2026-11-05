import math

def build_measurements(p):
    solid = build_part(p)
    if isinstance(solid, dict):
        return solid
    A = float(p['A'])
    D = float(p['D'])
    E = float(p['E'])
    J = float(p['J'])
    R = A / 2.0
    S = math.sqrt(0.5)
    recs = []
    recs.append({'id': 'A-diameter', 'markerId': 'sec-A-1', 'source': 'A', 'kind': 'diameter', 'nominal': A, 'center': [0.0, 0.0, -(J + D) / 2.0], 'axis': [0.0, 0.0, 1.0], 'radius': R})
    recs.append({'id': 'D-outer-radius', 'markerId': 'sec-D-1', 'source': 'D', 'kind': 'radius', 'nominal': D, 'center': [R - D, 0.0, -D], 'axis': [0.0, 1.0, 0.0], 'radius': D, 'point': [R - D + D * S, 0.0, -D + D * S]})
    recs.append({'id': '3-wall-thickness', 'markerId': 'sec-3-1', 'source': '3', 'kind': 'thickness', 'nominal': float(WALL_T), 'points': [[0.0, R, -J / 2.0], [0.0, R - WALL_T, -J / 2.0]], 'direction': [0.0, 1.0, 0.0]})
    cr = R - WALL_T - E
    cz = -WALL_T - E
    recs.append({'id': 'E-inner-radius', 'markerId': 'sec-E-1', 'source': 'E', 'kind': 'radius', 'nominal': E, 'center': [cr, 0.0, cz], 'axis': [0.0, 1.0, 0.0], 'radius': E, 'point': [cr + E * S, 0.0, cz + E * S]})
    recs.append({'id': 'J-length', 'markerId': 'sec-J-1', 'source': 'J', 'kind': 'distance', 'nominal': J, 'points': [[0.0, 0.0, 0.0], [0.0, R, -J]], 'direction': [0.0, 0.0, 1.0]})
    return recs
