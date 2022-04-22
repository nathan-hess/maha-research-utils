##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import unittest

# Custom package and module imports
import mahautils
from mahautils.dict.exceptions import IncompatibleUnits


##############################################################################
# --- TEST CASES: UNIT DICTIONARY ------------------------------------------ #
##############################################################################
class Test_UnitDict(unittest.TestCase):
    def test_convert_m_cm(self):
        # Checks that conversion from meter to centimeters is correct
        unit_dict = mahautils.dict.UnitDict(mahautils.dict.BASE_UNITS['MKS'])
        unit_dict.add_unit('m',  [0,1,0,0,0,0,0], 1,    0)
        unit_dict.add_unit('cm', [0,1,0,0,0,0,0], 0.01, 0)

        self.assertAlmostEqual(
            unit_dict.convert_unit(0.912, from_unit='m', to_unit='cm'),
            91.2
        )

    def test_incompatible_units(self):
        # Checks that incompatible unit types are correctly identified
        unit_dict = mahautils.dict.UnitDict(mahautils.dict.BASE_UNITS['MKS'])
        unit_dict.add_unit('m/s', [0,1,-1,0,0,0,0], 1,    0)
        unit_dict.add_unit('cm',  [0,1, 0,0,0,0,0], 0.01, 0)

        with self.assertRaises(IncompatibleUnits):
            unit_dict.convert_unit(1, from_unit='m/s', to_unit='cm')

    def test_check_defined(self):
        # Checks that a previously-defined unit is correctly identified
        unit_dict = mahautils.dict.UnitDict(mahautils.dict.BASE_UNITS['MKS'])
        unit_dict.add_unit('m',  [0,1,0,0,0,0,0], 1,    0)
        unit_dict.add_unit('cm', [0,1,0,0,0,0,0], 0.01, 0)

        self.assertTrue(unit_dict.check_unit_defined('cm'))
        self.assertTrue(unit_dict.check_unit_defined('m'))

    def test_check_undefined(self):
        # Checks that a unit that is not already defined is correctly identified
        unit_dict = mahautils.dict.UnitDict(mahautils.dict.BASE_UNITS['MKS'])
        unit_dict.add_unit('m',  [0,1,0,0,0,0,0], 1,    0)
        unit_dict.add_unit('cm', [0,1,0,0,0,0,0], 0.01, 0)

        self.assertFalse(unit_dict.check_unit_defined('kg'))
        self.assertFalse(unit_dict.check_unit_defined('m/s'))
        self.assertFalse(unit_dict.check_unit_defined('mol'))

    def test_str(self):
        # Checks that the string representation of a unit dictionary matches
        # expected format
        unit_dict = mahautils.dict.UnitDict(mahautils.dict.BASE_UNITS['MKS'])
        unit_dict.add_unit('m',  [0,1,0,0,0,0,0], 1.00,  0)
        unit_dict.add_unit('cm', [0,1,0,0,0,0,0], 1/100, 0)

        self.assertEqual(
            str(unit_dict),
            ('m   :  {[0, 1, 0, 0, 0, 0, 0]; 1.0*x + 0}\n'
             'cm  :  {[0, 1, 0, 0, 0, 0, 0]; 0.01*x + 0}')
        )
