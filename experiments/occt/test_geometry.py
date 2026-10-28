import copy,json,math,unittest
from pathlib import Path
from worker import build,validate,volume
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_OUT,TopAbs_IN

class GeometryChecks(unittest.TestCase):
    def setUp(self):self.data=json.loads(Path(__file__).with_name('plate-160.json').read_text())
    def test_three_holes_are_empty_and_base_is_solid(self):
        shape,checks=build(self.data)
        for h in self.data['holes']:
            self.assertEqual(BRepClass3d_SolidClassifier(shape,gp_Pnt(h['xMm'],h['yMm'],-1.5),1e-7).State(),TopAbs_OUT)
        self.assertEqual(BRepClass3d_SolidClassifier(shape,gp_Pnt(0,0,-1.5),1e-7).State(),TopAbs_IN)
        self.assertTrue(checks['validBrep']);self.assertEqual(checks['solidCount'],1)
    def test_two_hole_volume_difference(self):
        three,_=build(self.data);two_data=copy.deepcopy(self.data);two_data['holes'].pop();two,_=build(two_data)
        self.assertAlmostEqual(volume(two)-volume(three),math.pi*2.5**2*3,places=5)
    def test_asymmetric_holes_supported(self):
        self.data['outerDiameterMm']=286;self.data['holes']=[dict(xMm=0,yMm=86.7,diameterMm=21),dict(xMm=0,yMm=-78.7,diameterMm=12.6)]
        shape,checks=build(self.data);self.assertTrue(checks['validBrep']);self.assertEqual(checks['holeCount'],2)
    def test_reject_bend_intersection(self):
        self.data['holes'][0]['yMm']=75
        with self.assertRaises(ValueError):validate(self.data)
    def test_reject_overlap(self):
        self.data['holes'][1]['yMm']=self.data['holes'][0]['yMm']
        with self.assertRaises(ValueError):validate(self.data)
    def test_reject_impossible_radius(self):
        self.data['outerRadiusMm']=2
        with self.assertRaises(ValueError):validate(self.data)

class DrawingChecks(unittest.TestCase):
    def test_real_section_and_hlr(self):
        from technical_sheet import derive
        data=json.loads(Path(__file__).with_name('plate-160.json').read_text());data['holes']=data['holes'][:2]
        shape,_=build(data);front,edges,loops,cut_visible=derive(shape,data)
        self.assertGreaterEqual(len(front),3);self.assertEqual(len(loops),3);self.assertGreater(len(cut_visible),len(loops))
        self.assertTrue(all(abs(p.X())<1e-6 for loop in loops for p in loop))

class ConditionalSectionChecks(unittest.TestCase):
    def data(self):
        data=json.loads(Path(__file__).with_name('plate-160.json').read_text())
        for i,h in enumerate(data['holes']):h['id']=str(i)
        data['drawing']={'section':{'mode':'through-features','featureIds':['0','1','2']}}
        return data
    def test_off_axis_hole_is_included_without_false_transition_edges(self):
        from technical_sheet import derive,section_bands
        data=self.data();shape,_=build(data);_,edges,loops,_=derive(shape,data)
        bands=section_bands(data);self.assertEqual(len(bands),3)
        # 3 holes split the base into 4 disconnected cross-section regions.
        self.assertEqual(len(loops),4)
        for boundary in [b[2] for b in bands[:-1]]:
            self.assertFalse(any(all(abs(p.Y()-boundary)<1e-6 for p in edge) for edge in edges))
    def test_absent_or_centered_third_hole_is_planar(self):
        from technical_sheet import section_bands,derive
        data=self.data();data['holes'][2]['xMm']=0
        self.assertEqual(len(section_bands(data)),1)
        shape,_=build(data);self.assertEqual(len(derive(shape,data)[2]),4)
        data['holes'].pop();self.assertEqual(len(section_bands(data)),1)
        shape,_=build(data);self.assertEqual(len(derive(shape,data)[2]),3)

if __name__=='__main__':unittest.main()
