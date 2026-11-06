import math
import cadquery as cq

T_WALL = 3.0
T_BASE = 3.0
R_CLOSED_OUT = 8.0
R_CLOSED_IN = 5.0
R_OPEN_RIM = 1.5


def _check(p):
    keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'J']
    for k in keys:
        if p.get(k) is None:
            return None, 'eksik olcu: ' + k
    v = {}
    for k in keys:
        v[k] = float(p[k])
    if v['A'] <= 0 or v['J'] <= 0:
        return None, 'ana olcu sifir veya negatif'
    ro = v['A'] / 2.0
    if ro - R_CLOSED_OUT <= 0:
        return None, 'govde capi kose yaricapina yetmiyor'
    if v['J'] <= R_OPEN_RIM + T_BASE + R_CLOSED_IN:
        return None, 'govde boyu kose detaylarina yetmiyor'
    if abs(v['G'] - v['B'] / 2.0) > 1e-6:
        return None, 'B ve G olculeri uyusmuyor'
    flat = ro - R_CLOSED_OUT
    cand = [(0.0, v['B'] / 2.0, v['C']),
            (0.0, -v['B'] / 2.0, v['D']),
            (-v['F'], 0.0, v['E'])]
    holes = []
    for x, y, d in cand:
        if d < 0:
            return None, 'negatif delik capi'
        if d > 0:
            if math.hypot(x, y) + d / 2.0 >= flat:
                return None, 'delik taban duzlemi disina tasiyor'
            holes.append((x, y, d))
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            x1, y1, d1 = holes[i]
            x2, y2, d2 = holes[j]
            if math.hypot(x1 - x2, y1 - y2) <= (d1 + d2) / 2.0:
                return None, 'delikler birbiriyle cakisiyor'
    return (v, holes), None


def build_part(p):
    chk, err = _check(p)
    if err is not None:
        return {'error': err}
    v, holes = chk
    ro = v['A'] / 2.0
    ri = ro - T_WALL
    J = v['J']
    s = math.sqrt(0.5)
    rf = R_CLOSED_OUT
    rfi = R_CLOSED_IN
    rr = R_OPEN_RIM
    # Local plane: x = radius, y = world Z (origin at closed end outer face centre)
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    prof = (
        cq.Workplane(plane)
        .moveTo(0, 0)
        .lineTo(ro - rf, 0)
        .threePointArc((ro - rf + rf * s, -rf + rf * s), (ro, -rf))
        .lineTo(ro, -J + rr)
        .threePointArc((ro - rr + rr * s, -J + rr - rr * s), (ro - rr, -J))
        .lineTo(ri, -J)
        .lineTo(ri, -T_BASE - rfi)
        .threePointArc((ri - rfi + rfi * s, -T_BASE - rfi + rfi * s), (ri - rfi, -T_BASE))
        .lineTo(0, -T_BASE)
        .close()
    )
    body = prof.revolve(360.0, (0, 0, 0), (0, 1, 0))
    for x, y, d in holes:
        cyl = cq.Solid.makeCylinder(d / 2.0, T_BASE + 2.0,
                                    cq.Vector(x, y, -T_BASE - 1.0),
                                    cq.Vector(0, 0, 1))
        body = body.cut(cyl)
    return body
