import copy
import unittest
from local_drawing import resolve_local_sections


class LocalSections(unittest.TestCase):
    def drawing(self, direction='V', offset=-44.5, span=30):
        return {'sections':[{'kind':'localCentered','direction':direction,'offsetMm':offset,'spanMm':span}]}

    def test_vertical_span_sign_and_bounds(self):
        original=self.drawing()
        sec=resolve_local_sections(original,[-80,-80,-33,80,80,0])['sections'][0]
        self.assertEqual(sec['worldPath'][1:5],[[0,15,0],[-44.5,15,0],[-44.5,-15,0],[0,-15,0]])
        self.assertGreater(sec['worldPath'][0][1],80)
        self.assertLess(sec['worldPath'][-1][1],-80)
        self.assertEqual(original['sections'][0]['kind'],'localCentered')

    def test_horizontal_positive_offset_is_up(self):
        sec=resolve_local_sections(self.drawing('H',7),[-50,-50,-3,50,50,0])['sections'][0]
        self.assertEqual(sec['worldPath'][2:4],[[15,7,0],[-15,7,0]])

    def test_zero_is_center_plane(self):
        for direction, normal in [('V',[1,0,0]),('H',[0,1,0])]:
            sec=resolve_local_sections(self.drawing(direction,0),[-50,-50,-3,50,50,0])['sections'][0]
            self.assertEqual(sec['kind'],'planar')
            self.assertEqual(sec['cuttingPlanes'],[{'point':[0,0,0],'normal':normal}])

    def test_span_larger_than_body_is_not_clipped(self):
        sec=resolve_local_sections(self.drawing(span=300),[-50,-50,-3,50,50,0])['sections'][0]
        self.assertGreater(sec['worldPath'][0][1],150)
        self.assertEqual(sec['worldPath'][2][1],150)

    def test_legacy_preserved(self):
        drawing={'sections':[{'kind':'planar','cuttingPlanes':[]}]}
        self.assertEqual(resolve_local_sections(drawing,()),drawing)

    def test_invalid_settings(self):
        for d in [self.drawing('D'),self.drawing(span=0),self.drawing(offset=float('nan'))]:
            with self.assertRaises(ValueError):resolve_local_sections(d,[-50,-50,-3,50,50,0])

    def test_offset_trace_actually_crosses_hole(self):
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
        from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
        from cad_recipe_executor import box,section_lines
        body=BRepPrimAPI_MakeCylinder(80,3).Shape()
        tool=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-44.5,0,-1),gp_Dir(0,0,1)),5,5).Shape()
        shape=BRepAlgoAPI_Cut(body,tool).Shape()
        sec=resolve_local_sections(self.drawing(),box(shape))['sections'][0]
        lines,_=section_lines(shape,sec,{'direction':[1,0,0],'up':[0,1,0]})
        ys=[p[1] for line in lines for p in line]
        self.assertTrue(any(abs(y-5)<1e-5 for y in ys))
        self.assertTrue(any(abs(y+5)<1e-5 for y in ys))

    def test_native_occt_both_directions_and_offset_signs(self):
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from cad_recipe_executor import box, section_lines
        shape=BRepPrimAPI_MakeCylinder(80,3).Shape()
        for direction in ('V','H'):
            view={'direction':[1,0,0] if direction=='V' else [0,1,0],
                  'up':[0,1,0] if direction=='V' else [1,0,0]}
            for offset in (-44.5,0,44.5):
                sec=resolve_local_sections(self.drawing(direction,offset),box(shape))['sections'][0]
                lines,loops=section_lines(shape,sec,view)
                self.assertTrue(lines)
                self.assertTrue(loops)

if __name__=='__main__':unittest.main()
