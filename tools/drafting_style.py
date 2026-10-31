"""Local A5 paper geometry, scale selection and centerline patterns."""
import math

PAPER_MM=(210.,148.)
PIXELS=(1754,1236)
DPI=PIXELS[0]*25.4/PAPER_MM[0]
PX_PER_MM=PIXELS[0]/PAPER_MM[0]


def choose_scale(view_extents,panels):
    fits=[]
    for (width,height),(_,_,w,h) in zip(view_extents,panels):
        fits.append(min((w-30)/max(width,1e-9),(h-30)/max(height,1e-9))/PX_PER_MM)
    maximum=min(fits)
    if maximum<=0:raise ValueError('No usable drafting panel')
    # Familiar reduction scales, with room for large and very small parts.
    candidates=[1/d for d in (1,1.25,1.5,2,2.5,3,4,5,6,8,10,15,20,25,50,100,200,500,1000)]
    candidates += [2.,5.,10.,20.,50.,100.]
    allowed=[s for s in candidates if s<=maximum+1e-10]
    return max(allowed) if allowed else maximum


def scale_label(scale):
    return f'1:{1/scale:g}' if scale<=1 else f'{scale:g}:1'


def patterned_line(draw,a,b,width,pattern,fill='black'):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    if not length:return
    position=0.;i=0
    while position<length:
        end=min(length,position+pattern[i%len(pattern)])
        if i%2==0:draw.line((a[0]+dx*position/length,a[1]+dy*position/length,a[0]+dx*end/length,a[1]+dy*end/length),fill=fill,width=width)
        position=end;i+=1
