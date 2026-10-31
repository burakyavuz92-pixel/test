"""Deterministic transport resizing only; source file is never modified."""
import sys,json,math
from PIL import Image
source,destination,maxedge=sys.argv[1],sys.argv[2],int(sys.argv[3])
maxpatch=int(sys.argv[4]) if len(sys.argv)>4 else 0
if maxpatch<0:raise ValueError("Invalid patch budget")
if not 32<=maxedge<=20000:raise ValueError('Invalid API image edge limit')
with Image.open(source) as im:
 before=im.size;ratio=min(1,maxedge/max(before));size=tuple(max(1,round(x*ratio)) for x in before)
 while maxpatch and math.ceil(size[0]/32)*math.ceil(size[1]/32)>maxpatch:
  size=tuple(max(1,int(x*.995)) for x in size)
 im.convert('RGB').resize(size,Image.Resampling.LANCZOS).save(destination,quality=95,subsampling=0,dpi=im.info.get('dpi',(300,300)))
 print(json.dumps({'sourceSize':before,'transmittedSize':size,'maxEdge':maxedge,'patchBudget':maxpatch or None,'patches32':math.ceil(size[0]/32)*math.ceil(size[1]/32),'operation':'resize-only','sourceModified':False}))
