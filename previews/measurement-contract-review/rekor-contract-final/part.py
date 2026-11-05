import math
import cadquery as cq

def _num(p, k):
    v = p.get(k)
    return None if v is None else float(v)

def _chamfer(p, k):
    leg = _num(p, k)
    if leg is None or leg == 0:
        return (0.0, 0.0)
    ang = _num(p, k + '__angleDeg')
    if ang is None or not (0.0 < ang < 90.0):
        return None
    return (leg, leg * math.tan(math.radians(ang)))

def _values(p):
    v = {}
    for k in ['A', 'B', 'C', 'D', 'E', 'K', 'L', 'M', 'N']:
        x = _num(p, k)
        if x is None:
            return None, 'Eksik ölçü verisi: ' + k
        v[k] = x
    if v['A'] <= 0 or v['B'] <= 0 or v['K'] <= 0 or v['C'] <= 0 or v['M'] <= 0 or v['D'] < 0 or v['E'] <= 0 or v['L'] <= 0 or v['N'] <= 0:
        return None, 'Ölçü değeri geçersiz'
    return v, None

def build_part(p):
    v, err = _values(p)
    if err:
        return {'error': err}
    J = _chamfer(p, 'J')
    F = _chamfer(p, 'F')
    G = _chamfer(p, 'G')
    if J is None or F is None or G is None:
        return {'error': 'Pah açısı verisi eksik'}
    Ja, Jr = J
    Fa, Fr = F
    Ga, Gr = G
    C, M, D = v['C'], v['M'], v['D']
    ro = v['A'] / 2.0
    Rb = v['B'] / 2.0
    Rk = v['K'] / 2.0
    Re = v['E'] / 2.0
    Rl = v['L'] / 2.0
    Rn = v['N'] / 2.0
    if D == 0:
        if abs(v['B'] - v['K']) > 1e-9:
            return {'error': 'Derinlik sıfırken B ve K uyuşmuyor'}
        Rbl = Rk
    else:
        Rbl = Rb
    total = C + M + 5.0
    if D > 0 and D <= Fa:
        return {'error': 'B cep derinliği pah boyundan küçük'}
    if D >= total - Ga:
        return {'error': 'Delik derinliği toplam boya uymuyor'}
    if Ja >= C:
        return {'error': 'Dış pah gövde boyunu aşıyor'}
    if ro - Jr <= Rbl + Fr:
        return {'error': 'Sol yüz duvar kalınlığı yetersiz'}
    if Rn <= Rk + Gr:
        return {'error': 'Sağ yüz duvar kalınlığı yetersiz'}
    if not (Rl > Re and Rl > Rn):
        return {'error': 'Flanş çapı yetersiz'}
    zs = -(C + M)
    zl = zs - 1.0
    zr = -total
    pts = [(ro - Jr, 0.0), (ro, -Ja), (ro, -C), (Re, -C), (Re, zs), (Rl, zs), (Rl, zl), (Rn, zr), (Rk + Gr, zr), (Rk, zr + Ga)]
    if D > 0:
        pts += [(Rk, -D), (Rb, -D), (Rb, -Fa)]
    else:
        pts += [(Rk, -Fa)]
    pts.append((Rbl + Fr, 0.0))
    clean = []
    for q in pts:
        if clean and abs(q[0] - clean[-1][0]) < 1e-9 and abs(q[1] - clean[-1][1]) < 1e-9:
            continue
        clean.append(q)
    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) < 1e-9 and abs(clean[0][1] - clean[-1][1]) < 1e-9:
        clean.pop()
    prof = cq.Workplane('XZ').polyline(clean).close()
    return prof.revolve(360, (0, 0, 0), (0, 1, 0))
