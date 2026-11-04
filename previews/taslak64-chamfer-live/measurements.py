import math

def build_measurements(p):
    A = float(p['A']); B = float(p['B']); C = float(p['C']); D = float(p['D'])
    E = float(p['E']); K = float(p['K'])
    F = float(p['F']); Fa = float(p['F__angleDeg'])
    G = float(p['G']); Ga = float(p['G__angleDeg'])
    J = float(p['J']); Ja = float(p['J__angleDeg'])
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
    def P(r, z):
        return [r, 0.0, z]
    def dia(rid, src, mk, nom, zc, rad):
        return {'id': rid, 'source': src, 'kind': 'diameter', 'nominal': nom, 'markerId': mk, 'center': [0.0, 0.0, zc], 'axis': [0.0, 0.0, 1.0], 'radius': rad}
    def dist(rid, src, mk, nom, a, b, d):
        return {'id': rid, 'source': src, 'kind': 'distance', 'nominal': nom, 'markerId': mk, 'points': [a, b], 'direction': d}
    def cham(rid, src, mk, leg, ang, a, b, d):
        return {'id': rid, 'source': src, 'kind': 'chamfer', 'nominal': leg, 'angleDeg': ang, 'markerId': mk, 'points': [a, b], 'direction': d}
    dn = [0.0, 0.0, -1.0]
    up = [0.0, 0.0, 1.0]
    return [
        dia('r1', 'A', 'm6', A, -C / 2.0, r_out),
        dia('r2', 'B', 'm7', B, -(F + D) / 2.0, rb),
        dist('r3', 'C', 'm2', C, P(r_out - rJ, 0.0), P(r_out, -C), dn),
        dist('r4', 'D', 'm8', D, P(rb + rF, 0.0), P(rb, -D), dn),
        dia('r5', 'E', 'm9', E, -(C + z_step) / 2.0, r_neck),
        dist('r6', '5', 'm1', L - z_step, P(r_lip, -z_step), P(r_end, -L), dn),
        dist('r7', '2,8', 'm10', z_step - C, P(r_neck, -C), P(r_neck, -z_step), dn),
        cham('r8', 'F', 'm4', F, Fa, P(rb + rF, 0.0), P(rb, -F), dn),
        cham('r9', 'G', 'm3', G, Ga, P(rk + rG, -L), P(rk, -(L - G)), up),
        cham('r10', 'J', 'm5', J, Ja, P(r_out - rJ, 0.0), P(r_out, -J), dn),
        dia('r11', 'Ø25 ±0,5', 'm11', 2.0 * r_lip, -(z_step + z_land) / 2.0, r_lip),
    ]
