ZERO = 0.0
ONE = 1.0
TWO = 2.0

def build_face_tags(p):
    if p.get('A') is None or p.get('B') is None:
        return {'error':'Yüzey için A veya B ölçüsü eksik.'}
    return [{'name':'dis','surface':{'kind':'cylinder','axisOrigin':[ZERO,ZERO,ZERO],'axisDirection':[ZERO,ZERO,ONE],'radius':p['A']/TWO}},{'name':'montaj','surface':{'kind':'plane','normal':[ZERO,ZERO,ONE],'offset':-p['B']}}]
