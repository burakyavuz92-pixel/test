import sys
from PIL import Image
source,destination=sys.argv[1:]
with Image.open(source) as im:
    if im.size!=(7016,4961):raise ValueError('Unsupported calibrated sheet size')
    k=im.width/1487
    im.crop(tuple(round(v*k) for v in (1160,60,1445,430))).save(destination)
