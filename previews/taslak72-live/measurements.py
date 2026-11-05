import math

def _meas(mid, source, marker, kind, nominal, unresolved=None, **extra):
    rec = {'id': mid, 'source': source, 'kind': kind, 'nominal': float(nominal), 'markerId': marker}
    if unresolved is not None:
        rec['unresolved'] = unresolved
    rec.update(extra)
    return rec

def _diam(mid, source, marker, nominal, cz, unresolved=None):
    if unresolved is not None:
        return _meas(mid, source, marker, 'diameter', nominal, unresolved)
    return _meas(mid, source, marker, 'diameter', nominal, None, center=[0.0, 0.0, float(cz)], axis=[0.0, 0.0, 1.0], radius=float(nominal) / 2.0)

def _dist(mid, source, marker, nominal, p0, p1, d, unresolved=None):
    if unresolved is not None:
        return _meas(mid, source, marker, 'distance', nominal, unresolved)
    return _meas(mid, source, marker, 'distance', nominal, None, points=[[float(c) for c in p0], [float(c) for c in p1]], direction=[float(c) for c in d])

def _cham(mid, source, marker, leg, angle, p0, p1, d, unresolved=None):
    if unresolved is not None:
        return _meas(mid, source, marker, 'chamfer', leg, unresolved, angleDeg=angle)
    return _meas(mid, source, marker, 'chamfer', leg, None, points=[[float(c) for c in p0], [float(c) for c in p1]], direction=[float(c) for c in d], angleDeg=angle)

def _angle(p, key):
    a = p.get(key + '__angleDeg')
    return None if a is None else float(a)

def build_measurements(p):
    v = _params(p)
    if 'error' in v:
        return v
    part = build_part(p)
    if isinstance(part, dict):
        return part
    A = v['A']; B = v['B']; C = v['C']; D = v['D']; E = v['E']
    K = v['K']; L = v['L']; M = v['M']; N = v['N']
    F = v['F']; Fr = v['Fr']; G = v['G']; Gr = v['Gr']; J = v['J']; Jr = v['Jr']
    zc = -C
    zS = -(C + M)
    zL = zS - LAND_MM
    zE = -(C + M + HEAD_MM)
    rin = B / 2.0 if D > 0.0 else K / 2.0
    up = (0.0, 0.0, 1.0)
    down = (0.0, 0.0, -1.0)
    zero = (0.0, 0.0, 0.0)
    recs = []
    recs.append(_diam('meas_A', 'A', 'mk_A', A, -(J + C) / 2.0))
    if D > 0.0:
        recs.append(_diam('meas_B', 'B', 'mk_B', B, -(F + D) / 2.0))
    else:
        recs.append(_diam('meas_B', 'B', 'mk_B', B, 0.0, 'D=0 olduğundan karşı delik yok'))
    recs.append(_dist('meas_C', 'C', 'mk_C', C, (A / 2.0 - Jr, 0.0, 0.0), (A / 2.0, 0.0, zc), down))
    if D > 0.0:
        recs.append(_dist('meas_D', 'D', 'mk_D', D, (B / 2.0 + Fr, 0.0, 0.0), (B / 2.0, 0.0, -D), down))
    else:
        recs.append(_dist('meas_D', 'D', 'mk_D', D, zero, zero, down, 'D=0 olduğundan karşı delik yok'))
    if M > 0.0:
        recs.append(_diam('meas_E', 'E', 'mk_E', E, -(C + M / 2.0)))
    else:
        recs.append(_diam('meas_E', 'E', 'mk_E', E, 0.0, 'M=0 olduğundan flanş yok'))
    if F > 0.0:
        recs.append(_cham('meas_F', 'F', 'mk_F', F, _angle(p, 'F'), (rin + Fr, 0.0, 0.0), (rin, 0.0, -F), down))
    else:
        recs.append(_cham('meas_F', 'F', 'mk_F', F, _angle(p, 'F'), zero, zero, down, 'pah boyu sıfır'))
    if G > 0.0:
        recs.append(_cham('meas_G', 'G', 'mk_G', G, _angle(p, 'G'), (K / 2.0 + Gr, 0.0, zE), (K / 2.0, 0.0, zE + G), up))
    else:
        recs.append(_cham('meas_G', 'G', 'mk_G', G, _angle(p, 'G'), zero, zero, up, 'pah boyu sıfır'))
    if J > 0.0:
        recs.append(_cham('meas_J', 'J', 'mk_J', J, _angle(p, 'J'), (A / 2.0 - Jr, 0.0, 0.0), (A / 2.0, 0.0, -J), down))
    else:
        recs.append(_cham('meas_J', 'J', 'mk_J', J, _angle(p, 'J'), zero, zero, down, 'pah boyu sıfır'))
    recs.append(_diam('meas_L', 'L', 'mk_L', L, (zS + zL) / 2.0))
    if M > 0.0:
        recs.append(_dist('meas_M', 'M', 'mk_M', M, (E / 2.0, 0.0, zc), (E / 2.0, 0.0, zS), down))
    else:
        recs.append(_dist('meas_M', 'M', 'mk_M', M, zero, zero, down, 'M=0 olduğundan adım yok'))
    recs.append(_diam('meas_N', 'N', 'mk_N', N, zE))
    recs.append(_dist('meas_5', '5', 'mk_5', HEAD_MM, (L / 2.0, 0.0, zS), (N / 2.0, 0.0, zE), down))
    return recs
