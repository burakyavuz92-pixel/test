import cadquery as cq
import math

def build_part(p):
    A=p['A'];B=p['B'];C=p['C'];D=p['D'];E=p['E'];L=p['L']
    if None in (A,B,C,D,E,L):
        return {'error':'Eksik parametre'}
    if L<=C or L<=A:
        return {'error':'Baş çapı gövdeden küçük'}
    if E>=A/2 or B<=D+5:
        return {'error':'Geçersiz pah veya uzunluk'}
    zb=-D
    zn=-(D+5)
    zt=-(D+B)
    pts=[(0,0),(L/2,0),(L/2,zb),(C/2,zb),(C/2,zn),(A/2,zn-1.5),(A/2,zt+E),(A/2-E,zt),(0,zt)]
    w=cq.Workplane('XZ').polyline(pts).close().revolve(360,(0,0,0),(0,1,0))
    try:
        r=min(5.0,D-0.3)
        w=w.edges(cq.selectors.RadiusNthSelector(0,directionMax=True)).edges('>Z').fillet(r)
    except Exception:
        pass
    return w
