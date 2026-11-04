"""Resolve dimension anchors from construction references, not Excel label names."""
import math,re
import numpy as np
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Torus,GeomAbs_Cylinder,GeomAbs_Circle
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
from PIL import Image,ImageDraw,ImageChops,ImageFilter


def resolve_anchors(recipe,shape,front,section,bounds,bindings=None):
    by_id={b["dimension"]["id"]:b for b in (bindings or [])}
    ops={o['id']:o for o in recipe['geometry']['operations']}
    frames={f['id']:f for f in recipe['geometry']['frames']}
    def primitive(id,seen=None):
        seen=set() if seen is None else seen
        if id in seen:raise ValueError('Cyclic annotation reference')
        if id=='unresolved':raise ValueError('CadQuery measurement requires an explicit geometric reference')
        seen.add(id);op=ops[id]
        if op['op']=='cylinder':
            a=op['args'];f=frames[op['frame']];x=np.array(f['xAxis']);z=np.array(f['zAxis']);basis=np.column_stack((x,np.cross(z,x),z))
            origin=np.array(f['origin'])+basis@np.array(a['origin']);direction=basis@np.array(a['direction']);direction=direction/np.linalg.norm(direction)
            return {'center':origin,'axis':direction,'radius':a['diameter']/2,'end':origin+direction*a['length'],'length':a['length']}
        if op['op']=='cut':return primitive(op['tool'],seen)
        if op['op'] in ('alias','join') and len(op.get('inputs',[]))==1:return primitive(op['inputs'][0],seen)
        raise ValueError('No unique cylindrical construction reference')
    fr,fu,fn=front;sr,su,sn=section
    def project(p,basis):return np.array([np.dot(p,basis[0]),np.dot(p,basis[1])])
    annotations=[];unresolved=[];omitted=[]
    for dim in recipe['drawing']['dimensions']:
        if not dim['effectiveVisible']:continue
        try:
            value=dim['nominal'];targets=dim['targets'];kind=dim['type'];axis=dim['axis']
            if value==0:omitted.append({'id':dim['id'],'reason':'zero dimension'});continue
            binding=by_id.get(dim['id']);dest_view=binding['view'] if binding else None;dest=front if dest_view=='front' else section
            item={'id':dim['id'],'dimension':dim}
            if binding:item['templateBinding']=binding
            if 'scriptReference' in dim:
                from script_measurements import anchor
                item.update(anchor(shape,dim['scriptReference'],value,front,section,dest_view));annotations.append(item);continue
            if 'relation' in dim:
                from measurement_contract import resolve
                measured=resolve(shape,dim['relation'])
                if abs(measured-value)>1e-5:raise ValueError(f'Final-body measurement {measured:g} differs from nominal {value:g}')
                surfaces=dim['relation']['surfaces'];first=surfaces[0];relation=dim['relation']['kind']
                if relation=='diameter':
                    direction=np.array(first['axisDirection']);center=np.array(first['axisOrigin'])
                    if dest_view=='section':
                        centers=[];ex=TopExp_Explorer(shape,TopAbs_EDGE)
                        while ex.More():
                            curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
                            if curve.GetType()==GeomAbs_Circle:
                                circle=curve.Circle();p=circle.Location();point=np.array([p.X(),p.Y(),p.Z()])
                                if abs(circle.Radius()*2-value)<1e-5 and np.linalg.norm(np.cross(point-center,direction))<1e-5:centers.append(project(point,section).tolist())
                            ex.Next()
                        radial=project(direction,section);perp=np.array([-radial[1],radial[0]])
                        if not centers or np.linalg.norm(perp)<1e-7:raise ValueError('No supported section diameter edge')
                        item.update(view='section',kind='sectionDiameter',centerOptions=centers,radius=value/2,radialDirection=perp/np.linalg.norm(perp))
                        annotations.append(item);continue
                    if abs(abs(np.dot(direction,fn))-1)>1e-6:raise ValueError('Diameter requires face-on front view')
                    item.update(view='front',kind='circle',center=project(center,front).tolist(),radius=value/2)
                elif relation=='axisDistance':
                    a=np.array(first['axisOrigin']);b=np.array(surfaces[1]['axisOrigin']);direction=np.array(dim['relation']['direction'],dtype=float);direction/=np.linalg.norm(direction)
                    b=a+direction*np.dot(b-a,direction);pa,pb=project(a,front),project(b,front)
                    if dest_view not in (None,'front') or abs(np.linalg.norm(pb-pa)-value)>1e-5:raise ValueError('Axis distance requires unobscured front view')
                    item.update(view='front',kind='linear',points=[pa.tolist(),pb.tolist()],axis='X' if abs(pb[0]-pa[0])>abs(pb[1]-pa[1]) else 'Y')
                elif relation in ('planeDistance','wallThickness'):
                    if dest_view not in (None,'section'):raise ValueError('Surface distance requires section view')
                    if relation=='planeDistance':
                        normal=np.array(first['normal']);other=surfaces[1]
                        a=normal*first['offset'];b=normal*np.dot(normal,other['normal'])*other['offset']
                    else:
                        normal=np.array(first['axisDirection'],dtype=float);radial=su-normal*np.dot(su,normal)
                        radial/=np.linalg.norm(radial);center=np.array(first['axisOrigin'])
                        a=center+radial*first['radius'];b=center+radial*surfaces[1]['radius']
                    pa,pb=project(a,section),project(b,section)
                    if abs(np.linalg.norm(pb-pa)-value)>1e-5:raise ValueError('Measurement hidden in section')
                    item.update(view='section',kind='linear',points=[pa.tolist(),pb.tolist()],axis='X' if abs(pb[0]-pa[0])>abs(pb[1]-pa[1]) else 'Y')
                else:
                    # Existing radius anchor resolver below requires a unique toroidal face.
                    pass
                if relation!='radius':
                    annotations.append(item);continue
            if kind=='radius':
                op=ops[targets[0]['operation']]
                if op['op']!='fillet':raise ValueError('Radius needs an explicit supported fillet reference')
                candidates=[];face_count=0;ex=TopExp_Explorer(shape,TopAbs_FACE)
                while ex.More():
                    face=TopoDS.Face_s(ex.Current());surface=BRepAdaptor_Surface(face)
                    if 'relation' in dim:
                        from measurement_contract import surface_matches
                        if not surface_matches(face,dim['relation']['surfaces'][0]):ex.Next();continue
                    if surface.GetType()==GeomAbs_Torus:
                        t=surface.Torus()
                        if abs(t.MinorRadius()-value)<1e-5:
                            face_count+=1
                            p=t.Location();center=np.array([p.X(),p.Y(),p.Z()]);direction=t.Axis().Direction();normal=np.array([direction.X(),direction.Y(),direction.Z()]);radial=su-normal*np.dot(su,normal)
                            if np.linalg.norm(radial)>1e-7:
                                radial/=np.linalg.norm(radial)
                                for degree in (45,135,225,315):
                                    angle=math.radians(degree);point=center+radial*(t.MajorRadius()+value*math.cos(angle))+normal*value*math.sin(angle)
                                    dist=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex(),face);dist.Perform()
                                    if dist.Value()<1e-5:
                                        candidates.append(point)
                                        opposite=center-radial*(t.MajorRadius()+value*math.cos(angle))+normal*value*math.sin(angle)
                                        other=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*opposite)).Vertex(),face);other.Perform()
                                        if other.Value()<1e-5:candidates.append(opposite)
                                        break
                    ex.Next()
                if face_count!=1 or not candidates:raise ValueError('Radius has no unique surviving toroidal face')
                item.update(view=dest_view or 'section',kind='leader',anchor=project(candidates[0],dest).tolist(),anchorOptions=[project(p,dest).tolist() for p in candidates])
            else:
                ps=[primitive(t['operation']) for t in targets]
                p=ps[0]
                if kind in ('diameter','pitchDiameter'):
                    if binding and dest_view=='section':
                        centers=[];ex=TopExp_Explorer(shape,TopAbs_EDGE)
                        while ex.More():
                            curve=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()))
                            if curve.GetType()==GeomAbs_Circle:
                                c=curve.Circle();loc=c.Location();point=np.array([loc.X(),loc.Y(),loc.Z()]);d=c.Axis().Direction();direction=np.array([d.X(),d.Y(),d.Z()])
                                if abs(c.Radius()*2-value)<1e-5 and abs(abs(np.dot(direction,p['axis']))-1)<1e-6 and np.linalg.norm(np.cross(point-p['center'],p['axis']))<1e-5:centers.append(project(point,section).tolist())
                            ex.Next()
                        if not centers:raise ValueError('No surviving diameter edge in section')
                        radial=project(p['axis'],section);perp=np.array([-radial[1],radial[0]])
                        if np.linalg.norm(perp)<1e-7:raise ValueError('Cylinder not edge-on in section')
                        perp/=np.linalg.norm(perp)
                        item.update(view='section',kind='sectionDiameter',centerOptions=centers,radius=value/2,radialDirection=perp.tolist())
                        annotations.append(item);continue
                    if kind=='pitchDiameter' or len(ps)!=1 or abs(abs(np.dot(p['axis'],fn))-1)>1e-6:raise ValueError('No supported face-on diameter')
                    if abs(p['radius']*2-value)>1e-5:raise ValueError('Dimension value differs from referenced diameter')
                    item.update(view='front',kind='circle',center=project(p['center'],front).tolist(),radius=p['radius'])
                elif axis in ('X','Y') and kind=='distance':
                    direction=np.eye(3)[0 if axis=='X' else 1]
                    a=ps[0]['center'];b=ps[1]['center'] if len(ps)==2 else np.zeros(3)
                    if len(ps)>2 or abs(abs(np.dot(a-b,direction))-value)>1e-5:raise ValueError('Distance has no matching center pair')
                    destination=front if not binding or dest_view=='front' else section
                    projected=project(direction,destination)
                    if np.linalg.norm(projected)<1e-7:raise ValueError('Measurement axis is hidden in selected view')
                    item.update(view=dest_view or 'front',kind='linear',points=[project(a,destination).tolist(),project(b,destination).tolist()],axis='X' if abs(projected[0])>abs(projected[1]) else 'Y')
                elif axis=='radial' and kind=='thickness' and len(ps)==1:
                    if abs(abs(p['axis'][2])-1)>1e-6:raise ValueError('Radial wall relation requires axial cylinders')
                    faces=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
                    while ex.More():
                        face=TopoDS.Face_s(ex.Current());surface=BRepAdaptor_Surface(face)
                        if surface.GetType()==GeomAbs_Cylinder:
                            c=surface.Cylinder();loc=c.Location();d=c.Axis().Direction()
                            if abs(d.Z())>.999999 and math.hypot(loc.X()-p['center'][0],loc.Y()-p['center'][1])<1e-5:
                                b=Bnd_Box();BRepBndLib.AddOptimal_s(face,b,False,False);faces.append((c.Radius(),b.Get()))
                        ex.Next()
                    pairs=[(a,b) for a in faces for b in faces if abs(a[0]-p['radius'])<1e-5 and abs(b[0]-a[0]-value)<1e-5 and min(a[1][5],b[1][5])>max(a[1][2],b[1][2])+1e-5]
                    if len(pairs)!=1:raise ValueError('No unique concentric wall pair')
                    a,b=pairs[0];z=(max(a[1][2],b[1][2])+min(a[1][5],b[1][5]))/2
                    center=p['center'].copy();center[2]=z
                    item.update(view='section',kind='linear',points=[project(center+su*a[0],section).tolist(),project(center+su*b[0],section).tolist()],axis='Y')
                elif axis=='Z' and kind in ('distance','thickness') and len(ps)==1:
                    if abs(abs(p['axis'][2])-1)>1e-6:raise ValueError('Z dimension needs axial construction')
                    lo=max(min(p['center'][2],p['end'][2]),bounds[2]);hi=min(max(p['center'][2],p['end'][2]),bounds[5])
                    if abs(hi-lo-value)>1e-5:raise ValueError(f'Axial extent {lo:g}..{hi:g} does not match {value:g}')
                    a=p['center'].copy();b=a.copy();a[2]=lo;b[2]=hi
                    if binding and dest_view!='section':raise ValueError('Axial measurement requires section view')
                    item.update(view='section',kind='linear',points=[project(a,section).tolist(),project(b,section).tolist()],axis='X')
                else:raise ValueError('Explicit anchor relation required for this measurement')
            annotations.append(item)
        except (ValueError,KeyError,IndexError) as ex:unresolved.append({'id':dim['id'],'reason':str(ex),'dimension':dim})
    return annotations,unresolved,omitted


