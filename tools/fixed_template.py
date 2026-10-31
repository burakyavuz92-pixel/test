"""Fixed template regions, measured on the user's 7016 x 4961 drawing."""
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache

REFERENCE=(7016,4961)
# Drawing area only; title block, notes, revision row and outer grid remain intact.
ERASE=[(100,166,6854,3880),(100,3880,4838,4450)]
FIELDS={'scale':(5072,4203,5258,4304),'product':(5780,4535,6410,4852),'format':(6425,4535,6848,4625)}

@lru_cache(maxsize=2)
def _blank(source,width,height):
    with Image.open(source) as im:
        if im.width<1000 or abs(im.width/im.height-REFERENCE[0]/REFERENCE[1])>.02:return None
        image=im.convert('RGB');draw=ImageDraw.Draw(image)
        for box in ERASE:
            draw.rectangle(tuple(round(v*(im.width/REFERENCE[0] if i%2==0 else im.height/REFERENCE[1])) for i,v in enumerate(box)),fill='white')
        return image.resize((width,height),Image.Resampling.LANCZOS)

def background(source,size):
    image=_blank(str(source),*size)
    return image.copy() if image is not None else None

def fill_fields(image,values,fontpath):
    draw=ImageDraw.Draw(image);sx=image.width/REFERENCE[0];sy=image.height/REFERENCE[1]
    for name,text in values.items():
        box=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(FIELDS[name]));x0,y0,x1,y1=box
        draw.rectangle(box,fill='white')
        size=max(6,int((y1-y0)*.6))
        while size>5:
            font=ImageFont.truetype(fontpath,size);bounds=draw.textbbox((0,0),text,font=font)
            if bounds[2]-bounds[0]<=x1-x0-8 and bounds[3]-bounds[1]<=y1-y0-4:break
            size-=1
        draw.text(((x0+x1-bounds[2]-bounds[0])/2,(y0+y1-bounds[3]-bounds[1])/2),text,font=font,fill='black')
