import unittest
from cad_script_sheet import unbound_nonmeasurement
class Nonmeasurement(unittest.TestCase):
 def test_metadata_is_ignored_but_real_dimensions_preserved(self):
  record={'source':'H','nominal':None,'unresolved':'title field'}
  self.assertTrue(unbound_nonmeasurement(record,{}))
  self.assertFalse(unbound_nonmeasurement(record,{'H':{}}))
  self.assertFalse(unbound_nonmeasurement(dict(record,source='5'),{}))
  self.assertFalse(unbound_nonmeasurement(dict(record,markerId='m'),{}))
  self.assertFalse(unbound_nonmeasurement(dict(record,nominal=5),{}))
