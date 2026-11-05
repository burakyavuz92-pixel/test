import math

def build_measurements(p):
    A = _val(p, "A")
    D = _val(p, "D")
    E = _val(p, "E")
    J = _val(p, "J")
    if A is None or D is None or E is None or J is None:
        return {"error": "Eksik ölçü var"}
    if A <= 0 or D <= 0 or E <= 0 or J <= 0:
        return {"error": "Ölçüler sıfır veya negatif olamaz"}
    R = A / 2.0
    Ri = R - WALL_T
    if D >= R or E >= Ri or J <= D:
        return {"error": "Ölçüler tutarlı bir parça oluşturmuyor"}
    c = math.sqrt(0.5)
    axis_z = [0.0, 0.0, 1.0]
    return [
        {"id": "rec-A", "markerId": "m-A", "source": "A", "kind": "diameter", "nominal": A, "center": [0.0, 0.0, -J / 2.0], "axis": axis_z, "radius": R},
        {"id": "rec-D", "markerId": "m-D", "source": "D", "kind": "radius", "nominal": D, "center": [R - D, 0.0, -D], "point": [R - D + D * c, 0.0, -D + D * c], "axis": [0.0, 1.0, 0.0], "radius": D},
        {"id": "rec-E", "markerId": "m-E", "source": "E", "kind": "radius", "nominal": E, "center": [Ri - E, 0.0, -WALL_T - E], "point": [Ri - E + E * c, 0.0, -WALL_T - E + E * c], "axis": [0.0, 1.0, 0.0], "radius": E},
        {"id": "rec-J", "markerId": "m-J", "source": "J", "kind": "distance", "nominal": J, "points": [[0.0, 0.0, 0.0], [0.0, 0.0, -J]], "direction": [0.0, 0.0, -1.0]},
        {"id": "rec-3", "markerId": "m-3", "source": "3", "kind": "thickness", "nominal": WALL_T, "points": [[R, 0.0, -J / 2.0], [Ri, 0.0, -J / 2.0]], "direction": [-1.0, 0.0, 0.0]}
    ]
