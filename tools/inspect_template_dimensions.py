"""Offline OCR review only; no CAD rendering or API calls."""
import argparse,csv,io,json,math,pathlib,re,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
from quoted_label_ocr import quoted_candidates
import cv2
import numpy as np

# View regions for this reference template. The title block is excluded.
REGIONS={'section':(.035,.055,.29,.78),'front':(.35,.055,.81,.78),'isometric':(.81,.055,.975,.34)}

def inspect(source,folder):
 folder=pathlib.Path(folder);folder.mkdir(parents=True,exist_ok=True);im=Image.open(source).convert('RGB');w,h=im.size;candidates=[]
 mask=(np.asarray(ImageOps.grayscale(im))<205).astype('uint8')*255
 lines=np.zeros_like(mask)
 for kernel in [np.ones((1,130),np.uint8),np.ones((130,1),np.uint8),np.eye(130,dtype=np.uint8),np.fliplr(np.eye(130,dtype=np.uint8)).copy()]:
  lines=cv2.bitwise_or(lines,cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel))
 cleaned=Image.fromarray(255-cv2.subtract(mask,lines))
 jobs=[]
 for view,region in REGIONS.items():
  box=tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(region))
  for mode in ('original','line-cleaned'):
   for angle in (0,90,270,45,-45):jobs.append((view,box,angle,mode))
 for job,(view,box,angle,mode) in enumerate(jobs):
   crop=(cleaned if mode=='line-cleaned' else ImageOps.grayscale(im)).crop(box)
   rotated=ImageOps.grayscale(crop).rotate(angle,expand=True,fillcolor=255)
   path=folder/f'ocr-{job}.png';rotated.save(path)
   run=subprocess.run(['tesseract',str(path),'stdout','--psm','11','-l','eng','tsv'],capture_output=True,text=True,check=True)
   (folder/f'ocr-{job}.tsv').write_text(run.stdout)
   a=math.radians(angle);c=math.cos(a);s=math.sin(a)
   for word in csv.DictReader(io.StringIO(run.stdout),delimiter='\t',quoting=csv.QUOTE_NONE):
    text=word.get('text','').strip();confidence=float(word.get('conf','-1'))
    if not text or confidence<25:continue
    normalized=text.replace('’',"'").replace('‘',"'").replace('“',"'").replace('”',"'").replace('"',"'").replace(' ','').replace('!',"'")
    if re.fullmatch(r"[^A-Za-z0-9]*'[A-Z]'(?:\+\d+(?:[.,]\d+)?)?[^A-Za-z0-9]*",normalized):kind='parameter' if '+' not in normalized else 'symbolic-fixed-relation'
    elif re.fullmatch(r'[RrØø⌀]?[0-9]+(?:[.,][0-9]+)?',normalized):kind='fixed-measurement-candidate'
    else:continue
    if kind=='fixed-measurement-candidate' and confidence<(75 if normalized[:1].upper()=='R' else 85):continue
    x,y,bw,bh=[int(word[k]) for k in ('left','top','width','height')];points=[]
    for px,py in [(x,y),(x+bw,y),(x+bw,y+bh),(x,y+bh)]:
     dx=px-rotated.width/2;dy=py-rotated.height/2;points.append((box[0]+crop.width/2+c*dx-s*dy,box[1]+crop.height/2+s*dx+c*dy))
    bbox=[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
    if any(v<0 for v in bbox) or bbox[2]>w or bbox[3]>h:continue
    candidate={'view':view,'text':text,'normalizedText':normalized,'kind':kind,'confidence':confidence,'preprocessing':mode,'ocrRotationDeg':angle,'bboxPixels':bbox,'bboxNormalized':[v/(w if i%2==0 else h) for i,v in enumerate(bbox)],'status':'needs-review'}
    duplicate=None
    for old in candidates:
     b=old['bboxPixels'];intersection=max(0,min(b[2],bbox[2])-max(b[0],bbox[0]))*max(0,min(b[3],bbox[3])-max(b[1],bbox[1]))
     area=min((b[2]-b[0])*(b[3]-b[1]),(bbox[2]-bbox[0])*(bbox[3]-bbox[1]))
     if old['view']==view and old['normalizedText']==normalized and intersection/max(area,1)>.4:duplicate=old;break
    if duplicate:
     if confidence>duplicate['confidence']:candidates.remove(duplicate);candidates.append(candidate)
    else:candidates.append(candidate)
   path.unlink()
 for item in quoted_candidates(im,REGIONS,folder):
  b=item['bboxPixels'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
  if not any(v['view']==item['view'] and abs((v['bboxPixels'][0]+v['bboxPixels'][2])/2-cx)<40 and abs((v['bboxPixels'][1]+v['bboxPixels'][3])/2-cy)<40 for v in candidates):candidates.append(item)
 candidates.sort(key=lambda v:(v['view'],v['bboxPixels'][1],v['bboxPixels'][0]))
 preview=im.resize((1754,round(1754*h/w)));draw=ImageDraw.Draw(preview);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);k=preview.width/w
 for i,entry in enumerate(candidates,1):
  entry['id']=i;b=[round(v*k) for v in entry['bboxPixels']];color='blue' if entry['kind']=='parameter' else 'red'
  draw.rectangle(b,outline=color,width=2);draw.text((b[0],max(0,b[1]-15)),f'{i}:{entry["normalizedText"]}',font=font,fill=color,stroke_width=1,stroke_fill='white')
 preview.save(folder/'detection-preview.jpeg',quality=95)
 report={'apiCalls':0,'source':str(source),'sourceSha256':hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest(),'sourcePixels':[w,h],'viewRegionsNormalized':REGIONS,'candidates':candidates,'limits':['Candidate detection only; arrow/extension connections are not resolved','Numeric OCR tokens may be false positives; missing detections require review','Fixed view regions are for this template, not inferred from arbitrary drawings']}
 (folder/'detections.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({'count':len(candidates),'candidates':[(v['id'],v['view'],v['normalizedText']) for v in candidates]},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('folder');a=p.parse_args();inspect(a.source,a.folder)
