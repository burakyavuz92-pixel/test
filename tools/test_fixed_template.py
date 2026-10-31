import unittest,tempfile,pathlib
from PIL import Image
from fixed_template import background

class FixedTemplate(unittest.TestCase):
 def test_drawing_erased_titleblock_preserved_and_copy_isolated(self):
  with tempfile.TemporaryDirectory() as folder:
   path=pathlib.Path(folder)/'template.jpg'
   Image.new('RGB',(1403,992),'black').save(path)
   first=background(path,(1403,992))
   self.assertEqual(first.getpixel((200,200)),(255,255,255))
   self.assertEqual(first.getpixel((1250,940)),(0,0,0))
   first.putpixel((1250,940),(255,0,0))
   self.assertEqual(background(path,(1403,992)).getpixel((1250,940)),(0,0,0))
 def test_small_fixture_uses_plain_sheet(self):
  with tempfile.TemporaryDirectory() as folder:
   path=pathlib.Path(folder)/'small.jpg';Image.new('RGB',(20,20)).save(path)
   self.assertIsNone(background(path,(100,70)))
if __name__=='__main__':unittest.main()
