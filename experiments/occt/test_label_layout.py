import unittest
from label_layout import LabelLayout,polygon,hits_segment,overlap
class LayoutChecks(unittest.TestCase):
    def test_rotated_text_hits_vertical_dimension(self):
        box=polygon((-30,-14,30,4),100,100,20,3)
        self.assertTrue(hits_segment(box,(100,50),(100,150)))
    def test_candidate_relocation(self):
        layout=LabelLayout((0,0,300,300));layout.segment((100,0),(100,300))
        x,y,a,_=layout.choose('tol',(-25,-14,25,4),[(100,100,20,None),(160,100,20,None)])
        self.assertEqual(x,160);self.assertEqual(layout.records[0]['candidate'],1)
    def test_long_tolerance_and_existing_text(self):
        layout=LabelLayout((0,0,400,400));layout.labels.append(polygon((-35,-15,35,6),100,100,0,3))
        x,*_=layout.choose('other',(-40,-16,40,6),[(110,100,0,None),(220,100,0,None)])
        self.assertEqual(x,220)
    def test_failure_does_not_silently_overlap(self):
        layout=LabelLayout((0,0,20,20))
        with self.assertRaises(ValueError):layout.choose('wide',(-40,-10,40,10),[(10,10,0,None)])
    def test_leader_does_not_cross_previous_label(self):
        layout=LabelLayout((0,0,300,300));layout.labels.append(polygon((-10,-10,10,10),100,100,0))
        self.assertFalse(layout.clear(polygon((-10,-10,10,10),240,240,0),((0,0),(200,200))))
if __name__=='__main__':unittest.main()
