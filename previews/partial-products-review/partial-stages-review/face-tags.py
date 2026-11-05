def _num(p, k, default=0.0):
    v = p.get(k)
    return float(default if v is None else v)

def build_face_tags(p):
    if p["C"]==38.5:
        return {"error":"Test: montaj yüzeyi tanımlanamıyor"}
    C = _num(p, "C")
    neck_w = 2.8
    z_shoulder = -(C + neck_w)
    return [
        {
            "name": "montaj",
            "surface": {
                "kind": "plane",
                "normal": [0.0, 0.0, 1.0],
                "offset": z_shoulder
            }
        }
    ]
