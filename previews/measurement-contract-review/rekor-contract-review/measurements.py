def _m_angle(p, key):
    a = p.get(key + '__angleDeg')
    if a is None:
        return None
    return float(a)

def _m_diam(rid, mid, src, nominal, zc, radius):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': 'diameter', 'nominal': float(nominal), 'center': [0.0, 0.0, float(zc)], 'axis': [0.0, 0.0, 1.0], 'radius': float(radius)}

def _m_dist(rid, mid, src, nominal, p1, p2):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': 'distance', 'nominal': float(nominal), 'points': [p1, p2], 'direction': [0.0, 0.0, 1.0]}

def _m_cham(rid, mid, src, nominal, p1, p2, ang):
    out = {'id': rid, 'markerId': mid, 'source': src, 'kind': 'chamfer', 'nominal': float(nominal), 'points': [p1, p2], 'direction': [0.0, 0.0, 1.0]}
    if ang is not None:
        out['angleDeg'] = ang
    return out

def build_measurements(p):
    pts, err = _profile(p)
    if err is not None:
        return {'error': err}
    v = _dims(p)
    fl, fr = _leg(p, 'F')
    gl, gr = _leg(p, 'G')
    jl, jr = _leg(p, 'J')
    RA = v['A'] / 2.0
    RB = v['B'] / 2.0
    RK = v['K'] / 2.0
    RE = v['E'] / 2.0
    RL = v['L'] / 2.0
    RN = v['N'] / 2.0
    C = v['C']
    D = v['D']
    M = v['M']
    zC = -C
    zM = -(C + M)
    zL = zM - LAND_MM
    zE = -(C + M + COLLAR_TOTAL_MM)
    bore_left = RB if D > 0 else RK
    if D > 0:
        zB = (-fl - D) / 2.0
        d_p1 = [bore_left + fr, 0.0, 0.0]
        d_p2 = [RB, 0.0, -D]
        d_nom = D
    else:
        zB = (-fl + zE + gl) / 2.0
        d_p1 = [bore_left + fr, 0.0, 0.0]
        d_p2 = [bore_left + fr, 0.0, 0.0]
        d_nom = 0.0
    recs = []
    recs.append(_m_diam('rec-A', 'mk-A', 'A', v['A'], (zC - jl) / 2.0, RA))
    recs.append(_m_diam('rec-B', 'mk-B', 'B', v['B'], zB, bore_left))
    recs.append(_m_dist('rec-C', 'mk-C', 'C', C, [RA - jr, 0.0, 0.0], [RA, 0.0, zC]))
    recs.append(_m_dist('rec-D', 'mk-D', 'D', d_nom, d_p1, d_p2))
    recs.append(_m_diam('rec-E', 'mk-E', 'E', v['E'], (zM + zC) / 2.0, RE))
    recs.append(_m_cham('rec-F', 'mk-F', 'F', fl, [bore_left + fr, 0.0, 0.0], [bore_left, 0.0, -fl], _m_angle(p, 'F')))
    recs.append(_m_cham('rec-G', 'mk-G', 'G', gl, [RK, 0.0, zE + gl], [RK + gr, 0.0, zE], _m_angle(p, 'G')))
    recs.append(_m_cham('rec-J', 'mk-J', 'J', jl, [RA - jr, 0.0, 0.0], [RA, 0.0, -jl], _m_angle(p, 'J')))
    recs.append(_m_diam('rec-L', 'mk-L', 'L', v['L'], (zL + zM) / 2.0, RL))
    recs.append(_m_diam('rec-N', 'mk-N', 'N', v['N'], zE, RN))
    recs.append(_m_dist('rec-M', 'mk-M', 'M', M, [RE, 0.0, zC], [RE, 0.0, zM]))
    recs.append(_m_dist('rec-5', 'mk-5', ' 5 ', COLLAR_TOTAL_MM, [RL, 0.0, zM], [RN, 0.0, zE]))
    return recs
