def build_measurements(p):
    vals, err = _params(p)
    if err:
        return {'error': err}
    A = vals['A']
    B = vals['B']
    C = vals['C']
    D = vals['D']
    E = vals['E']
    L = vals['L']
    ang = vals['ang']
    rA = A / 2.0
    rC = C / 2.0
    rL = L / 2.0
    zN = -B
    zb = -(B - NECK_LEN)
    za = zb - TAPER_LEN
    zc = zN - (D - HEAD_ROUND)
    zF = zN - D
    ax = E / math.tan(math.radians(ang)) if E > 0 else 0.0
    zCh = -ax
    zShank = (zCh + za) / 2.0
    zNeck = (zb + zN + COLLAR_FILLET) / 2.0
    zHead = (zN + zc) / 2.0
    zAxis = [0.0, 0.0, 1.0]
    recs = []
    recs.append({'id': 'rec_A', 'markerId': 'm_A', 'source': 'A', 'kind': 'diameter', 'nominal': A, 'center': [0.0, 0.0, zShank], 'axis': zAxis, 'radius': rA})
    recs.append({'id': 'rec_B', 'markerId': 'm_B', 'source': 'B', 'kind': 'distance', 'nominal': B, 'points': [[0.0, 0.0, 0.0], [0.0, 0.0, zN]], 'direction': zAxis})
    recs.append({'id': 'rec_C', 'markerId': 'm_C', 'source': 'C', 'kind': 'diameter', 'nominal': C, 'center': [0.0, 0.0, zNeck], 'axis': zAxis, 'radius': rC})
    recs.append({'id': 'rec_D', 'markerId': 'm_D', 'source': 'D', 'kind': 'distance', 'nominal': D, 'points': [[0.0, 0.0, zN], [0.0, 0.0, zF]], 'direction': zAxis})
    if E > 0:
        recs.append({'id': 'rec_E', 'markerId': 'm_E', 'source': 'E', 'kind': 'chamfer', 'nominal': E, 'angleDeg': ang, 'points': [[rA - E, 0.0, 0.0], [rA, 0.0, zCh]], 'direction': [1.0, 0.0, 0.0]})
    else:
        recs.append({'id': 'rec_E', 'source': 'E', 'kind': 'chamfer', 'nominal': E, 'unresolved': 'pah ölçüsü sıfır, ölçü yok'})
    recs.append({'id': 'rec_L', 'markerId': 'm_L', 'source': 'L', 'kind': 'diameter', 'nominal': L, 'center': [0.0, 0.0, zHead], 'axis': zAxis, 'radius': rL})
    return recs
