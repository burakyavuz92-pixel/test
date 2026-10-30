import cadquery as cq
import math

def build_part(p):
    A = float(p["A"])
    B = float(p["B"]) if p.get("B") is not None else 0.0
    C = float(p["C"]) if p.get("C") is not None else 0.0
    D = float(p["D"])
    E = float(p["E"])
    F = float(p["F"]) if p.get("F") is not None else 0.0
    G = float(p["G"]) if p.get("G") is not None else 0.0
    I = float(p["I"]) if p.get("I") is not None else 0.0
    J = float(p["J"])

    t = 3.0
    depth = 33.0
    r_out_bend = 8.0
    r_in_bend = r_out_bend - t
    r_rim = 1.5
    r_bore_fillet = 2.0

    R_out = A / 2.0
    R_in = R_out - t
    R_flat = R_out - r_out_bend
    z_rim_center = depth - r_rim

    s45 = math.sqrt(0.5)

    # 1. Main cup body revolved around Z axis (exterior flat face at Z = 0, open rim at Z = 33)
    cup = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(R_flat, 0.0)
        .threePointArc(
            (R_flat + r_out_bend * s45, r_out_bend * (1.0 - s45)),
            (R_out, r_out_bend),
        )
        .lineTo(R_out, z_rim_center)
        .threePointArc(
            (R_out - r_rim, depth),
            (R_in, z_rim_center),
        )
        .lineTo(R_in, r_out_bend)
        .threePointArc(
            (R_flat + r_in_bend * s45, r_out_bend - r_in_bend * s45),
            (R_flat, t),
        )
        .lineTo(0.0, t)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )

    # 2. Cut mounting hole for the boss and through-holes G and I in the flat face
    r_boss_inner = J / 2.0
    r_boss_outer = D / 2.0
    r_fillet_end = min(r_boss_inner + r_bore_fillet, r_boss_outer - 0.2)
    r_eff_fillet = r_fillet_end - r_boss_inner
    r_cut_mid = 0.5 * (r_fillet_end + r_boss_outer)

    cut_cyl = (
        cq.Workplane("XY")
        .workplane(offset=-1.0)
        .center(-B, 0.0)
        .circle(r_cut_mid)
        .extrude(t + 2.0)
    )
    cup = cup.cut(cut_cyl)

    if G > 0:
        hole_g = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .center(0.0, C / 2.0)
            .circle(G / 2.0)
            .extrude(t + 2.0)
        )
        cup = cup.cut(hole_g)

    if I > 0:
        hole_i = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .center(0.0, -C / 2.0)
            .circle(I / 2.0)
            .extrude(t + 2.0)
        )
        cup = cup.cut(hole_i)

    # 3. Revolved boss (Detail B) positioned at (-B, 0)
    r_flange = r_boss_outer + 1.5
    z_start = -F
    z_end = -F + E

    boss_wp = cq.Workplane("XZ").moveTo(r_boss_inner, z_start + r_eff_fillet)
    if r_eff_fillet > 1e-3:
        boss_wp = boss_wp.threePointArc(
            (
                r_boss_inner + r_eff_fillet * (1.0 - s45),
                z_start + r_eff_fillet * (1.0 - s45),
            ),
            (r_fillet_end, z_start),
        )
    else:
        boss_wp = boss_wp.lineTo(r_fillet_end, z_start)

    if z_end > t:
        boss_wp = (
            boss_wp.lineTo(r_boss_outer, z_start)
            .lineTo(r_boss_outer, t)
            .lineTo(r_flange, t)
            .lineTo(r_flange, z_end)
            .lineTo(r_boss_inner, z_end)
            .close()
        )
    else:
        boss_wp = (
            boss_wp.lineTo(r_boss_outer, z_start)
            .lineTo(r_boss_outer, z_end)
            .lineTo(r_boss_inner, z_end)
            .close()
        )

    boss = boss_wp.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)).translate(
        (-B, 0.0, 0.0)
    )

    result = cup.union(boss)
    return result