class Annotations:
    def __init__(self,image,font,scale,check_geometry=False,avoid_lines=False):
        self.avoid_lines=avoid_lines;self.line_segments=[];self.image=image;self.draw=ImageDraw.Draw(image);self.font=font;self.S=scale;self.boxes=[];self.placed=[];self.labels=[];self.geometry=(np.asarray(image.convert('L'))<100) if check_geometry else None
    def line(self,a,b):
        self.draw.line((tuple(a),tuple(b)),fill='black',width=max(1,self.S))
        if self.avoid_lines:self.line_segments.append((np.array(a),np.array(b)))
    def arrow(self,tip,toward):
        tip=np.array(tip,dtype=float);v=np.array(toward,dtype=float)-tip;n=np.linalg.norm(v)
        if n<1e-7:return
        v/=n;side=np.array([-v[1],v[0]]);base=tip+v*12*self.S
        self.draw.polygon([tuple(tip),tuple(base+side*3.6*self.S),tuple(base-side*3.6*self.S)],fill='black')
    def text_layer(self,text):
        text_scale=20/18
        T=self.S*text_scale
        font=lambda size:self.font(round(size*text_scale))
        # Format asymmetric deviations locally; thread callouts do not match this suffix.
        match=re.fullmatch(r'(.*?) \(([+-][0-9]+(?:,[0-9]+)?(?:e[+-]?[0-9]+)?)/([+-][0-9]+(?:,[0-9]+)?(?:e[+-]?[0-9]+)?)\)',text)
        chunks=[(text,18,0,0)]
        if match:
            nominal,upper,lower=match.groups()
            main=font(18);small=font(12)
            probe=ImageDraw.Draw(Image.new('L',(1,1)))
            w=probe.textbbox((0,0),nominal,font=main)[2]
            tw=max(probe.textbbox((0,0),v,font=small)[2] for v in (upper,lower))
            chunks=[(nominal,18,0,4*T),('(',24,w+2*T,0),(upper,12,w+10*T,0),(lower,12,w+10*T,13*T),(')',24,w+12*T+tw,0)]
        layer=Image.new('RGB',(max(1,round(len(text)*24*T)),round(40*T)),'white');draw=ImageDraw.Draw(layer)
        for value,size,x,y in chunks:
            f=font(size);bb=draw.textbbox((0,0),value,font=f)
            draw.text((x-bb[0],y-bb[1]),value,font=f,fill='black')
        ink=ImageChops.invert(layer.convert('L'));bounds=ink.getbbox()
        return layer.crop(bounds) if bounds else layer.crop((0,0,1,1))
    def text_mask(self,layer):
        # One output pixel of clearance around actual glyphs, including rotated text.
        return ImageChops.invert(layer.convert('L')).point(lambda v:255 if v>20 else 0).filter(ImageFilter.MaxFilter(2*self.S+1))
    def paste_label(self,layer,position):
        self.image.paste(layer,position,self.text_mask(layer))
    def label(self,text,center,vertical=False,angle=None):
        layer=self.text_layer(text)
        # Padding accommodates the glyph mask's narrow clearance halo.
        padded=Image.new('RGB',(layer.width+2*self.S,layer.height+2*self.S),'white');padded.paste(layer,(self.S,self.S));layer=padded
        if angle is not None:layer=layer.rotate(-angle,expand=True,resample=Image.Resampling.BICUBIC,fillcolor='white')
        elif vertical:layer=layer.rotate(90,expand=True)
        x=int(center[0]-layer.width/2);y=int(center[1]-layer.height/2);box=(x,y,x+layer.width,y+layer.height)
        if x<25*self.S or y<50*self.S or box[2]>1720*self.S or box[3]>875*self.S:raise ValueError('Annotation outside drawing region')
        mask=self.text_mask(layer);active=np.asarray(mask)>0
        for prior,position in self.labels:
            px,py=position;left=max(x,px);top=max(y,py);right=min(box[2],px+prior.width);bottom=min(box[3],py+prior.height)
            if left<right and top<bottom:
                previous=np.asarray(self.text_mask(prior))>0
                if np.any(active[top-y:bottom-y,left-x:right-x]&previous[top-py:bottom-py,left-px:right-px]):raise ValueError('Annotation labels collide')
        if self.geometry is not None and np.count_nonzero(self.geometry[y:box[3],x:box[2]]&active)>10*self.S*self.S:raise ValueError('Annotation text intersects drawing geometry')
        if self.avoid_lines:
            for a,b in self.line_segments:
                samples=np.linspace(a,b,max(2,int(np.linalg.norm(b-a))+1));xx=np.rint(samples[:,0]-x).astype(int);yy=np.rint(samples[:,1]-y).astype(int);valid=(xx>=0)&(yy>=0)&(xx<active.shape[1])&(yy<active.shape[0])
                if np.any(active[yy[valid],xx[valid]]):raise ValueError('Annotation intersects another dimension line')
        self.paste_label(layer,(x,y));self.labels.append((layer,(x,y)));self.boxes.append(box);return box
    def leader(self,tip,label,text):
        label=np.array(label);tip=np.array(tip);direction=1 if label[0]<tip[0] else -1
        elbow=label+np.array([direction*25*self.S,0]);self.line(tip,elbow);self.arrow(tip,elbow);self.line(elbow,label);self.label(text,label)
    def linear(self,a,b,coordinate,text,horizontal):
        a=np.array(a);b=np.array(b)
        if horizontal:p=np.array([a[0],coordinate]);q=np.array([b[0],coordinate])
        else:p=np.array([coordinate,a[1]]);q=np.array([coordinate,b[1]])
        self.line(a,p);self.line(b,q);self.line(p,q)
        length=np.linalg.norm(q-p);self.arrow(p,q if length>30*self.S else p-(q-p));self.arrow(q,p if length>30*self.S else q+(q-p))
        center=(p+q)/2
        if length<100*self.S:
            center+=np.array([85*self.S,0]) if horizontal else np.array([0,-70*self.S])
        self.label(text,center,not horizontal)


