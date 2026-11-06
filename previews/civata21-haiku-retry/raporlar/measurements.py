import math

def _arc_extreme(cr, cz, rad, p6, p7, am):
    tau = 2.0 * math.pi
    th6 = math.atan2(p6[1] - cz, p6[0] - cr)
    th7 = math.atan2(p7[1] - cz, p7[0] - cr)
    thm = math.atan2(am[1] - cz, am[0] - cr)
    d7 = (th7 - th6) % tau
    dm = (thm - th6) % tau
    span = d7 if dm < d7 else d7 - tau
    best = None
    for i in range(2001):
        th = th6 + span * i / 2000.0
        r = cr + rad * math.cos(th)
        z = cz + rad * math.sin(th)
        if best is None or r > best[0]:
            best = (r, z)
    return best

def build_measurements(p):
    a, err = _num(p, 'A')
    if err:
        return {'error': err}
    b, err = _num(p, 'B')
    if err:
        return {'error': err}
    c, err = _num(p, 'C')
    if err:
        return {'error': err}
    d, err = _num(p, 'D')
    if err:
        return {'error': err}
    l, err = _num(p, 'L')
    if err:
        return {'error': err}
    ec, axial, err = _chamfer(p)
    if err:
        return {'error': err}
    chk = build_part(p)
    if isinstance(chk, dict):
        return chk
    rs = a / 2.0
    rc = c / 2.0
    rh = l / 2.0
    zu = -b
    zt = -(b + d)
    rt = rh - HEAD_EDGE_STEP
    p6 = (rh, zu)
    p7 = (rt, zt)
    vr = rt - rh
    vz = zt - zu
    lc = math.hypot(vr, vz)
    h = math.sqrt(max(HEAD_ROUND_R ** 2 - (lc / 2.0) ** 2, 0.0))
    nr = vz / lc
    nz = -vr / lc
    cr = (rh + rt) / 2.0 + h * nr
    cz = (zu + zt) / 2.0 + h * nz
    am = (cr - HEAD_ROUND_R * nr, cz - HEAD_ROUND_R * nz)
    rmax, zmax = _arc_extreme(cr, cz, HEAD_ROUND_R, p6, p7, am)
    z_shank = -(axial + (b - NECK_LENGTH - CONE_LENGTH)) / 2.0
    z_neck = -(b - NECK_LENGTH / 2.0)
    recs = []
    recs.append({'id': 'rec-A', 'markerId': 'mk-A', 'source': 'A', 'kind': 'diameter', 'nominal': a, 'center': [0.0, 0.0, z_shank], 'axis': [0.0, 0.0, 1.0], 'radius': rs})
    recs.append({'id': 'rec-B', 'markerId': 'mk-B', 'source': 'B', 'kind': 'distance', 'nominal': b, 'points': [[0.0, 0.0, 0.0], [0.0, 0.0, zu]], 'direction': [0.0, 0.0, 1.0]})
    recs.append({'id': 'rec-C', 'markerId': 'mk-C', 'source': 'C', 'kind': 'diameter', 'nominal': c, 'center': [0.0, 0.0, z_neck], 'axis': [0.0, 0.0, 1.0], 'radius': rc})
    recs.append({'id': 'rec-D', 'markerId': 'mk-D', 'source': 'D', 'kind': 'distance', 'nominal': d, 'points': [[rh, 0.0, zu], [rt, 0.0, zt]], 'direction': [0.0, 0.0, 1.0]})
    recs.append({'id': 'rec-L', 'markerId': 'mk-L', 'source': 'L', 'kind': 'diameter', 'nominal': l, 'center': [0.0, 0.0, zmax], 'axis': [0.0, 0.0, 1.0], 'radius': rmax})
    if ec > 0:
        ang = float(p.get('E__angleDeg'))
        recs.append({'id': 'rec-E', 'markerId': 'mk-E', 'source': 'E', 'kind': 'chamfer', 'nominal': ec, 'points': [[rs - ec, 0.0, 0.0], [rs, 0.0, -axial]], 'direction': [1.0, 0.0, 0.0], 'angleDeg': ang})
    return recs
