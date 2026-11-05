def _mb_geo(p):
    v, err = _values(p)
    if err:
        return None, err
    J = _chamfer(p, 'J')
    F = _chamfer(p, 'F')
    G = _chamfer(p, 'G')
    if J is None or F is None or G is None:
        return None, 'Pah açısı verisi eksik'
    g = {}
    g['C'] = v['C']
    g['M'] = v['M']
    g['D'] = v['D']
    g['ro'] = v['A'] / 2.0
    g['Rb'] = v['B'] / 2.0
    g['Rk'] = v['K'] / 2.0
    g['Re'] = v['E'] / 2.0
    g['Rl'] = v['L'] / 2.0
    g['Rn'] = v['N'] / 2.0
    g['Ja'] = J[0]
    g['Jr'] = J[1]
    g['Fa'] = F[0]
    g['Fr'] = F[1]
    g['Ga'] = G[0]
    g['Gr'] = G[1]
    g['Rbl'] = g['Rk'] if g['D'] == 0 else g['Rb']
    g['zs'] = -(g['C'] + g['M'])
    g['zl'] = g['zs'] - 1.0
    g['zr'] = -(g['C'] + g['M'] + 5.0)
    return g, None

def _mb_base(rid, mid, src, kind, nominal):
    return {'id': rid, 'markerId': mid, 'source': src, 'kind': kind, 'nominal': float(nominal)}

def _mb_unres(rid, mid, src, kind, nominal, reason):
    r = _mb_base(rid, mid, src, kind, nominal)
    r['unresolved'] = reason
    return r

def _mb_diam(rid, mid, src, nominal, zc, radius):
    r = _mb_base(rid, mid, src, 'diameter', nominal)
    r['center'] = [0.0, 0.0, float(zc)]
    r['axis'] = [0.0, 0.0, 1.0]
    r['radius'] = float(radius)
    return r

def _mb_dist(rid, mid, src, nominal, p1, p2, direction):
    r = _mb_base(rid, mid, src, 'distance', nominal)
    r['points'] = [[float(c) for c in p1], [float(c) for c in p2]]
    r['direction'] = [float(c) for c in direction]
    return r

def _mb_chf(p, k, rid, mid, p1, p2, direction):
    leg = _num(p, k)
    ang = _num(p, k + '__angleDeg')
    if leg is None or leg == 0:
        return _mb_unres(rid, mid, k, 'chamfer', 0.0 if leg is None else leg, 'Pah boyu sıfır; bu pah yüzü yok')
    if ang is None:
        return _mb_unres(rid, mid, k, 'chamfer', leg, 'Pah açısı verisi yok')
    r = _mb_base(rid, mid, k, 'chamfer', leg)
    r['points'] = [[float(c) for c in p1], [float(c) for c in p2]]
    r['direction'] = [float(c) for c in direction]
    r['angleDeg'] = float(ang)
    return r

def build_measurements(p):
    g, err = _mb_geo(p)
    if err:
        return {'error': err}
    built = build_part(p)
    if isinstance(built, dict):
        return {'error': built.get('error', 'Geometri üretilemedi')}
    C = g['C']
    M = g['M']
    D = g['D']
    ro = g['ro']
    Rb = g['Rb']
    Rk = g['Rk']
    Re = g['Re']
    Rl = g['Rl']
    Rn = g['Rn']
    Ja = g['Ja']
    Jr = g['Jr']
    Fa = g['Fa']
    Fr = g['Fr']
    Ga = g['Ga']
    Gr = g['Gr']
    Rbl = g['Rbl']
    zs = g['zs']
    zl = g['zl']
    zr = g['zr']
    rl = ((Rbl + Fr) + (ro - Jr)) / 2.0
    out = []
    out.append(_mb_diam('rec-A', 'mk-A-1', 'A', _num(p, 'A'), -(Ja + C) / 2.0, ro))
    if D == 0:
        out.append(_mb_unres('rec-B', 'mk-B-1', 'B', 'diameter', _num(p, 'B'), 'Derinlik sıfır; B için ayrı cep yok'))
    else:
        out.append(_mb_diam('rec-B', 'mk-B-1', 'B', _num(p, 'B'), -(Fa + D) / 2.0, Rb))
    out.append(_mb_dist('rec-C', 'mk-C-1', 'C', C, [rl, 0.0, 0.0], [(ro + Re) / 2.0, 0.0, -C], [0.0, 0.0, -1.0]))
    if D == 0:
        out.append(_mb_unres('rec-D', 'mk-D-1', 'D', 'distance', 0.0, 'Derinlik sıfır; ölçü çizilmez'))
    else:
        out.append(_mb_dist('rec-D', 'mk-D-1', 'D', D, [rl, 0.0, 0.0], [(Rk + Rb) / 2.0, 0.0, -D], [0.0, 0.0, -1.0]))
    out.append(_mb_diam('rec-E', 'mk-E-1', 'E', _num(p, 'E'), -(C + M / 2.0), Re))
    out.append(_mb_chf(p, 'F', 'rec-F', 'mk-F-1', [Rbl + Fr, 0.0, 0.0], [Rbl, 0.0, -Fa], [0.0, 0.0, -1.0]))
    out.append(_mb_chf(p, 'G', 'rec-G', 'mk-G-1', [Rk + Gr, 0.0, zr], [Rk, 0.0, zr + Ga], [0.0, 0.0, 1.0]))
    out.append(_mb_chf(p, 'J', 'rec-J', 'mk-J-1', [ro - Jr, 0.0, 0.0], [ro, 0.0, -Ja], [0.0, 0.0, -1.0]))
    out.append(_mb_diam('rec-L', 'mk-L-1', 'L', _num(p, 'L'), (zs + zl) / 2.0, Rl))
    out.append(_mb_dist('rec-M', 'mk-M-1', 'M', M, [(ro + Re) / 2.0, 0.0, -C], [(Re + Rl) / 2.0, 0.0, zs], [0.0, 0.0, -1.0]))
    out.append(_mb_diam('rec-N', 'mk-N-1', 'N', _num(p, 'N'), zr, Rn))
    out.append(_mb_dist('rec-5', 'mk-5-1', ' 5 ', 5.0, [(Re + Rl) / 2.0, 0.0, zs], [(Rk + Gr + Rn) / 2.0, 0.0, zr], [0.0, 0.0, -1.0]))
    return out