def render_dimensions(image,font,S,items,pix_front,pix_section,value_text,check_geometry=False):
    painter=Annotations(image,font,S,check_geometry=check_geometry);failures=[];drawn=[];depth_lane=0;radius_lane=0;center_counts={}
    circles=[i for i in items if i['kind']=='circle'];largest=max(circles,key=lambda i:i['radius'],default=None)
    maincenter=np.array(pix_front(largest['center'])) if largest else np.array([750*S,460*S])
    mainradius=abs(pix_front([largest['center'][0]+largest['radius'],largest['center'][1]])[0]-maincenter[0]) if largest else 250*S
    for item in items:
        dim=item['dimension'];text=value_text(dim);pix=pix_front if item['view']=='front' else pix_section
        backup=image.copy();saved_boxes=list(painter.boxes);saved_labels=list(painter.labels)
        try:
            if item['kind']=='circle':
                center=np.array(item['center']);r=item['radius'];cp=np.array(pix(center))
                if item is largest:
                    painter.linear(pix(center+[0,-r]),pix(center+[0,r]),maincenter[0]-mainradius-65*S,text,False)
                else:
                    key=tuple(round(float(v),4) for v in center);index=center_counts.get(key,0);center_counts[key]=index+1
                    if cp[1]<maincenter[1]-25*S:
                        label=np.array([1110*S,110*S]);angle=45
                    elif cp[1]>maincenter[1]+25*S:
                        label=np.array([1110*S,800*S]);angle=-45
                    else:
                        label=np.array([335*S,(340+230*index)*S]);angle=135 if index%2==0 else 225
                    rad=math.radians(angle);tip=pix(center+r*np.array([math.cos(rad),math.sin(rad)]));painter.leader(tip,label,text)
            elif item['kind']=='linear':
                a,b=[pix(p) for p in item['points']]
                if item['view']=='front':coordinate=85*S if item['axis']=='X' else maincenter[0]+mainradius+65*S
                elif item['axis']=='X':coordinate=(75+35*depth_lane)*S;depth_lane+=1
                else:coordinate=70*S
                painter.linear(a,b,coordinate,text,item['axis']=='X')
            else:
                point=pix(item['anchor']);label=[280*S,(240+60*radius_lane)*S] if point[1]<350*S else [280*S,650*S];radius_lane+=1
                painter.leader(point,label,text)
            drawn.append(item['id'])
        except ValueError as ex:
            image.paste(backup,(0,0));painter.boxes=saved_boxes;painter.labels=saved_labels
            failures.append({'id':item['id'],'reason':str(ex),'dimension':dim})
    for layer,position in painter.labels:painter.paste_label(layer,position)
    return {'placed':drawn,'failed':failures}


