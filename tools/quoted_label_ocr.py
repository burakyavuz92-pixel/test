"""Local glyph recognition bounded by two detected quote components."""
import csv,io,math,subprocess
import cv2,numpy as np
from PIL import ImageOps

def quoted_candidates(image,regions,folder):
 W,H=image.size;result=[];path=folder/'glyph.png'
 for view,region in regions.items():
  box=tuple(round(v*(W if i%2==0 else H)) for i,v in enumerate(region));crop=image.crop(box)
  for angle in (0,90,270,45,-45):
   rotated=ImageOps.grayscale(crop).rotate(angle,expand=True,fillcolor=255);mask=(np.asarray(rotated)<205).astype('uint8')*255
   _,_,stats,_=cv2.connectedComponentsWithStats(mask)
   quotes=[r for r in stats if 3<r[2]<25 and 8<r[3]<40 and r[4]>10]
   for x,y,w,h,area in stats:
    if not (12<w<110 and 35<h<110):continue
    left=[q for q in quotes if 0<x-q[0]<50 and abs(q[1]-y)<25]
    right=[q for q in quotes if 0<q[0]-(x+w)<50 and abs(q[1]-y)<25]
    if not left or not right:continue
    path=folder/'glyph.png';ImageOps.expand(rotated.crop((x-3,y-3,x+w+3,y+h+3)),20,fill=255).save(path)
    run=subprocess.run(['tesseract',str(path),'stdout','--psm','10','-l','eng','tsv'],capture_output=True,text=True,check=True)
    words=[r for r in csv.DictReader(io.StringIO(run.stdout),delimiter='\t',quoting=csv.QUOTE_NONE) if r.get('text','').strip()]
    if len(words)!=1:continue
    text=words[0]['text'].strip();confidence=float(words[0]['conf'])
    if len(text)!=1 or not text.isascii() or not text.isupper() or confidence<40:continue
    left=min(left,key=lambda q:x-q[0]);right=min(right,key=lambda q:q[0]-(x+w));x0=int(left[0]);x1=int(right[0]+right[2]);a=math.radians(angle);c=math.cos(a);s=math.sin(a);pts=[]
    for px,py in [(x0,y),(x1,y),(x1,y+h),(x0,y+h)]:
     dx=px-rotated.width/2;dy=py-rotated.height/2;pts.append((box[0]+crop.width/2+c*dx-s*dy,box[1]+crop.height/2+s*dx+c*dy))
    bbox=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
    result.append({'view':view,'text':"'"+text+"'",'normalizedText':"'"+text+"'",'kind':'parameter','confidence':confidence,'preprocessing':'quote-bounded-glyph','ocrRotationDeg':angle,'bboxPixels':bbox,'bboxNormalized':[float(v/(W if i%2==0 else H)) for i,v in enumerate(bbox)],'status':'needs-review','suffixUnverified':True})
 path=folder/'glyph.png'
 if path.exists():path.unlink()
 return result
