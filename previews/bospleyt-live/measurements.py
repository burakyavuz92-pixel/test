import math

def build_measurements(p):
    A = p.get('A')
    D = p.get('D')
    E = p.get('E')
    J = p.get('J')
    if A is None or D is None or E is None or J is None:
        return {'error': 'Satırda A, D, E veya J ölçüsü eksik.'}
    Ro = A / 2.0
    Ri = Ro - WALL
    if min(A, D, E, J) <= 0 or Ro <= D or Ri <= E or J <= WALL + E:
        return {'error': 'Bu satırdaki ölçüler tutarlı bir kesit üretmiyor.'}
    m = 1.0 / math.sqrt(2.0)
    yMid = -(D + J) / 2.0
    return [
        {'id': 'R-A', 'markerId': 'm-A', 'source': 'A', 'kind': 'diameter', 'nominal': A,
         'center': [0.0, yMid, 0.0], 'axis': [0.0, 1.0, 0.0], 'radius': Ro},
        {'id': 'R-D', 'markerId': 'm-D', 'source': 'D', 'kind': 'radius', 'nominal': D,
         'center': [Ro - D, -D, 0.0], 'point': [Ro - D + D * m, -D + D * m, 0.0],
         'axis': [0.0, 0.0, 1.0], 'radius': D},
        {'id': 'R-3', 'markerId': 'm-3', 'source': '3', 'kind': 'thickness', 'nominal': WALL,
         'points': [[Ro, yMid, 0.0], [Ri, yMid, 0.0]], 'direction': [-1.0, 0.0, 0.0]},
        {'id': 'R-E', 'markerId': 'm-E', 'source': 'E', 'kind': 'radius', 'nominal': E,
         'center': [Ri - E, -WALL - E, 0.0], 'point': [Ri - E + E * m, -WALL - E + E * m, 0.0],
         'axis': [0.0, 0.0, 1.0], 'radius': E},
        {'id': 'R-J', 'markerId': 'm-J', 'source': 'J', 'kind': 'distance', 'nominal': J,
         'points': [[Ro - D, 0.0, 0.0], [Ro, -J, 0.0]], 'direction': [0.0, -1.0, 0.0]},
    ]
