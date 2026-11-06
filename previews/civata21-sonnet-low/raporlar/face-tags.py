import cadquery as cq

def build_face_tags(p):
    A=p['A'];D=p['D']
    return [{'name':'dis','surface':{'kind':'cylinder','axisOrigin':[0,0,0],'axisDirection':[0,0,1],'radius':A/2}},{'name':'montaj','surface':{'kind':'plane','normal':[0,0,1],'offset':-D}}]
