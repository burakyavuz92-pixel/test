import math
import cadquery as cq

LAND_MM = 1.0
LIP_TOTAL_MM = 5.0


def _num(p, key, default=0.0):
    v = p.get(key)
    return float(default if v is None else v)


def _chamfer(p, key):
    leg = _num(p, key)
    if leg <= 0.0:
        return 0.0, 0.0
    ang = p.get(key + '__angleDeg')
    if ang is None:
        raise ValueError('Pah açısı eksik')
    ang = float(ang)
    if not (0.0 < ang < 90.0):
        raise ValueError('Pah açısı geçersiz')
    return leg, leg * math.tan(math.radians(ang))


def _dedupe(pts):
    out = []
    for q in pts:
        if not out or abs(out[-1][0] - q[0]) > 1e-9 or abs(out[-1][1] - q[1]) > 1e-9:
            out.append(q)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out


def _profile(p):
    A = _num(p, 'A')
    B = _num(p, 'B')
    C = _num(p, 'C')
    D = _num(p, 'D')
    E = _num(p, 'E')
    K = _num(p, 'K')
    L = _num(p, 'L')
    M = _num(p, 'M')
    N = _num(p, 'N')
    if A <= 0 or K <= 0 or C <= 0 or L <= 0 or N <= 0:
        raise ValueError('Temel ölçü eksik')
    if L / 2.0 <= E / 2.0:
        raise ValueError('Omuz yüzeyi oluşmuyor')
    R = A / 2.0
    Rb = B / 2.0
    Rk = K / 2.0
    Re = E / 2.0
    Rl = L / 2.0
    Rn = N / 2.0
    jx, jr = _chamfer(p, 'J')
    fx, fr = _chamfer(p, 'F')
    gx, gr = _chamfer(p, 'G')
    end = C + M + LIP_TOTAL_MM
    if D < 0 or D > end:
        raise ValueError('Derinlik uyumsuz')
    if D > 0 and B <= 0:
        raise ValueError('B çapı eksik')
    rin = Rb if D > 0 else Rk
    if D > 0 and fx > D:
        raise ValueError('Pah derinliği uyumsuz')
    if end - gx < D:
        raise ValueError('Sağ taraf derinliği uyumsuz')
    if (R - jr) <= rin + fr:
        raise ValueError('Giriş duvarı yetersiz')
    if Rn <= Rk + gr:
        raise ValueError('Sağ yüz duvarı yetersiz')
    s_pts = [(R - jr, 0.0)]
    if jx > 0:
        s_pts.append((R, jx))
    s_pts += [(R, C), (Re, C), (Re, C + M), (Rl, C + M), (Rl, C + M + LAND_MM), (Rn, end), (Rk + gr, end)]
    if gx > 0:
        s_pts.append((Rk, end - gx))
    if D > 0:
        s_pts += [(Rk, D), (Rb, D), (Rb, fx), (Rb + fr, 0.0)]
    else:
        s_pts += [(Rk, fx), (Rk + fr, 0.0)]
    s_pts = _dedupe(s_pts)
    return [(r, -s) for r, s in s_pts]


def build_part(p):
    try:
        pts = _profile(p)
    except ValueError as e:
        return {'error': str(e)}
    wp = cq.Workplane('XY').polyline(pts).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    return wp.rotate((0, 0, 0), (1, 0, 0), 90)
