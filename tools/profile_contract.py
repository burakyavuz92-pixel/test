"""Lower explicit profile chains; never invent a closing edge."""
import copy
import math


def normalize_loop(source):
    loop = copy.deepcopy(source)
    def point(p):
        if not isinstance(p, list) or len(p) != 2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in p):
            raise ValueError('Profile point must contain two finite numbers')
        return p
    def same(a,b):
        return math.dist(point(a),point(b)) <= 1e-7
    if loop['kind'] == 'polyline':
        points=loop['points']
        if len(points)<3:raise ValueError('Polyline requires at least three vertices')
        for p in points:point(p)
        if same(points[0],points[-1]):points.pop()
        if len(points)<3:raise ValueError('Polyline requires at least three vertices')
        if any(same(a,b) for a,b in zip(points,points[1:]+points[:1])):raise ValueError('Zero-length polyline edge')
        if loop.get('closed',True) is not True:raise ValueError('Profile polyline must be closed')
        loop['closed']=True
    elif loop['kind'] == 'path':
        chain='start' in loop
        if chain and 'closed' in loop:raise ValueError('Path uses explicit endpoint closure, not closed flag')
        segments=loop['segments']
        if not segments:raise ValueError('Empty profile path')
        start=point(loop.pop('start')) if chain else point(segments[0]['start'])
        previous=start
        for seg in segments:
            if chain:
                if 'start' in seg:raise ValueError('Chain segment must not repeat start')
                seg['start']=list(previous)
            elif not same(previous,seg['start']):raise ValueError('Disconnected profile path')
            end=point(seg['end'])
            if same(previous,end):raise ValueError('Zero-length profile segment')
            if seg['kind']=='arc':point(seg['mid'])
            elif seg['kind']!='line':raise ValueError('Unknown profile segment')
            previous=end
        if not same(previous,start):raise ValueError('Profile path is not closed: final end must equal initial start; no edge added')
        if loop.get('closed',True) is not True:raise ValueError('Profile path must be closed')
        loop['closed']=True
    return loop
