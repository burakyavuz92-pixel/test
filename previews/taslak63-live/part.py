import cadquery as cq
import math

def build_part(p):
    A = float(p['A'])
    B = float(p['B'])
    C = float(p['C'])
    D = float(p['D'])
    E = float(p['E'])
    HEAD_D = 25.0
    END_D = 22.0
    NECK_L = 2.8
    HEAD_L = 5.0
    THREAD_D = 12.0
    CH = 1.0
    rA = A / 2.0
    rB = B / 2.0
    rE = E / 2.0
    rH = HEAD_D / 2.0
    rEnd = END_D / 2.0
    rT = THREAD_D / 2.0
    z_neck = -C
    z_head = -(C + NECK_L)
    z_end = -(C + NECK_L + HEAD_L)
    # Profile in (radius, z) on XZ workplane; local y = global Z; body extends to -Z
    pts = [
        (rT + CH, 0.0),
        (rA, 0.0),
        (rA, z_neck),
        (rE, z_neck),
        (rE, z_head),
        (rH, z_head),
        (rEnd, z_end),
        (rB + CH, z_end),
        (rB, z_end + CH),
        (rB, -D),
        (rT, -D),
        (rT, -CH),
    ]
    body = cq.Workplane('XZ').polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
    return body
