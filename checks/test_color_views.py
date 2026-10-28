import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from color_views import geometry_view
from PIL import Image
class ColorChecks(unittest.TestCase):
    def test_red_removed_black_green_unchanged(self):
        im=Image.new('RGB',(4,1));im.putdata([(230,25,25),(0,0,0),(20,150,30),(255,255,255)])
        result,count=geometry_view(im)
        self.assertEqual([result.getpixel((x,0)) for x in range(4)],[(255,255,255),(0,0,0),(20,150,30),(255,255,255)])
        self.assertEqual(count,1);self.assertEqual(im.getpixel((0,0)),(230,25,25))
if __name__=='__main__':unittest.main()
