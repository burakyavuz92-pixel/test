import unittest,tempfile,pathlib,subprocess,sys,json,hashlib
from PIL import Image
class TransportTests(unittest.TestCase):
 def run_image(self,size,edge,patches):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t);source=p/'source.jpg';dest=p/'api.jpg';Image.new('RGB',size,'white').save(source,dpi=(300,300));before=hashlib.sha256(source.read_bytes()).hexdigest()
   r=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('prepare_api_image.py')),str(source),str(dest),str(edge),str(patches)],capture_output=True,text=True,check=True)
   meta=json.loads(r.stdout)
   self.assertEqual(before,hashlib.sha256(source.read_bytes()).hexdigest())
   with Image.open(dest) as im:self.assertEqual(tuple(meta['transmittedSize']),im.size);self.assertEqual(im.info['dpi'],(300,300))
   return meta
 def test_resize_preserves_ratio_and_source(self):
  m=self.run_image((100,50),64,0);self.assertEqual(m['transmittedSize'],[64,32])
 def test_no_upscale(self):
  m=self.run_image((16,8),64,0);self.assertEqual(m['transmittedSize'],[16,8])
 def test_patch_limit_also_applies_to_square(self):
  m=self.run_image((1024,1024),1024,100);self.assertLessEqual(m['patches32'],100)
if __name__=='__main__':unittest.main()
