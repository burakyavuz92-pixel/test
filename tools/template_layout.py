"""Local template layout preparation and source-bound dimension binding."""
import hashlib,json,math,pathlib
import cv2,numpy as np
from PIL import Image
from inspect_bracket_layout import inspect,read_columns

VERSION='bracket-layout-v1'

def source_frames(image,layout):
    W,H=image.size;w=1754;h=round(H*w/W);gray=cv2.resize(np.asarray(image.convert('L')),(w,h));scale=W/w
    # Round main view: require strong ink support around an entire circumference.
    x0,y0,x1,y1=map(round,(w*.30,h*.055,w*.81,h*.78));roi=gray[y0:y1,x0:x1];distance=cv2.distanceTransform((roi>190).astype('uint8'),cv2.DIST_L2,3);circles=[];base=min(roi.shape)
    for lower in np.arange(base*.16,base*.49,base*.09):
        found=cv2.HoughCircles(roi,cv2.HOUGH_GRADIENT,1,20,param1=100,param2=40,minRadius=int(lower),maxRadius=int(lower+base*.1))
        if found is None:continue
        for x,y,r in found.reshape(-1,3):
            t=np.linspace(0,2*np.pi,360);xs=np.rint(x+r*np.cos(t)).astype(int);ys=np.rint(y+r*np.sin(t)).astype(int)
            if min(xs)<0 or max(xs)>=roi.shape[1] or min(ys)<0 or max(ys)>=roi.shape[0]:continue
            score=float(np.mean(distance[ys,xs]<2))
            if score>.9:circles.append((r,x+x0,y+y0,score))
    frames={}
    if circles:
        r,x,y,score=max(circles);frames['front']={'bboxPixels':[float((x-r)*scale),float((y-r)*scale),float((x+r)*scale),float((y+r)*scale)],'method':'ink-validated circular outline','confidence':score}
    # This template's section is upright. Reject dimension lines aligned with OCR text.
    x0,y0,x1,y1=map(round,(w*.035,h*.055,w*.29,h*.78));roi=gray[y0:y1,x0:x1]
    lines=cv2.HoughLinesP(cv2.Canny(roi,70,150),1,np.pi/180,threshold=50,minLineLength=round((y1-y0)*.38),maxLineGap=30)
    structural=[]
    for x,y,X,Y in ([] if lines is None else lines.reshape(-1,4)):
        if abs(int(x)-int(X))>2:continue
        xx=(x+X)/2+x0
        if any(v['view']=='section' and abs(v.get('ocrRotationDeg',0)%180-90)<10 and abs(v['centerPixels'][0]/scale-xx)<10 for v in layout['candidates']):continue
        structural.append((xx,min(y,Y)+y0,max(y,Y)+y0))
    if len(structural)>=2:
        left=min(v[0] for v in structural);right=max(v[0] for v in structural)
        if right-left>30:frames['section']={'bboxPixels':[float(left*scale),float(min(v[1] for v in structural)*scale),float(right*scale),float(max(v[2] for v in structural)*scale)],'method':'long upright contours excluding labeled dimension lines','confidence':None}
    return frames

def prepare(source,excel,folder,cache_root='.template-layout-cache'):
    folder=pathlib.Path(folder);cache_root=pathlib.Path(cache_root);cache_root.mkdir(exist_ok=True)
    source_hash=hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest();columns=read_columns(excel)
    key=hashlib.sha256(json.dumps([VERSION,source_hash,columns],sort_keys=True).encode()).hexdigest();cache=cache_root/(key+'.json')
    if cache.exists():layout=json.loads(cache.read_text())
    else:
        ocr=folder/'template-detection';inspect(source,ocr,excel);layout=json.loads((ocr/'detections.json').read_text())
        layout['sourceFrames']=source_frames(Image.open(source),layout);layout['layoutVersion']=VERSION
        cache.write_text(json.dumps(layout,indent=2,ensure_ascii=False))
    (folder/'template-layout.json').write_text(json.dumps(layout,indent=2,ensure_ascii=False));return layout

def bind_dimensions(dimensions,layout):
    bindings=[];omitted=[];unresolved=[]
    for dim in dimensions:
        if not dim['effectiveVisible']:continue
        source=dim.get('valueSource',{});matches=[]
        for candidate in layout['candidates']:
            if source.get('kind')=='column':hit=candidate['label']==source['column']
            else:
                literal=candidate['label'];expected='R' if dim['type']=='radius' else ''
                try:hit=literal.startswith(expected) and abs(float(literal[len(expected):].replace(',','.'))-dim['nominal'])<1e-7
                except ValueError:hit=False
            if hit:matches.append(candidate)
        if not matches:omitted.append({'id':dim['id'],'reason':'No bracketed template marker'});continue
        if len(matches)!=1:unresolved.append({'id':dim['id'],'reason':'Ambiguous template marker','dimension':dim});continue
        candidate=matches[0];view=candidate['view']
        if view not in layout.get('sourceFrames',{}):unresolved.append({'id':dim['id'],'reason':'Source geometry frame unavailable','dimension':dim});continue
        bindings.append({'dimension':dim,'marker':candidate,'view':view,'sourceFrame':layout['sourceFrames'][view]})
    return bindings,omitted,unresolved

def map_source_point(binding,view_bbox,pix,point,page_scale=None):
    source=binding['sourceFrame']['bboxPixels'];x,y=point
    low=np.asarray(pix([view_bbox[0],view_bbox[3]]));high=np.asarray(pix([view_bbox[2],view_bbox[1]]))
    result=[]
    for i,v in enumerate((x,y)):
        a,b=source[i],source[i+2]
        if page_scale is not None and v<a:result.append(low[i]+(v-a)*page_scale)
        elif page_scale is not None and v>b:result.append(high[i]+(v-b)*page_scale)
        else:result.append(low[i]+(v-a)/(b-a)*(high[i]-low[i]))
    return np.asarray(result)

def map_label(binding,view_bbox,pix,page_scale=None):
    return map_source_point(binding,view_bbox,pix,binding['marker']['centerPixels'],page_scale)

def estimated_leader_target(binding):
    source=binding['sourceFrame']['bboxPixels'];point=np.array(binding['marker']['centerPixels'],float)
    angle=math.radians(binding['marker'].get('ocrRotationDeg',0));direction=np.array([math.cos(angle),math.sin(angle)])
    center=(np.array(source[:2])+np.array(source[2:]))/2
    if np.dot(center-point,direction)<0:direction=-direction
    hits=[]
    for i in (0,1):
        if abs(direction[i])<1e-8:continue
        for side in (source[i],source[i+2]):
            t=(side-point[i])/direction[i];hit=point+direction*t
            if t>0 and source[1-i]-1<=hit[1-i]<=source[3-i]+1:hits.append((t,hit))
    return min(hits,key=lambda v:v[0])[1] if hits else point
