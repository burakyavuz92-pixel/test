import math
import cadquery as cq

def build_part(p):
    A = float(p["A"]); B = float(p["B"]); C = float(p["C"]); D = float(p["D"])
    E = float(p["E"]); K = float(p["K"])
    F = float(p["F"]); Fa = float(p["F__angleDeg"])
    G = float(p["G"]); Ga = float(p["G__angleDeg"])
    J = float(p["J"]); Ja = float(p["J__angleDeg"])
    r_out = A / 2.0
    r_neck = E / 2.0
    r_lip = 25.0 / 2.0
    r_end = 22.0 / 2.0
    rb = B / 2.0
    rk = K / 2.0
    z_step = C + 2.8
    z_land = z_step + 1.0
    L = z_step + 5.0
    rF = F * math.tan(math.radians(Fa))
    rG = G * math.tan(math.radians(Ga))
    rJ = J * math.tan(math.radians(Ja))
    pts = [
        (rb + rF, 0.0),
        (r_out - rJ, 0.0),
        (r_out, -J),
        (r_out, -C),
        (r_neck, -C),
        (r_neck, -z_step),
        (r_lip, -z_step),
        (r_lip, -z_land),
        (r_end, -L),
        (rk + rG, -L),
        (rk, -(L - G)),
        (rk, -D),
        (rb, -D),
        (rb, -F),
    ]
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    body = cq.Workplane(plane).polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
    return body
