"""Merge model visual evidence with OCR without part names or measurement values."""
import copy,math

def canonical(label):
    from bracket_content import compact
    label=compact(label.strip().strip('[]'))
    try:return ('R' if label.startswith('R') else '')+format(float(label.removeprefix('R').replace(',','.')),'.10g')
    except ValueError:return label

def merge(layout,markers):
    result=copy.deepcopy(layout);evidence={};used_groups=set();unconfirmed=[];w,h=result['sourcePixels']
    for marker in markers:
        label=canonical(marker['label']);view=marker['view'];center=marker.get('centerNormalized')
        key=marker.get('id',label)
        if key in evidence:raise ValueError('Ambiguous visual marker: '+key)
        if view not in ('front','section') or center is None or len(center)!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in center):raise ValueError('Invalid visual marker')
        tips=marker.get('arrowTipsNormalized')
        if tips is not None:
            for p in tips:
                if p is not None and (len(p)!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in p)):raise ValueError('Invalid visual arrow tip')
        axis=marker.get('sectionAxisNormalized')
        if axis is not None and (len(axis)!=2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in axis) or abs(sum(v*v for v in axis)-1)>.01):raise ValueError('Invalid section axis')
        evidence[key]=marker
        matches=[c for c in result['candidates'] if canonical(c['label'])==label]
        positioned=[c for c in matches if 'centerNormalized' in c]
        if positioned:matches=[c for c in positioned if math.hypot((c['centerNormalized'][0]-center[0])*w,(c['centerNormalized'][1]-center[1])*h)<=max(w,h)*.025]
        if matches:
            c=min(matches,key=lambda c:sum((c.get('centerNormalized',center)[i]-center[i])**2 for i in (0,1)))
            group=c.get('observationGroup')
            if 'occurrenceId' in c or group is not None and group in used_groups:
                unconfirmed.append({'id':key,'label':marker['label'],'reason':'OCR occurrence already assigned'});continue
            if group is not None:used_groups.add(group)
            c['occurrenceId']=key
            frame=marker.get('viewFrameNormalized')
            if frame is not None:
                if len(frame)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<=1 for v in frame) or frame[0]>=frame[2] or frame[1]>=frame[3]:raise ValueError('Invalid source geometry frame')
                if not tips or not any(p is not None for p in tips):raise ValueError('View assignment requires arrow evidence')
                previous=result.setdefault('sourceFrames',{}).get(view)
                bbox=[frame[0]*w,frame[1]*h,frame[2]*w,frame[3]*h]
                if previous and previous.get('method')=='model geometry frame' and any(abs(a-b)>max(w,h)*.01 for a,b in zip(previous['bboxPixels'],bbox)):raise ValueError('Inconsistent source geometry frames')
                result['sourceFrames'][view]={'bboxPixels':bbox,'method':'model geometry frame','confidence':None}
                c['ocrRegionView']=c['view'];c['view']=view;c['viewAssignment']='model arrow and geometry reference'
            elif c['view']=='unassigned':c['view']=view
            elif c['view']!=view:raise ValueError('OCR and model disagree on view: '+label)
            continue
        unconfirmed.append({'id':key,'label':marker['label'],'reason':'No matching OCR text near model marker'})
        # Model evidence may help validate an OCR-approved label, but may not
        # authorize an unbracketed annotation or invent an OCR candidate.
        continue
    result['unconfirmedModelMarkers']=unconfirmed
    return result,evidence
