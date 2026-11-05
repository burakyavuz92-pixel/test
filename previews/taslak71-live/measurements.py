import math


def _rec(mid, marker, source, kind, nominal, **kw):
    r = {'id': mid, 'markerId': marker, 'source': source, 'kind': kind, 'nominal': nominal}
    r.update(kw)
    return r


def _angle(p, label):
    a = p.get(label + '__angleDeg')
    if a is None:
        a = 45.0
    return float(a)


def build_measurements(p):
    g, err = _dims(p)
    if err is not None:
        return {'error': err}
    C = g['C']
    M = g['M']
    D = g['D']
    RA = g['RA']
    RB = g['RB']
    RK = g['RK']
    RE = g['RE']
    RL = g['RL']
    RN = g['RN']
    Jx = g['Jx']
    Jr = g['Jr']
    Fx = g['Fx']
    Fr = g['Fr']
    Gx = g['Gx']
    Gr = g['Gr']
    zc = -(C + M)
    zend = zc - 5.0
    ax = [0.0, 0.0, 1.0]
    dn = [0.0, 0.0, -1.0]
    up = [0.0, 0.0, 1.0]
    out = []

    out.append(_rec('r-A', 'm-A', 'A', 'diameter', _f(p, 'A'), center=[0.0, 0.0, -C / 2.0], axis=ax, radius=RA))

    if D > 0.0:
        out.append(_rec('r-B', 'm-B', 'B', 'diameter', _f(p, 'B'), center=[0.0, 0.0, -(Fx + D) / 2.0], axis=ax, radius=RB))
    else:
        out.append(_rec('r-B', 'm-B', 'B', 'diameter', _f(p, 'B'), unresolved='Sayaç derinliği sıfır'))

    out.append(_rec('r-C', 'm-C', 'C', 'distance', _f(p, 'C'), points=[[RA - Jr, 0.0, 0.0], [RA, 0.0, -C]], direction=dn))

    if D > 0.0:
        out.append(_rec('r-D', 'm-D', 'D', 'distance', _f(p, 'D'), points=[[RB + Fr, 0.0, 0.0], [RB, 0.0, -D]], direction=dn))
    else:
        out.append(_rec('r-D', 'm-D', 'D', 'distance', _f(p, 'D'), unresolved='Sayaç derinliği sıfır'))

    if M > 0.0:
        out.append(_rec('r-E', 'm-E', 'E', 'diameter', _f(p, 'E'), center=[0.0, 0.0, -C - M / 2.0], axis=ax, radius=RE))
    else:
        out.append(_rec('r-E', 'm-E', 'E', 'diameter', _f(p, 'E'), unresolved='Boyun yok (M=0)'))

    if Fx > 0.0:
        out.append(_rec('r-F', 'm-F', 'F', 'chamfer', Fx, points=[[RB + Fr, 0.0, 0.0], [RB, 0.0, -Fx]], direction=dn, angleDeg=_angle(p, 'F')))
    else:
        out.append(_rec('r-F', 'm-F', 'F', 'chamfer', _f(p, 'F'), unresolved='Pah yok (F=0)'))

    if Gx > 0.0:
        out.append(_rec('r-G', 'm-G', 'G', 'chamfer', Gx, points=[[RK + Gr, 0.0, zend], [RK, 0.0, zend + Gx]], direction=up, angleDeg=_angle(p, 'G')))
    else:
        out.append(_rec('r-G', 'm-G', 'G', 'chamfer', _f(p, 'G'), unresolved='Pah yok (G=0)'))

    if Jx > 0.0:
        out.append(_rec('r-J', 'm-J', 'J', 'chamfer', Jx, points=[[RA - Jr, 0.0, 0.0], [RA, 0.0, -Jx]], direction=dn, angleDeg=_angle(p, 'J')))
    else:
        out.append(_rec('r-J', 'm-J', 'J', 'chamfer', _f(p, 'J'), unresolved='Pah yok (J=0)'))

    out.append(_rec('r-L', 'm-L', 'L', 'diameter', _f(p, 'L'), center=[0.0, 0.0, zc - 0.5], axis=ax, radius=RL))

    if M > 0.0:
        out.append(_rec('r-M', 'm-M', 'M', 'distance', M, points=[[RE, 0.0, -C], [RE, 0.0, zc]], direction=dn))
    else:
        out.append(_rec('r-M', 'm-M', 'M', 'distance', _f(p, 'M'), unresolved='Boyun yok (M=0)'))

    out.append(_rec('r-N', 'm-N', 'N', 'diameter', _f(p, 'N'), center=[0.0, 0.0, zend], axis=ax, radius=RN))

    out.append(_rec('r-5', 'm-5', '5', 'distance', 5.0, points=[[RL, 0.0, zc], [RN, 0.0, zend]], direction=dn))

    return out
