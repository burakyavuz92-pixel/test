import cadquery as cq

WALL_T = 3.0
END_T = 3.0
R_END_OUTER = 8.0
R_END_INNER = 5.0
R_OPEN_EDGE = 1.5
TOL = 1e-2

class _RowError(Exception):
    pass

def _req(p, k):
    v = p.get(k)
    if v is None:
        raise _RowError('Eksik ölçü: ' + k)
    return float(v)

def _geometry(p):
    A = _req(p, 'A')
    B = _req(p, 'B')
    C = _req(p, 'C')
    D = _req(p, 'D')
    E = _req(p, 'E')
    F = _req(p, 'F')
    G = _req(p, 'G')
    J = _req(p, 'J')
    if A <= 0 or B <= 0 or J <= 0:
        raise _RowError('Geçersiz boyut')
    if abs(B - 2.0 * G) > 1e-6:
        raise _RowError('B ve G ölçüleri uyuşmuyor')
    if min(C, D, E) < 0 or F < 0:
        raise _RowError('Negatif delik ölçüsü')
    ro = A / 2.0
    ri = ro - WALL_T
    if ri <= 0 or J <= END_T:
        raise _RowError('Gövde kesiti oluşturulamıyor')
    holes = []
    if C > 0:
        holes.append((0.0, B / 2.0, C / 2.0))
    if D > 0:
        holes.append((0.0, -B / 2.0, D / 2.0))
    if E > 0:
        holes.append((-F, 0.0, E / 2.0))
    for x, y, r in holes:
        if (x * x + y * y) ** 0.5 + r >= ri:
            raise _RowError('Delikler gövdeye sığmıyor')
    return ro, ri, J, holes

def _circle_edges(shape, z, r):
    found = []
    for e in shape.Edges():
        bb = e.BoundingBox()
        if (abs(bb.zmin - z) < TOL and abs(bb.zmax - z) < TOL
                and abs(bb.xlen / 2.0 - r) < TOL and abs(bb.ylen / 2.0 - r) < TOL):
            found.append(e)
    return found

def _round_edge(shape, z, r, rad):
    edges = _circle_edges(shape, z, r)
    if not edges:
        raise _RowError('Yuvarlama kenarı bulunamadı')
    return shape.fillet(rad, edges).Solids()[0]

def build_part(p):
    try:
        ro, ri, J, holes = _geometry(p)
    except _RowError as e:
        return {'error': str(e)}
    outer = cq.Solid.makeCylinder(ro, J, cq.Vector(0, 0, -J), cq.Vector(0, 0, 1))
    cav = cq.Solid.makeCylinder(ri, J - END_T + 1.0, cq.Vector(0, 0, -J - 1.0), cq.Vector(0, 0, 1))
    body = outer.cut(cav).Solids()[0]
    body = _round_edge(body, 0.0, ro, R_END_OUTER)
    body = _round_edge(body, -J, ro, R_OPEN_EDGE)
    body = _round_edge(body, -END_T, ri, R_END_INNER)
    for x, y, r in holes:
        h = cq.Solid.makeCylinder(r, END_T + 2.0, cq.Vector(x, y, -END_T - 1.0), cq.Vector(0, 0, 1))
        body = body.cut(h).Solids()[0]
    return cq.Workplane('XY').newObject([body])
