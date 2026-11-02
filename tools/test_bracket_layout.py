import unittest
from inspect_bracket_layout import parse_token,normalize_label,inverse_box
class BracketLayout(unittest.TestCase):
 def test_supported_marker_forms(self):
  for text,label in [('[A]','A'),('[ Ø G ]','G'),('Ø[G]','G'),('Ø [J]','J'),('[R2]','R2'),('[3]','3')]:self.assertEqual(parse_token(text),label)
 def test_no_brackets_means_no_automatic_marker(self):
  for text in ['R5','R8','A','ØK',"'A'",'[A','A]','(A)']:self.assertIsNone(parse_token(text))
 def test_excel_type_disambiguates_diameter_symbol(self):
  self.assertEqual(normalize_label('DA',{'A':True})[0],'A')
  self.assertEqual(normalize_label('PD',{'D':True})[0],'D')
  self.assertEqual(normalize_label('DB',{'B':False})[0],'DB')
  self.assertEqual(normalize_label('DA',{'A':True,'DA':False})[0],'DA')
 def test_rotated_box_center_returns_to_source(self):
  for angle,rotated in [(0,(200,100)),(90,(100,200)),(270,(100,200))]:
   cx,cy=rotated[0]/2,rotated[1]/2
   pts=inverse_box([cx-10,cy-10,cx+10,cy+10],(200,100),rotated,(30,40),angle)
   self.assertAlmostEqual(sum(p[0] for p in pts)/4,130)
   self.assertAlmostEqual(sum(p[1] for p in pts)/4,90)
if __name__=='__main__':unittest.main()
