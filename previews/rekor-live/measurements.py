def build_measurements(p):
    try:
        _profile(p)
    except ValueError as e:
        return {'error': 'Satır ölçüleri geometri kurallarına uymuyor: ' + str(e)}
    A = _num(p, 'A')
    B = _num(p, 'B')
    C = _num(p, 'C')
    D = _num(p, 'D')
    E = _num(p, 'E')
    K = _num(p, 'K')
    L = _num(p, 'L')
    M = _num(p, 'M')
    N = _num(p, 'N')
    F_val = _num(p, 'F')
    G_val = _num(p, 'G')
    J_val = _num(p, 'J')
    jx, jr = _chamfer(p, 'J')
    fx, fr = _chamfer(p, 'F')
    gx, gr = _chamfer(p, 'G')
    R = A / 2.0
    Rb = B / 2.0
    Rk = K / 2.0
    Re = E / 2.0
    Rl = L / 2.0
    Rn = N / 2.0
    end = C + M + LIP_TOTAL_MM
    has_b = D > 0.0
    rin = Rb if has_b else Rk
    zdir = [0.0, 0.0, -1.0]

    def ang(key):
        a = p.get(key + '__angleDeg')
        return None if a is None else float(a)

    def rec(label, kind, nominal, **kw):
        r = {'id': 'meas-' + label, 'markerId': 'marker-' + label, 'source': label, 'kind': kind, 'nominal': nominal}
        r.update(kw)
        return r

    def diam(label, nominal, radius, zc):
        return rec(label, 'diameter', nominal, center=[0.0, 0.0, zc], axis=[0.0, 0.0, 1.0], radius=radius)

    def dist(label, nominal, p1, p2):
        return rec(label, 'distance', nominal, points=[p1, p2], direction=list(zdir))

    def cham(label, leg, p1, p2):
        return rec(label, 'chamfer', leg, points=[p1, p2], direction=list(zdir), angleDeg=ang(label))

    out = []
    out.append(diam('A', A, R, -(jx + C) / 2.0))
    if has_b:
        out.append(diam('B', B, Rb, -(fx + D) / 2.0))
    else:
        out.append(rec('B', 'diameter', B, unresolved='D=0 olduğundan B deliği yok'))
    out.append(dist('C', C, [R - jr, 0.0, 0.0], [R, 0.0, -C]))
    if has_b:
        out.append(dist('D', D, [Rb + fr, 0.0, 0.0], [Rb, 0.0, -D]))
    else:
        out.append(rec('D', 'distance', D, unresolved='D=0 olduğundan delik derinliği yok'))
    out.append(diam('E', E, Re, -(C + M / 2.0)))
    if fx > 0.0:
        out.append(cham('F', fx, [rin + fr, 0.0, 0.0], [rin, 0.0, -fx]))
    else:
        out.append(rec('F', 'chamfer', F_val, unresolved='F pahı tanımlı değil'))
    if gx > 0.0:
        out.append(cham('G', gx, [Rk, 0.0, -(end - gx)], [Rk + gr, 0.0, -end]))
    else:
        out.append(rec('G', 'chamfer', G_val, unresolved='G pahı tanımlı değil'))
    if jx > 0.0:
        out.append(cham('J', jx, [R - jr, 0.0, 0.0], [R, 0.0, -jx]))
    else:
        out.append(rec('J', 'chamfer', J_val, unresolved='J pahı tanımlı değil'))
    out.append(diam('L', L, Rl, -(C + M + LAND_MM / 2.0)))
    out.append(dist('M', M, [Re, 0.0, -C], [Re, 0.0, -(C + M)]))
    out.append(diam('N', N, Rn, -end))
    out.append(dist('5', end - (C + M), [Rl, 0.0, -(C + M)], [Rn, 0.0, -end]))
    return out