def render_template_dimensions(image,font,S,items,pix_front,pix_section,layout,view_boxes,value_text):
    from template_layout import map_label,map_source_point,estimated_leader_target
    painter=Annotations(image,font,S,check_geometry=True);drawn=[];failures=[];records=[]
    page_scale=image.width/layout['sourcePixels'][0]
    for item in items:
        binding=item['templateBinding'];view=binding['view'];pix=pix_front if view=='front' else pix_section
        desired=map_label(binding,view_boxes[view],pix,page_scale)
        dim=item['dimension'];text=value_text(dim);kind=item['kind']
        text_height=painter.text_layer(text).height
        points=None;tip=None;horizontal=None
        if kind=='circle':
            center=np.array(item['center']);cp=np.array(pix(center));direction=desired-cp
            if np.linalg.norm(direction)<1e-7:failures.append({'id':item['id'],'reason':'Template label is at circle center','dimension':dim});continue
            # Convert pixel direction back to the view plane without changing the view.
            direction=np.array([direction[0],-direction[1]]);direction/=np.linalg.norm(direction)
            tip=np.array(pix(center+direction*item['radius']))
        elif kind=='sectionDiameter':
            center=min(item['centerOptions'],key=lambda c:np.linalg.norm(np.array(pix(c))-desired))
            radial=np.array(item['radialDirection']);points=[np.array(pix(np.array(center)+radial*item['radius'])),np.array(pix(np.array(center)-radial*item['radius']))]
            horizontal=abs(points[1][0]-points[0][0])>abs(points[1][1]-points[0][1])
        elif kind=='linear':
            points=[np.array(pix(p)) for p in item['points']];horizontal=item['axis']=='X'
        else:
            expected=map_source_point(binding,view_boxes[view],pix,estimated_leader_target(binding))
            tip=min((np.array(pix(p)) for p in item.get('anchorOptions',[item['anchor']])),key=lambda p:np.linalg.norm(p-expected))
        base=desired.copy()
        placed=False;reason='No collision-free template-local placement'
        # Candidate shifts are relative to the detected template position, never a new view.
        shifts=[(0,0)]
        if points is not None:
            for distance in (4,8,12,16,24,32):
                shifts.extend([(0,-distance),(0,distance)] if horizontal else [(-distance,0),(distance,0)])
        else:
            shifts += [(dx,dy) for distance in (4,8,12,16,24,32) for dx,dy in [(0,-distance),(0,distance),(-distance,0),(distance,0)]]
        shifts += sorted([(dx,dy) for dx in (-64,-48,-32,-24,-16,0,16,24,32,48,64) for dy in (-64,-48,-32,-24,-16,0,16,24,32,48,64) if dx and dy],key=lambda d:d[0]*d[0]+d[1]*d[1])
        for dx,dy in shifts:
            candidate=base+np.array([dx,dy])*S
            backup=image.copy();old_boxes=list(painter.boxes);old_labels=list(painter.labels)
            try:
                if points is not None:
                    a,b=points
                    # Text above a horizontal line / left of a vertical line.
                    clearance=text_height/2+2*S
                    coordinate=candidate[1]+clearance if horizontal else candidate[0]+clearance
                    p=np.array([a[0],coordinate]) if horizontal else np.array([coordinate,a[1]])
                    q=np.array([b[0],coordinate]) if horizontal else np.array([coordinate,b[1]])
                    painter.line(a,p);painter.line(b,q);painter.line(p,q)
                    length=np.linalg.norm(p-q);painter.arrow(p,q if length>30*S else p-(q-p));painter.arrow(q,p if length>30*S else q+(q-p))
                    painter.label(text,candidate,vertical=not horizontal)
                else:
                    if np.linalg.norm(tip-candidate)>120*S:raise ValueError('Leader exceeds local view placement limit')
                    painter.line(tip,candidate);painter.arrow(tip,candidate)
                    direction=tip-candidate;angle=math.degrees(math.atan2(direction[1],direction[0]));angle=(angle+90)%180-90
                    painter.label(text,candidate,angle=angle)
                drawn.append(item['id']);records.append({'id':item['id'],'sourceLabel':binding['marker']['label'],'view':view,'templateLabelPixels':(desired/S).tolist(),'placedLabelPixels':(candidate/S).tolist()});placed=True;break
            except ValueError as ex:
                reason=str(ex);image.paste(backup,(0,0));painter.boxes=old_boxes;painter.labels=old_labels
        if not placed:failures.append({'id':item['id'],'reason':reason,'dimension':dim})
    for layer,position in painter.labels:painter.paste_label(layer,position)
    return {'placed':drawn,'failed':failures,'templatePlacements':records}
