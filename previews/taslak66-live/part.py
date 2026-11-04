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
