"""View-local dimension bands; CAD anchors and source visibility are unchanged."""
import numpy as np

def side_for(horizontal,desired,bounds):
 x0,y0,x1,y1=bounds
 return ('top' if desired[1]<(y0+y1)/2 else 'bottom') if horizontal else ('left' if desired[0]<(x0+x1)/2 else 'right')

def screen_bounds(pix,b):
 points=[pix([b[0],b[1]]),pix([b[2],b[3]])];a=np.asarray(points)
 return [float(a[:,0].min()),float(a[:,1].min()),float(a[:,0].max()),float(a[:,1].max())]

def band_coordinate(bounds,side,offset):
 return {'left':bounds[0]-offset,'right':bounds[2]+offset,'top':bounds[1]-offset,'bottom':bounds[3]+offset}[side]

def crossing(a,b,c,d):
 def orient(p,q,r):
  x=q-p;y=r-p;return x[0]*y[1]-x[1]*y[0]
 return orient(a,b,c)*orient(a,b,d)<-1e-7 and orient(c,d,a)*orient(c,d,b)<-1e-7

def render(image,font,S,items,pix_front,pix_section,layout,view_boxes,value_text):
 from dimension_annotations import Annotations
 from template_layout import map_label
 painter=Annotations(image,font,S,check_geometry=True,avoid_lines=True);failed=[];drawn=[];records=[];linear=[];leaders=[]
 for item in items:
  binding=item['templateBinding'];view=binding['view'];pix=pix_front if view=='front' else pix_section;bounds=screen_bounds(pix,view_boxes[view]);desired=map_label(binding,view_boxes[view],pix,image.width/layout['sourcePixels'][0]);kind=item['kind']
  if kind=='linear':
   points=[np.asarray(pix(p),float) for p in item['points']];horizontal=item['axis']=='X'
  elif kind=='sectionDiameter':
   center=min(item['centerOptions'],key=lambda c:np.linalg.norm(np.asarray(pix(c))-desired));r=np.asarray(item['radialDirection'])*item['radius'];points=[np.asarray(pix(np.asarray(center)-r)),np.asarray(pix(np.asarray(center)+r))];horizontal=abs(points[1][0]-points[0][0])>abs(points[1][1]-points[0][1])
  elif kind=='circle' and abs(item['radius']*2-(view_boxes[view][3]-view_boxes[view][1]))<1e-4:
   c=np.asarray(item['center']);r=item['radius'];points=[np.asarray(pix(c+[0,-r])),np.asarray(pix(c+[0,r]))];horizontal=False
  else:
   leaders.append((item,view,pix,bounds,desired));continue
  side=side_for(horizontal,desired,bounds);span=abs(points[1][0 if horizontal else 1]-points[0][0 if horizontal else 1]);linear.append((span,item,view,pix,bounds,points,horizontal,side,desired))
 # Short spans consume near lanes; whole-view extents are allocated last/outside.
 lane_offsets={}
 for span,item,view,pix,bounds,points,horizontal,side,desired in sorted(linear,key=lambda x:(x[0],x[1]['id'])):
  dim=item['dimension'];text=value_text(dim);layer=painter.text_layer(text);key=(view,side);offset=lane_offsets.get(key,18*S);placed=False;reason='No free dimension band within sheet'
  for extra in (0,10,20,32,48):
   coord=band_coordinate(bounds,side,offset+extra*S);a,b=points;p=np.array([a[0],coord]) if horizontal else np.array([coord,a[1]]);q=np.array([b[0],coord]) if horizontal else np.array([coord,b[1]])
   sign=-1 if side in ('top','left') else 1;center=(p+q)/2;clearance=layer.height/2+5*S;center[1 if horizontal else 0]+=sign*clearance
   narrow=span<layer.width+20*S
   if narrow:
    # Keep narrow dimension text outside its arrows, in the same external band.
    center[0 if horizontal else 1]=max(p[0 if horizontal else 1],q[0 if horizontal else 1])+layer.width/2+14*S
   backup=image.copy();old_boxes=list(painter.boxes);old_labels=list(painter.labels);old_segments=list(painter.line_segments)
   try:
    painter.label(text,center,vertical=not horizontal)
    # Place dimension lines outside the complete view; extension lines start at geometry.
    painter.line(a,p);painter.line(b,q);painter.line(p,q)
    if narrow:
     v=(q-p)/max(np.linalg.norm(q-p),1e-9);painter.line(p-v*12*S,q+v*12*S);painter.arrow(p,p-v*12*S);painter.arrow(q,q+v*12*S)
    else:painter.arrow(p,q);painter.arrow(q,p)
    drawn.append(item['id']);lane_offsets[key]=offset+extra*S+layer.height+14*S;records.append({'id':item['id'],'view':view,'side':side,'mode':'external-band','placedLabelPixels':(center/S).tolist(),'bandCoordinate':coord/S,'narrow':bool(narrow)});placed=True;break
   except ValueError as ex:
    reason=str(ex);image.paste(backup,(0,0));painter.boxes=old_boxes;painter.labels=old_labels;painter.line_segments=old_segments
  if not placed:failed.append({'id':item['id'],'dimension':dim,'reason':reason})
 for item,view,pix,bounds,desired in leaders:
  dim=item['dimension'];text=value_text(dim);layer=painter.text_layer(text)
  if item['kind']=='circle':
   c=np.asarray(item['center']);cp=np.asarray(pix(c));d=np.array([desired[0]-cp[0],cp[1]-desired[1]]);d/=max(np.linalg.norm(d),1e-9);tips=[np.asarray(pix(c+d*item['radius']))]
  else:tips=[np.asarray(pix(p)) for p in item.get('anchorOptions',[item['anchor']])]
  if item['kind']=='circle':
   import math
   cp=np.asarray(pix(item['center']));tip=tips[0];v=(tip-cp)/max(np.linalg.norm(tip-cp),1e-9)
   angle=math.degrees(math.atan2(v[1],v[0]));angle=(angle+90)%180-90
   normal=np.array([-v[1],v[0]])
   backup=image.copy();old_boxes=list(painter.boxes);old_labels=list(painter.labels);old_segments=list(painter.line_segments)
   try:
    pos=tip+v*(layer.width/2+18*S)-normal*(layer.height/2+5*S)
    painter.label(text,pos,angle=angle)
    painter.line(2*cp-tip,tip+v*(layer.width+25*S));painter.arrow(tip,tip+v*18*S)
    drawn.append(item['id']);records.append({'id':item['id'],'view':view,'mode':'inclined-diameter','labelAngleDeg':angle,'placedLabelPixels':(pos/S).tolist()});continue
   except ValueError:
    image.paste(backup,(0,0));painter.boxes=old_boxes;painter.labels=old_labels;painter.line_segments=old_segments
  chamfer=dim.get('sourceMeasurement',{}).get('chamferAngleDeg') is not None or dim.get('scriptReference',{}).get('kind')=='chamfer'
  gap=32*S if chamfer else 16*S
  candidates=[]
  for tip in tips:

   # Four nearby exterior sides; each hole/radius remains independently labelled.
   for k in range(-3,4):
    delta=k*24*S
    for pos in ([bounds[0]-layer.width/2-gap,tip[1]+delta],[bounds[2]+layer.width/2+gap,tip[1]+delta],[tip[0]+delta,bounds[1]-layer.height/2-gap],[tip[0]+delta,bounds[3]+layer.height/2+gap]):
     pos=np.asarray(pos);cost=np.linalg.norm(pos-tip)+.35*np.linalg.norm(pos-desired);candidates.append((cost,tip,pos))
  for tip in ([] if chamfer else tips):
   for distance in (24,40,64,96):
    for dx,dy in ((1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)):
     pos=tip+np.array([dx,dy])*distance*S
     candidates.append((np.linalg.norm(pos-tip)+.35*np.linalg.norm(pos-desired)+80*S,tip,pos))
  candidates=[(cost+sum(100*S for a,b in painter.line_segments if crossing(tip,pos,a,b)),tip,pos) for cost,tip,pos in candidates]
  placed=False;reason='No short clear leader position'
  for _,tip,pos in sorted(candidates,key=lambda v:v[0]):
   if np.linalg.norm(tip-pos)>200*S:continue
   backup=image.copy();old_boxes=list(painter.boxes);old_labels=list(painter.labels);old_segments=list(painter.line_segments)
   try:
    painter.label(text,pos);edge=pos.copy();edge[0]+=(-1 if tip[0]<pos[0] else 1)*(layer.width/2+3*S);painter.line(tip,edge);painter.arrow(tip,edge)
    drawn.append(item['id']);records.append({'id':item['id'],'view':view,'mode':'short-leader','placedLabelPixels':(pos/S).tolist()});placed=True;break
   except ValueError as ex:reason=str(ex);image.paste(backup,(0,0));painter.boxes=old_boxes;painter.labels=old_labels;painter.line_segments=old_segments
  if not placed:failed.append({'id':item['id'],'dimension':dim,'reason':reason})
 for layer,pos in painter.labels:painter.paste_label(layer,pos)
 return {'placed':drawn,'failed':failed,'templatePlacements':records,'annotationLineLengthPixels':sum(float(np.linalg.norm(b-a)) for a,b in painter.line_segments)/S,'lineSegments':[[list(a/S),list(b/S)] for a,b in painter.line_segments]}
