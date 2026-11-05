import math

def _bad(mid, src, kind, nom, reason):
    return {'id': 'rec-' + mid, 'markerId': mid, 'source': src, 'kind': kind, 'nominal': nom, 'unresolved': reason}

def _hole(p, mid, src, cx, cy, zc):
    nom = _req(p, src)
    if nom <= 0:
        return _bad(mid, src, 'diameter', nom, 'Sifir olcu icin delik referansi yok')
    return {'id': 'rec-' + mid, 'markerId': mid, 'source': src, 'kind': 'diameter', 'nominal': nom, 'center': [cx, cy, zc], 'axis': [0.0, 0.0, 1.0], 'radius': nom / 2.0}

def build_measurements(p):
    try:
        ro, ri, J, _holes = _geometry(p)
        A = _req(p, 'A')
        B = _req(p, 'B')
        F = _req(p, 'F')
        G = _req(p, 'G')
        C = _req(p, 'C')
        D = _req(p, 'D')
        E = _req(p, 'E')
    except _RowError as e:
        return {'error': str(e)}
    zc = -END_T / 2.0
    out = []
    out.append({'id': 'rec-dim-A-sec', 'markerId': 'dim-A-sec', 'source': 'A', 'kind': 'diameter', 'nominal': A, 'center': [0.0, 0.0, -J / 2.0], 'axis': [0.0, 0.0, 1.0], 'radius': ro})
    if ro > R_END_OUTER:
        rf = (ro - R_END_OUTER) / 2.0
        out.append({'id': 'rec-dim-J-sec', 'markerId': 'dim-J-sec', 'source': 'J', 'kind': 'distance', 'nominal': J, 'points': [[rf, 0.0, 0.0], [ri, 0.0, -J]], 'direction': [0.0, 0.0, 1.0]})
    else:
        out.append(_bad('dim-J-sec', 'J', 'distance', J, 'Uc yuzunde olcum noktasi yok'))
    out.append({'id': 'rec-dim-F-front', 'markerId': 'dim-F-front', 'source': 'F', 'kind': 'distance', 'nominal': F, 'points': [[-F, 0.0, zc], [0.0, 0.0, zc]], 'direction': [1.0, 0.0, 0.0]})
    if C > 0 and D > 0:
        out.append({'id': 'rec-dim-B-front', 'markerId': 'dim-B-front', 'source': 'B', 'kind': 'distance', 'nominal': B, 'points': [[0.0, B / 2.0, zc], [0.0, -B / 2.0, zc]], 'direction': [0.0, 1.0, 0.0]})
    else:
        out.append(_bad('dim-B-front', 'B', 'distance', B, 'C veya D deligi yok'))
    if D > 0:
        out.append({'id': 'rec-dim-G-front', 'markerId': 'dim-G-front', 'source': 'G', 'kind': 'distance', 'nominal': G, 'points': [[0.0, 0.0, zc], [0.0, -B / 2.0, zc]], 'direction': [0.0, 1.0, 0.0]})
    else:
        out.append(_bad('dim-G-front', 'G', 'distance', G, 'D deligi yok'))
    out.append(_hole(p, 'dim-C-front', 'C', 0.0, B / 2.0, zc))
    out.append(_hole(p, 'dim-D-front', 'D', 0.0, -B / 2.0, zc))
    out.append(_hole(p, 'dim-E-front', 'E', -F, 0.0, zc))
    return out
