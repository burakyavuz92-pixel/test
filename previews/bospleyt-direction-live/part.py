import cadquery as cq

WALL_T = 3.0


def _val(p, key):
    v = p.get(key)
    if v is None:
        return None
    return float(v)


def build_part(p):
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
    try:
        # Outer body: closed end face centred on origin at z=0, body toward -Z
        outer = cq.Workplane("XY").circle(R).extrude(-J)
        outer = outer.edges(">Z").fillet(D)
        # Inner cavity: open end at z=-J, floor at z=-WALL_T
        cav = (
            cq.Workplane("XY")
            .workplane(offset=-WALL_T)
            .circle(Ri)
            .extrude(-(J + 1.0 - WALL_T))
        )
        cav = cav.edges(">Z").fillet(E)
        body = outer.cut(cav)
    except Exception:
        return {"error": "Geometri oluşturulamadı"}
    return body
