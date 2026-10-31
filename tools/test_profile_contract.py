import copy
import math
import unittest
from profile_contract import normalize_loop
from cad_v9_compiler import compile_recipe
from cad_recipe_executor import build,vol


class Profiles(unittest.TestCase):
    def recipe(self,loop):
        return {'schemaVersion':9,'geometry':{'features':[{'id':'body','op':'add','shape':{'kind':'extrude','profile':{'outer':loop},'extent':{'from':-3,'to':0}}}]},'drawing':{}}
    def test_polyline_closes_locally(self):
        loop={'kind':'polyline','points':[[0,0],[10,0],[10,10],[0,10]]}
        body,_,_=build(compile_recipe(self.recipe(loop),{},'test'))
        self.assertAlmostEqual(vol(body),300,places=5)
    def test_line_arc_chain(self):
        loop={'kind':'path','start':[0,0],'segments':[{'kind':'line','end':[10,0]},{'kind':'arc','mid':[5,5],'end':[0,0]}]}
        original=copy.deepcopy(loop)
        compiled=compile_recipe(self.recipe(loop),{},'test')
        body,_,_=build(compiled)
        self.assertAlmostEqual(vol(body),math.pi*25/2*3,places=5)
        self.assertEqual(loop,original)
    def test_no_invented_closure(self):
        loop={'kind':'path','start':[0,0],'segments':[{'kind':'line','end':[10,0]},{'kind':'line','end':[10,10]}]}
        with self.assertRaisesRegex(ValueError,'not closed'):compile_recipe(self.recipe(loop),{},'test')
    def test_repeated_start_rejected(self):
        loop={'kind':'path','start':[0,0],'segments':[{'kind':'line','start':[1,0],'end':[0,0]}]}
        with self.assertRaisesRegex(ValueError,'repeat start'):normalize_loop(loop)
    def test_legacy_missing_edge_detected(self):
        loop={'kind':'path','closed':True,'segments':[{'kind':'line','start':[0,0],'end':[10,0]},{'kind':'line','start':[10,0],'end':[10,10]}]}
        with self.assertRaisesRegex(ValueError,'not closed'):normalize_loop(loop)
    def test_legacy_disconnected(self):
        loop={'kind':'path','closed':True,'segments':[{'kind':'line','start':[0,0],'end':[10,0]},{'kind':'line','start':[11,0],'end':[0,0]}]}
        with self.assertRaisesRegex(ValueError,'Disconnected'):normalize_loop(loop)
    def test_legacy_closed_profile_supported(self):
        loop={'kind':'path','closed':True,'segments':[{'kind':'line','start':[0,0],'end':[10,0]},{'kind':'line','start':[10,0],'end':[0,10]},{'kind':'line','start':[0,10],'end':[0,0]}]}
        body,_,_=build(compile_recipe(self.recipe(loop),{},'test'))
        self.assertAlmostEqual(vol(body),150,places=5)
    def test_ambiguous_flag_rejected(self):
        with self.assertRaisesRegex(ValueError,'closed flag'):normalize_loop({'kind':'path','start':[0,0],'closed':True,'segments':[]})

if __name__=='__main__':unittest.main()
