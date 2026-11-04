def build_face_tags(p):
    C = float(p["C"])
    return [{"name": "montaj", "surface": {"kind": "plane", "normal": [0.0, 0.0, 1.0], "offset": -(C + 2.8)}}]
