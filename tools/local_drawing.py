"""Resolve user-defined section traces against actual OCCT bounds; no hole semantics."""
import copy
import math


def resolve_local_sections(drawing, bounds):
    result = copy.deepcopy(drawing)
    if not any(s.get('kind') == 'localCentered' for s in result['sections']):
        return result
    if len(bounds) != 6 or not all(math.isfinite(x) for x in bounds):
        raise ValueError('Invalid native model bounds')
    xmin, ymin, zmin, xmax, ymax, zmax = bounds
    for section in result['sections']:
        if section.get('kind') != 'localCentered':
            continue
        vertical = section['direction'] == 'V'
        if section['direction'] not in ('V', 'H'):
            raise ValueError('Section direction must be V or H')
        offset, span = section['offsetMm'], section['spanMm']
        if not all(math.isfinite(x) for x in (offset, span)) or span < 0 or (offset != 0 and span == 0):
            raise ValueError('Invalid local section span/offset')
        normal = [1, 0, 0] if vertical else [0, 1, 0]
        if offset == 0:
            section.update(kind='planar', cuttingPlanes=[{'point': [0, 0, 0], 'normal': normal}])
            continue
        lo, hi = (ymin, ymax) if vertical else (xmin, xmax)
        margin = max(xmax-xmin, ymax-ymin, zmax-zmin, 1) * .05 + 1
        # The supplied span is centered at the origin, not at the target hole.
        lo, hi = min(lo, -span/2)-margin, max(hi, span/2)+margin
        path2 = [(0, hi), (0, span/2), (offset, span/2), (offset, -span/2), (0, -span/2), (0, lo)]
        path = [[x, y, 0] if vertical else [y, x, 0] for x, y in path2]
        planes = []
        for a, b in zip(path, path[1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            length = math.hypot(dx, dy)
            planes.append({'point': a, 'normal': [dy/length, -dx/length, 0]})
        section.update(kind='stepped', worldPath=path, sweepDirection=[0, 0, 1], cuttingPlanes=planes)
    return result
