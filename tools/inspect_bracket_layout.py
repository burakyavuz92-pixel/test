"""Offline bracket-delimited layout detection. No unmarked text inference."""
import argparse,csv,hashlib,io,json,math,pathlib,re,subprocess,os,zipfile,xml.etree.ElementTree as ET
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from inspect_template_dimensions import REGIONS

TOKEN=re.compile(r'(?:[Øø⌀])?\[(?:[Øø⌀Oo])?([A-Z][A-Z0-9]*|\d+(?:[.,]\d+)?)\]')
def parse_token(text):
    text=re.sub(r'\s+','',text)
    found=TOKEN.fullmatch(text)
    return found.group(1) if found else None

def inverse_box(box,size,rotated_size,offset,angle):
    c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle));pts=[]
    for x,y in [(box[0],box[1]),(box[2],box[1]),(box[2],box[3]),(box[0],box[3])]:
        dx=x-rotated_size[0]/2;dy=y-rotated_size[1]/2
        pts.append([offset[0]+size[0]/2+c*dx-s*dy,offset[1]+size[1]/2+s*dx+c*dy])
    return pts

def read_columns(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        shared=[''.join(v.itertext()) for v in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rows=ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:sheetData/m:row',ns)
        def value(cell):
            text=cell.findtext('m:v','',ns)
            return shared[int(text)] if cell.get('t')=='s' else ''.join(cell.find('m:is',ns).itertext()) if cell.get('t')=='inlineStr' else text
        headers={c.get('r').rstrip('0123456789'):value(c).strip() for c in rows[0]}
        result={v:False for k,v in headers.items() if len(k)>1 or k>='F'}
        for row in rows[1:]:
            for c in row:
                name=headers.get(c.get('r').rstrip('0123456789'))
                if name in result and value(c).lstrip().startswith(('Ø','ø','⌀')):result[name]=True
        return result

def normalize_label(label,columns):
    if label in columns:return label,None
    if len(label)>1 and label[0] in 'DPQO0' and columns.get(label[1:],False):return label[1:],'diameter-symbol OCR normalization using Excel type'
    return label,None

def save_preview(image,found,folder):
    W,H=image.size
    preview=image.resize((1754,round(H*1754/W)));draw=ImageDraw.Draw(preview);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);k=preview.width/W
    for i,item in enumerate(found,1):
        item['id']=i;polygon=[tuple(p*k for p in xy) for xy in item['polygonPixels']];draw.line(polygon+[polygon[0]],fill='blue',width=2);draw.text((min(p[0] for p in polygon),min(p[1] for p in polygon)-18),f'{i}:[{item["label"]}]',font=font,fill='blue',stroke_width=1,stroke_fill='white')
    preview.save(folder/'detection-preview.jpeg',quality=95)

def inspect(source,folder,excel=None):
    folder=pathlib.Path(folder);folder.mkdir(parents=True,exist_ok=True)
    image=Image.open(source).convert('RGB');W,H=image.size;found=[];columns=read_columns(excel) if excel else {}
    for view,region in REGIONS.items():
        rect=tuple(round(v*(W if i%2==0 else H)) for i,v in enumerate(region));crop=image.crop(rect)
        for angle in range(0,360,15):
            raw=crop.rotate(angle,expand=True,fillcolor='white')
            mask=(np.asarray(raw.convert('L'))<180).astype('uint8')*255
            lines=cv2.bitwise_or(cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((1,65),np.uint8)),cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((120,1),np.uint8)))
            cleaned=Image.fromarray(255-cv2.subtract(mask,lines))
            variants=[(raw,0,0,11),(cleaned,0,0,11)]
            if angle in (0,15,30,45,270,315,330,345):
                n,_,stats,_=cv2.connectedComponentsWithStats(cv2.subtract(mask,lines))
                centers=[]
                for x,y,bw,bh,area in stats[1:]:
                    if not (35<bh<110 and 4<bw<100 and 45<area<5000):continue
                    cx=x+bw/2;cy=y+bh/2
                    if any(abs(cx-px)<60 and abs(cy-py)<35 for px,py in centers):continue
                    centers.append((cx,cy));left=max(0,int(cx-130));top=max(0,int(cy-65));right=min(raw.width,int(cx+130));bottom=min(raw.height,int(cy+65))
                    roi=raw.crop((left,top,right,bottom));roi_mask=(np.asarray(roi.convert('L'))<180).astype('uint8')*255
                    vertical=cv2.morphologyEx(roi_mask,cv2.MORPH_OPEN,np.ones((25,1),np.uint8))
                    _,_,bars,_=cv2.connectedComponentsWithStats(vertical)
                    bars=[r for r in bars[1:] if r[3]>35]
                    if len(bars)<2 or np.mean(roi_mask>0)>.25:continue
                    variants.append((roi,left,top,7))
            words=[]
            for variant,ox,oy,psm in variants:
                path=folder/'ocr-input.png';variant.save(path)
                run=subprocess.run(['tesseract',str(path),'stdout','--psm',str(psm),'-l','eng','tsv'],capture_output=True,text=True,check=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
                part=[v for v in csv.DictReader(io.StringIO(run.stdout),delimiter='\t',quoting=csv.QUOTE_NONE) if v.get('text','').strip()]
                prefix=str(len(words))
                for v in part:v['left']=str(int(v['left'])+ox);v['top']=str(int(v['top'])+oy);v['block_num']=prefix+':'+v['block_num']
                words.extend(part)
            rotated=raw
            print(f'{view} angle={angle} local_regions={len(variants)-2}',flush=True)
            groups={}
            for word in words:groups.setdefault(tuple(word[k] for k in ('block_num','par_num','line_num')),[]).append(word)
            for line in groups.values():
                for start in range(len(line)):
                    for end in range(start+1,min(len(line),start+4)+1):
                        span=line[start:end];text=''.join(w['text'] for w in span);label=parse_token(text)
                        if label is None:continue
                        raw_label=label;label,correction=normalize_label(label,columns)
                        conf=min(float(w['conf']) for w in span)
                        if conf<20:continue
                        b=[min(int(w['left']) for w in span),min(int(w['top']) for w in span),max(int(w['left'])+int(w['width']) for w in span),max(int(w['top'])+int(w['height']) for w in span)]
                        polygon=inverse_box(b,crop.size,rotated.size,rect,angle)
                        center=np.mean(polygon,axis=0);old=next((v for v in found if v['view']==view and np.linalg.norm(np.array(v['centerPixels'])-center)<max(40,(b[3]-b[1])*.7)),None)
                        item={'label':label,'rawLabel':raw_label,'normalization':correction,'sourceText':text,'view':view,'confidence':conf,'centerPixels':center.tolist(),'polygonPixels':polygon,'centerNormalized':[center[0]/W,center[1]/H],'ocrRotationDeg':angle,'orientationStatus':'OCR search angle, not independently measured text orientation','status':'needs-review'}
                        if old:
                            if conf>old['confidence']:found.remove(old);found.append(item)
                        else:found.append(item)
        path.unlink()
    for item in found:
        label=item['label'];item['kind']='excel-label' if label in columns else 'literal-radius' if re.fullmatch(r'R[0-9]+(?:[.,][0-9]+)?',label) else 'literal-dimension' if re.fullmatch(r'[0-9]+(?:[.,][0-9]+)?',label) else 'unmatched-label'
    rejected=[v for v in found if v['kind']=='unmatched-label']
    found=[v for v in found if v['kind']!='unmatched-label']
    found.sort(key=lambda v:(v['view'],v['centerPixels'][1]))
    save_preview(image,found,folder)
    report={'apiCalls':0,'sourceSha256':hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest(),'sourcePixels':[W,H],'excelColumns':list(columns),'missingExcelLabels':sorted(set(columns)-{v['label'] for v in found}),'viewRegionsNormalized':REGIONS,'candidates':found,'rejectedCandidates':rejected,'limits':['Bracket labels only; unmarked text is intentionally excluded','Arrow connectivity not resolved','OCR angle search uses 15 degree steps; not a guaranteed arbitrary-angle detector','View regions are calibrated to this template']}
    (folder/'detections.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps([(v['label'],v['view'],v['ocrRotationDeg'],round(v['confidence'])) for v in found],ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('folder');p.add_argument('--excel');a=p.parse_args();inspect(a.source,a.folder,a.excel)
