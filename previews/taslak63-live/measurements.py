import cadquery as cq
import math

HEAD_D = 25.0
END_D = 22.0
NECK_L = 2.8
HEAD_L = 5.0
THREAD_D = 12.0
CH = 1.0

def _diameter(rid, mid, source, center, nominal):
    return {"id": rid, "markerId": mid, "source": source, "kind": "diameter", "nominal": nominal, "center": center, "axis": [0.0, 0.0, 1.0], "radius": nominal / 2.0}

def _distance(rid, mid, source, points, direction, nominal):
    return {"id": rid, "markerId": mid, "source": source, "kind": "distance", "nominal": nominal, "points": points, "direction": direction}

def _chamfer(rid, mid, source, points, direction, nominal):
    return {"id": rid, "markerId": mid, "source": source, "kind": "chamfer", "nominal": nominal, "angleDeg": 45.0, "points": points, "direction": direction}

def build_measurements(p):
    A = float(p['A'])
    B = float(p['B'])
    C = float(p['C'])
    D = float(p['D'])
    E = float(p['E'])
    rA = A / 2.0
    rB = B / 2.0
    rT = THREAD_D / 2.0
    z_neck = -C
    z_head = -(C + NECK_L)
    z_end = -(C + NECK_L + HEAD_L)
    z_bore = (-D + z_end + CH) / 2.0
    out = []
    out.append(_diameter("R-A", "M-A", "A", [0.0, 0.0, -C / 2.0], A))
    out.append(_diameter("R-B", "M-B", "B", [0.0, 0.0, z_bore], B))
    out.append(_distance("R-C", "M-C", "C", [[rA, 0.0, 0.0], [rA, 0.0, z_neck]], [0.0, 0.0, -1.0], C))
    out.append(_distance("R-D", "M-D", "D", [[rT, 0.0, 0.0], [rT, 0.0, -D]], [0.0, 0.0, -1.0], D))
    out.append(_diameter("R-E", "M-E", "E", [0.0, 0.0, -(C + NECK_L / 2.0)], E))
    out.append(_diameter("R-25", "M-25", "25 ±0,5", [0.0, 0.0, -(C + NECK_L + HEAD_L / 2.0)], HEAD_D))
    out.append(_chamfer("R-CH1", "M-CH1", "1 X 45°", [[rT + CH, 0.0, 0.0], [rT, 0.0, -CH]], [0.0, 0.0, -1.0], CH))
    out.append(_chamfer("R-CH2", "M-CH2", "1 X 45°", [[rB + CH, 0.0, z_end], [rB, 0.0, z_end + CH]], [0.0, 0.0, 1.0], CH))
    return out
