"""Merge model visual evidence with OCR without part names or measurement values."""
import copy,math

def canonical(label):
    label=label.strip().strip('[]')
    try:return ('R' if label.startswith('R') else '')+format(float(label.removeprefix('R').replace(',','.')),'.10g')
    except ValueError:return label

def merge(layout,markers):
    result=copy.deepcopy(layout);evidence={};w,h=result['sourcePixels']
    for marker in markers:
        label=canonical(marker['label']);view=marker['view'];center=marker.get('centerNormalized')
        if label in evidence:raise ValueError('Ambiguous visual marker: '+label)
        if view not in ('front','section') or center is None or len(center)!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in center):raise ValueError('Invalid visual marker')
        tips=marker.get('arrowTipsNormalized')
        if tips is not None:
            for p in tips:
                if p is not None and (len(p)!=2 or not all(isinstance(x,(int,float)) and math.isfinite(x) and 0<=x<=1 for x in p)):raise ValueError('Invalid visual arrow tip')
        evidence[label]=marker
        matches=[c for c in result['candidates'] if canonical(c['label'])==label]
        if matches:
            for c in matches:
                if c['view']!=view:raise ValueError('OCR and model disagree on view: '+label)
            continue
        # Model evidence may help validate an OCR-approved label, but may not
        # authorize an unbracketed annotation or invent an OCR candidate.
        continue
    return result,evidence
