import math
import cadquery as cq

WALL = 3.0

def build_part(p):
    A = p.get("A")
    D = p.get("D")
    E = p.get("E")
    J = p.get("J")
    if A is None or D is None or E is None or J is None:
        return {"error": "eksik ölçü var"}
    Ro = A / 2.0
    Ri = Ro - WALL
    if min(A, D, E, J) <= 0 or Ro <= D or Ri <= E or J <= WALL + E:
        return {"error": "ölçüler tutarlı bir parça oluşturmuyor"}
    m = 1.0 / math.sqrt(2.0)
    pl = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    prof = (
        cq.Workplane(pl)
        .moveTo(0, 0)
        .lineTo(Ro - D, 0)
        .threePointArc((Ro - D + D * m, -D + D * m), (Ro, -D))
        .lineTo(Ro, -J)
        .lineTo(Ri, -J)
        .lineTo(Ri, -WALL - E)
        .threePointArc((Ri - E + E * m, -WALL - E + E * m), (Ri - E, -WALL))
        .lineTo(0, -WALL)
        .close()
    )
    return prof.revolve(360, (0, 0, 0), (0, 1, 0))
