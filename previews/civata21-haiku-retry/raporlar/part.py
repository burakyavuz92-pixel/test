import math
import cadquery as cq

NECK_LENGTH = 5.0
CONE_LENGTH = 2.5
HEAD_ROUND_R = 5.0
HEAD_EDGE_STEP = 1.0


def _num(p, key):
    v = p.get(key)
    if v is None:
        return None, key + ' ölçüsü boş'
    try:
        f = float(v)
    except Exception:
        return None, key + ' ölçüsü sayısal değil'
    if not math.isfinite(f) or f <= 0:
        return None, key + ' ölçüsü pozitif olmalı'
    return f, None


def _chamfer(p):
    e = p.get('E')
    if e is None:
        return 0.0, 0.0, None
    try:
        e = float(e)
    except Exception:
        return None, None, 'E pah değeri sayısal değil'
    if not math.isfinite(e) or e < 0:
        return None, None, 'E pah değeri geçersiz'
    if e == 0:
        return 0.0, 0.0, None
    ang = p.get('E__angleDeg')
    if ang is None:
        return None, None, 'E pah açısı eksik'
    try:
        ang = float(ang)
    except Exception:
        return None, None, 'E pah açısı sayısal değil'
    if not (0.0 < ang < 90.0):
        return None, None, 'E pah açısı geçersiz'
    axial = e / math.tan(math.radians(ang))
    return e, axial, None


def build_part(p):
    a, err = _num(p, 'A')
    if err:
        return {'error': err}
    b, err = _num(p, 'B')
    if err:
        return {'error': err}
    c, err = _num(p, 'C')
    if err:
        return {'error': err}
    d, err = _num(p, 'D')
    if err:
        return {'error': err}
    l, err = _num(p, 'L')
    if err:
        return {'error': err}
    ec, axial, err = _chamfer(p)
    if err:
        return {'error': err}

    rs = a / 2.0
    rc = c / 2.0
    rh = l / 2.0
    if rh <= rc:
        return {'error': 'Başlık çapı kaplama çapından büyük olmalı'}
    if rh <= rs:
        return {'error': 'Başlık çapı gövde çapından büyük olmalı'}
    if l - 2.0 * HEAD_EDGE_STEP <= 0:
        return {'error': 'Başlık çapı üst yüzey için çok küçük'}
    if ec >= rs:
        return {'error': 'Pah gövde yarıçapından büyük'}
    if b - NECK_LENGTH - CONE_LENGTH <= axial + 1e-9:
        return {'error': 'Gövde boyu B pah ve boyun için yetersiz'}
    if math.hypot(HEAD_EDGE_STEP, d) > 2.0 * HEAD_ROUND_R:
        return {'error': 'Başlık kalınlığı R5 kenar yayına uymuyor'}

    zu = -b
    zt = -(b + d)
    p6 = (rh, zu)
    p7 = (rh - HEAD_EDGE_STEP, zt)
    vr = p7[0] - p6[0]
    vz = p7[1] - p6[1]
    lc = math.hypot(vr, vz)
    h = math.sqrt(HEAD_ROUND_R ** 2 - (lc / 2.0) ** 2)
    mx = (p6[0] + p7[0]) / 2.0
    mz = (p6[1] + p7[1]) / 2.0
    nr = vz / lc
    nz = -vr / lc
    cr = mx + h * nr
    cz = mz + h * nz
    amr = cr - HEAD_ROUND_R * nr
    amz = cz - HEAD_ROUND_R * nz

    wp = cq.Workplane('XY').moveTo(0.0, 0.0)
    if ec > 0:
        wp = wp.lineTo(rs - ec, 0.0).lineTo(rs, -axial)
    else:
        wp = wp.lineTo(rs, 0.0)
    wp = wp.lineTo(rs, -(b - NECK_LENGTH - CONE_LENGTH))
    wp = wp.lineTo(rc, -(b - NECK_LENGTH))
    wp = wp.lineTo(rc, zu).lineTo(rh, zu)
    wp = wp.threePointArc((amr, amz), p7)
    wp = wp.lineTo(0.0, zt).close()

    solid = wp.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    solid = solid.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
    return solid
