"""Deterministic search over shared scales and dimensioned view packages (page pixels)."""
import math
from drafting_style import PX_PER_MM

def candidates(extents,regions):
    bound=max(min(w/max(e[0],1e-9),h/max(e[1],1e-9))/PX_PER_MM for _,_,w,h in regions for e in extents)
    top=math.ceil(math.log10(max(bound,1e-12)))
    return sorted({m*10.**k for k in range(top-10,top+1) for m in (1,2,5) if m*10.**k<=bound+1e-10},reverse=True)

def layouts(extents,scale,padding,regions):
    # extents and result order: main, section. Section remains left.
    sizes=[(e[0]*scale*PX_PER_MM+2*p[0],e[1]*scale*PX_PER_MM+2*p[1]+32) for e,p in zip(extents,padding)]
    for x,y,w,h in regions:
        remaining=w-sum(s[0] for s in sizes)
        if remaining<40 or max(s[1] for s in sizes)>h:continue
        gap=min(120,remaining)
        total=sum(s[0] for s in sizes)+gap
        left=x+(w-total)/2
        section=(left,y+(h-sizes[1][1])/2,*sizes[1])
        main=(left+sizes[1][0]+gap,y+(h-sizes[0][1])/2,*sizes[0])
        yield [main,section]

def select(extents,padding,regions,trial):
    attempts=[]
    for scale in candidates(extents,regions):
        found=False;valid=[]
        for packages in layouts(extents,scale,padding,regions):
            found=True
            panels=[(x+px,y+py,w-2*px,h-2*py-32) for (x,y,w,h),(px,py) in zip(packages,padding)]
            result=trial(scale,panels,packages)
            reasons=result.get('reasons',[]) if isinstance(result,dict) else result
            score=result.get('score',0) if isinstance(result,dict) else 0
            attempts.append({'scale':scale,'accepted':not reasons,'reasons':reasons,'score':score})
            if not reasons:valid.append((score,len(valid),panels,packages))
        if valid:
            _,_,panels,packages=min(valid)
            trial(scale,panels,packages) # Restore the winning temporary drawing.
            return scale,panels,packages,attempts
        if not found:attempts.append({'scale':scale,'accepted':False,'reasons':['Dimensioned packages exceed available page region']})
    raise ValueError('No scale fits all resolved annotations and reserved page areas')
