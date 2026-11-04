"""Presentation must survive binding without changing measured geometry."""
import json, os, pathlib, unittest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from cad_script_sheet import dimensions
from cad_recipe_executor import text_value
from inspect_bracket_layout import read_columns
from template_layout import bind_dimensions
from script_measurements import anchor
import numpy as np

class Presentation(unittest.TestCase):
 def test_free_text_and_tolerance(self):
  cell={'nominalMm':10.5,'diameterSymbol':True,'displayText':'serbest (1/4 NPTF)','tolerance':{'upperDeviationMm':0,'lowerDeviationMm':-.1}}
  dim=dimensions(BRepPrimAPI_MakeCylinder(5.25,8).Shape(),{'B':cell})[0]
  self.assertEqual(dim['nominal'],10.5)
  self.assertEqual(dim['relation']['surfaces'][0]['radius'],5.25)
  self.assertEqual(text_value(dim),'serbest (1/4 NPTF) (+0/-0,1)')
 def test_custom_text_does_not_authorize_annotation(self):
  dim=dimensions(BRepPrimAPI_MakeCylinder(5.25,8).Shape(),{'B':{'nominalMm':10.5,'diameterSymbol':True,'displayText':'anything'}})[0]
  bound,omitted,unresolved=bind_dimensions([dim],{'candidates':[]})
  self.assertEqual(bound,[]);self.assertEqual(len(omitted),1);self.assertEqual(unresolved,[])
 def test_actual_excel_columns(self):
  self.assertEqual(read_columns('samples/taslak61/taslak6.1.xlsx'),{'A':True,'B':True,'C':False,'D':False,'E':False})
 def test_actual_workbook_through_binding(self):
  path=pathlib.Path(os.environ.get('EXCEL_PRESENTATION_JSON','output/taslak61-parser-check/normalized.json'))
  if not path.exists():self.skipTest('Run ExcelPresentationChecks first for workbook integration')
  rows=json.loads(path.read_text())['rows'];self.assertEqual(len(rows),6)
  expected=['M12x1.5-6H','M12x1.5-6H',"1/4''-18 NPT","1/4''-18 NPTF","1/4''-18 NPTF","1/4''-19 PT"]
  basis=tuple(np.array(x) for x in ([1,0,0],[0,1,0],[0,0,1]))
  for row,text in zip(rows,expected):
   with self.subTest(row=row['outputId']):
    shape=BRepPrimAPI_MakeCylinder(row['cells']['B']['nominalMm']/2,8).Shape()
    ds=dimensions(shape,row['cells']);self.assertEqual(len(ds),5)
    b=next(d for d in ds if d['sourceLabel']=='B')
    layout={'candidates':[{'label':'B','view':'front'}],'sourceFrames':{'front':{'bboxPixels':[0,0,100,100]}}}
    bound,omitted,unresolved=bind_dimensions(ds,layout)
    self.assertEqual(len(bound),1);self.assertEqual(len(omitted),4);self.assertEqual(unresolved,[])
    self.assertEqual(text_value(bound[0]['dimension']),text)
    self.assertEqual(b['relation']['surfaces'][0]['radius'],5.25)
    support=anchor(shape,{'kind':'diameter','nominal':10.5,'center':[0,0,4],'axis':[0,0,1],'radius':5.25},b['nominal'],basis,basis)
    self.assertEqual(support['kind'],'circle')
    c=next(d for d in ds if d['sourceLabel']=='C');self.assertTrue(text_value(c).endswith(' (±0,5)'))
    e=next(d for d in ds if d['sourceLabel']=='E');self.assertEqual(text_value(e),'20,9 (+0/-0,1)')
