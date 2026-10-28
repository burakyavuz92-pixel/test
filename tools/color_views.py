"""Local engineering-input views: redact red pixels only, never move geometry."""
import json,sys
from pathlib import Path
from PIL import Image,ImageChops

def geometry_view(image):
    rgb=image.convert('RGB');r,g,b=rgb.split()
    rg=ImageChops.subtract(r,g).point(lambda v:255 if v>30 else 0)
    rb=ImageChops.subtract(r,b).point(lambda v:255 if v>30 else 0)
    bright=r.point(lambda v:255 if v>100 else 0)
    mask=ImageChops.multiply(ImageChops.multiply(rg,rb),bright)
    result=rgb.copy();result.paste((255,255,255),mask=mask)
    return result,sum(mask.histogram()[1:])

if __name__=='__main__':
    source,output=map(Path,sys.argv[1:]);im=Image.open(source);result,count=geometry_view(im)
    result.save(output,quality=98,dpi=im.info.get('dpi',(300,300)))
    output.with_suffix('.json').write_text(json.dumps({'policy':'red-pixels-excluded-from-geometry','redPixelCount':count,'inputSize':list(im.size),'outputSize':list(result.size),'limits':['Threshold-based color extraction; not independent semantic validation','Black and green pixels are retained; pale red remnants can remain']},indent=2))
