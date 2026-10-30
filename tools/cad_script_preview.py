"""CPU mesh previews from the already built script geometry; no interpretation of input JPEG."""
import pathlib,sys,json
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'experiments/occt'))
from worker import render
out=pathlib.Path(sys.argv[1]);row=json.loads((out/'parameters.json').read_text());images=[]
for name,direction in [('z-negative',[1,-1,-1]),('z-positive',[1,-1,1])]:
 directory=out/name;directory.mkdir(exist_ok=True);render(out/'mesh.stl',directory,{'camera':{'direction':direction,'up':[0,1,0],'projection':'orthographic'}})
 with Image.open(directory/'occt-preview.png') as image:images.append(image.convert('RGB'))
page=Image.new('RGB',(1754,1240),'white');draw=ImageDraw.Draw(page);font=ImageFont.truetype('/workspace/fonts/arial/arial.ttf',20)
draw.text((45,30),row['outputId']+' — geometri betiği / inceleme',font=font,fill='black')
for i,image in enumerate(images):
 image.thumbnail((800,900));page.paste(image,(45+i*850,130));draw.text((45+i*850,85),['−Z tarafından','+Z tarafından'][i],font=font,fill='black')
draw.text((45,1140),'Tek parametrik betikten üretildi. Kesit, ölçülendirme ve antet uygulanmadı.',font=font,fill='black');page.save(out/(row['outputId']+'.jpeg'),quality=95,dpi=(300,300))
