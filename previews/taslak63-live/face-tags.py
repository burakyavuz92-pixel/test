import cadquery as cq
import math

def build_face_tags(p):
    E = float(p['E'])
    return [
        {'name': 'montaj', 'surface': {'kind': 'cylinder', 'axisOrigin': [0.0, 0.0, 0.0], 'axisDirection': [0.0, 0.0, 1.0], 'radius': E / 2.0}}
    ]
