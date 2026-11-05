import math
import cadquery as cq

def _num(p, k, default=0.0):
    v = p.get(k)
    return float(default if v is None else v)

def _ang(p, k, default):
    v = p.get(k + "__angleDeg")
    return float(default if v is None else v)

def build_part(p):
    A = _num(p, "A")
    B = _num(p, "B")
    C = _num(p, "C")
    D = _num(p, "D")
    E = _num(p, "E")
    F = _num(p, "F")
    G = _num(p, "G")
    J = _num(p, "J")
    K = _num(p, "K")
    L = _num(p, "L")
    fa = _ang(p, "F", 45.0)
    ga = _ang(p, "G", 45.0)
    ja = _ang(p, "J", 35.0)

    neck_w = 2.8   # [2,8]
    ring_w = 5.0   # [5]
    land = 1.0     # unbracketed 1, cylindrical land at free end
    end_dia = 22.0 # unbracketed diameter 22 at free end

    ro = A / 2.0
    rn = E / 2.0
    rr = L / 2.0
    rend = end_dia / 2.0
    rB = B / 2.0
    rK = K / 2.0

    zN = -(C + neck_w)
    zE = -(C + neck_w + ring_w)

    Jr = J * math.tan(math.radians(ja))
    Fr = F * math.tan(math.radians(fa))
    Gr = G * math.tan(math.radians(ga))

    pts = [
        (ro - Jr, 0.0),
        (ro, -J),
        (ro, -C),
        (rn, -C),
        (rn, zN),
        (rr, zN),
        (rend, zE + land),
        (rend, zE),
        (rK + Gr, zE),
        (rK, zE + G),
        (rK, -D),
        (rB, -D),
        (rB, -F),
        (rB + Fr, 0.0),
    ]

    body = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
        .rotate((0, 0, 0), (1, 0, 0), 90)
    )
    return body

def build_measurements(p):
    A = _num(p, "A")
    B = _num(p, "B")
    C = _num(p, "C")
    D = _num(p, "D")
    E = _num(p, "E")
    F = _num(p, "F")
    G = _num(p, "G")
    J = _num(p, "J")
    K = _num(p, "K")
    L = _num(p, "L")
    fa = _ang(p, "F", 45.0)
    ga = _ang(p, "G", 45.0)
    ja = _ang(p, "J", 35.0)

    neck_w = 2.8
    ring_w = 5.0
    land = 1.0
    end_dia = 22.0

    ro = A / 2.0
    rn = E / 2.0
    rr = L / 2.0
    rend = end_dia / 2.0
    rB = B / 2.0
    rK = K / 2.0

    zN = -(C + neck_w)
    zE = -(C + neck_w + ring_w)

    Jr = J * math.tan(math.radians(ja))
    Fr = F * math.tan(math.radians(fa))
    Gr = G * math.tan(math.radians(ga))

    ax = [0.0, 0.0, 1.0]

    def P(r, z):
        return [float(r), 0.0, float(z)]

    def rec(rid, mid, source, kind, nominal, **kw):
        out = {"id": rid, "markerId": mid, "source": source, "kind": kind, "nominal": float(nominal)}
        out.update(kw)
        return out

    return [
        rec("rec-A", "m-A", "A", "diameter", A, center=[0.0, 0.0, -(J + C) / 2.0], axis=ax, radius=ro),
        rec("rec-B", "m-B", "B", "diameter", B, center=[0.0, 0.0, -(F + D) / 2.0], axis=ax, radius=rB),
        rec("rec-C", "m-C", "C", "distance", C, points=[P(ro - Jr, 0.0), P(ro, -C)], direction=[0.0, 0.0, -1.0]),
        rec("rec-D", "m-D", "D", "distance", D, points=[P(rB + Fr, 0.0), P(rB, -D)], direction=[0.0, 0.0, -1.0]),
        rec("rec-E", "m-E", "E", "diameter", E, center=[0.0, 0.0, -(C + neck_w / 2.0)], axis=ax, radius=rn),
        rec("rec-F", "m-F", "F", "chamfer", F, points=[P(rB, -F), P(rB + Fr, 0.0)], direction=[0.0, 0.0, 1.0], angleDeg=fa),
        rec("rec-G", "m-G", "G", "chamfer", G, points=[P(rK + Gr, zE), P(rK, zE + G)], direction=[0.0, 0.0, 1.0], angleDeg=ga),
        rec("rec-J", "m-J", "J", "chamfer", J, points=[P(ro, -J), P(ro - Jr, 0.0)], direction=[0.0, 0.0, 1.0], angleDeg=ja),
        rec("rec-L", "m-L", "L", "diameter", L, center=[0.0, 0.0, zN], axis=ax, radius=rr),
        rec("rec-5", "m-5", "5", "thickness", ring_w, points=[P(rr, zN), P(rend, zE)], direction=[0.0, 0.0, -1.0]),
        rec("rec-2,8", "m-2_8", "2,8", "thickness", neck_w, points=[P(rn, -C), P(rn, zN)], direction=[0.0, 0.0, -1.0]),
    ]
