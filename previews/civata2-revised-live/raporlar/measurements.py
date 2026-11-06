import math

def build_measurements(p):
    chk = build_part(p)
    if isinstance(chk, dict):
        return chk
    A = float(p['A'])
    B = float(p['B'])
    C = float(p['C'])
    D = float(p['D'])
    E = float(p['E'])
    L = float(p['L'])
    ang = float(p['E__angleDeg'])
    Rh = L / 2.0
    axial = E
    radial = E * math.tan(math.radians(ang))
    zs = -(B - NECK_LEN - TAPER_LEN)
    zt = -(B + D)
    rr = EDGE_RADIUS - EDGE_INSET
    zc = zt + math.sqrt(EDGE_RADIUS ** 2 - rr ** 2)
    z_shank = (-axial + zs) / 2.0
    z_neck = -(B - NECK_LEN / 2.0)
    ax = [0.0, 0.0, 1.0]
    return [
        {'id': 'dim_A', 'markerId': 'sec-A', 'source': 'A', 'kind': 'diameter', 'nominal': A, 'center': [0.0, 0.0, z_shank], 'axis': ax, 'radius': A / 2.0},
        {'id': 'dim_B', 'markerId': 'sec-B', 'source': 'B', 'kind': 'distance', 'nominal': B, 'points': [[0.0, 0.0, 0.0], [0.0, 0.0, -B]], 'direction': ax},
        {'id': 'dim_C', 'markerId': 'sec-C', 'source': 'C', 'kind': 'diameter', 'nominal': C, 'center': [0.0, 0.0, z_neck], 'axis': ax, 'radius': C / 2.0},
        {'id': 'dim_D', 'markerId': 'sec-D', 'source': 'D', 'kind': 'distance', 'nominal': D, 'points': [[0.0, 0.0, -B], [0.0, 0.0, zt]], 'direction': ax},
        {'id': 'dim_E', 'markerId': 'sec-E', 'source': 'E', 'kind': 'chamfer', 'nominal': E, 'angleDeg': ang, 'points': [[A / 2.0 - radial, 0.0, 0.0], [A / 2.0, 0.0, -axial]], 'direction': ax},
        {'id': 'dim_L', 'markerId': 'front-L', 'source': 'L', 'kind': 'diameter', 'nominal': L, 'center': [0.0, 0.0, zc], 'axis': ax, 'radius': Rh},
    ]
