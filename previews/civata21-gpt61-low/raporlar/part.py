import cadquery as cq
import math
ZERO = 0.0
ONE = 1.0
TWO = 2.0
FIVE = 5.0
NINETY = 90.0
FULL = 360.0

def build_part(p):
    try:
        a,b,c,d,e,l = (p[k] for k in ('A','B','C','D','E','L'))
        angle = p['E__angleDeg']
        if any(v is None for v in (a,b,c,d,e,l,angle)):
            return {'error':'Gerekli ölçü boş.'}
        if min(a,b,c,d,l) <= ZERO or e < ZERO or not ZERO < angle < NINETY:
            return {'error':'Çap, boy veya pah açısı geçersiz.'}
        r = a/TWO
        neck = c/TWO
        head = l/TWO
        run = math.sqrt(TWO*FIVE*ONE-ONE*ONE)
        center = -b-d+run
        near = d-run
        if abs(near) >= FIVE or not ZERO < run < d:
            return {'error':'Baş kalınlığı R5 yayına uygun değil.'}
        end_radius = head-ONE
        start_radius = head-FIVE+math.sqrt(FIVE*FIVE-near*near)
        chamfer_drop = e*math.tan(math.radians(angle))
        taper = run
        if r <= chamfer_drop or neck < r or start_radius <= neck or b <= FIVE+taper+e or end_radius <= ZERO:
            return {'error':'Pah, boyun veya baş ölçüleri çakışıyor.'}
        profile = cq.Workplane('XZ').moveTo(ZERO,ZERO).lineTo(r-chamfer_drop,ZERO)
        if e > ZERO:
            profile = profile.lineTo(r,-e)
        profile = profile.lineTo(r,-b+FIVE+taper).lineTo(neck,-b+FIVE).lineTo(neck,-b).lineTo(start_radius,-b)
        profile = profile.threePointArc((head,center),(end_radius,-b-d)).lineTo(ZERO,-b-d).close()
        return profile.revolve(FULL,(ZERO,ZERO),(ZERO,ONE)).val()
    except (TypeError,ValueError,KeyError):
        return {'error':'Ölçü verisi geçersiz veya eksik.'}
