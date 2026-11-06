def build_measurements(p):
    try:
        solid = build_part(p)
        if isinstance(solid, dict):
            return solid
        a,b,c,d,e,l = (p[k] for k in ('A','B','C','D','E','L'))
        angle = p['E__angleDeg']
        r = a/TWO
        run = math.sqrt(TWO*FIVE-ONE)
        zmax = -b-d+run
        za = (-e-b+FIVE+run)/TWO
        zc = -b+FIVE/TWO
        return [
            {'id':'A_1','markerId':'A_1','source':'A','kind':'diameter','nominal':a,'center':[ZERO,ZERO,za],'axis':[ZERO,ZERO,ONE],'radius':r},
            {'id':'B_1','markerId':'B_1','source':'B','kind':'distance','nominal':b,'points':[[ZERO,ZERO,ZERO],[ZERO,ZERO,-b]],'direction':[ZERO,ZERO,ONE]},
            {'id':'C_1','markerId':'C_1','source':'C','kind':'distance','nominal':c,'points':[[ZERO,-c/TWO,zc],[ZERO,c/TWO,zc]],'direction':[ZERO,ONE,ZERO]},
            {'id':'D_1','markerId':'D_1','source':'D','kind':'thickness','nominal':d,'points':[[ZERO,ZERO,-b],[ZERO,ZERO,-b-d]],'direction':[ZERO,ZERO,ONE]},
            {'id':'E_1','markerId':'E_1','source':'E','kind':'chamfer','nominal':e,'points':[[ZERO,-(r-e*math.tan(math.radians(angle))),ZERO],[ZERO,-r,-e]],'direction':[ZERO,ZERO,ONE],'angleDeg':angle},
            {'id':'L_1','markerId':'L_1','source':'L','kind':'diameter','nominal':l,'center':[ZERO,ZERO,zmax],'axis':[ZERO,ZERO,ONE],'radius':l/TWO},
            {'id':'H_1','source':'H','kind':'distance','nominal':p.get('H'),'unresolved':'H başlık alanında; geometrik ölçü ilişkisi belirtilmemiş.'}
        ]
    except (TypeError, ValueError, KeyError):
        return {'error':'Ölçü verisi geçersiz veya eksik.'}
