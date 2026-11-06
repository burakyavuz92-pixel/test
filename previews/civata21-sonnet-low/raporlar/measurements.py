def build_measurements(p):
    A=p['A'];B=p['B'];C=p['C'];D=p['D'];E=p['E'];L=p['L']
    zb=-D
    zt=-(D+B)
    recs=[]
    recs.append({'id':'A','markerId':'A','source':'A','kind':'diameter','nominal':A,'center':[0,0,zt],'axis':[0,0,1],'radius':A/2})
    recs.append({'id':'B','markerId':'B','source':'B','kind':'distance','nominal':B,'points':[[0,0,zb],[0,0,zt]],'direction':[0,0,1]})
    recs.append({'id':'C','markerId':'C','source':'C','kind':'distance','nominal':C,'points':[[0,-C/2,zb],[0,C/2,zb]],'direction':[0,1,0]})
    recs.append({'id':'D','markerId':'D','source':'D','kind':'distance','nominal':D,'points':[[0,0,0],[0,0,zb]],'direction':[0,0,1]})
    recs.append({'id':'E','markerId':'E','source':'E','kind':'chamfer','nominal':E,'points':[[A/2,0,zt+E],[A/2-E,0,zt]],'direction':[0,0,1],'angleDeg':p['E__angleDeg']})
    recs.append({'id':'L','markerId':'L','source':'L','kind':'diameter','nominal':L,'center':[0,0,0],'axis':[0,0,1],'radius':L/2})
    return recs