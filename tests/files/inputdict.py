##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import unittest

# Custom package and module imports
import multics
from tests import SAMPLE_FILES_DIR


##############################################################################
# --- TEST CASES: UNIT DICTIONARY ------------------------------------------ #
##############################################################################
class Test_InputDict(unittest.TestCase):
    def test_get_var(self):
        # Check whether the value of a variable is correctly read from
        # a sample input dictionary
        input_dict = multics.files.InputDict()
        input_dict.read(SAMPLE_FILES_DIR / 'inputDict_01.txt')

        self.assertDictEqual(
            input_dict.get_var('Body1Pitch0'),
            {
                'unit': 'deg',
                'value': 93.2,
                'type': 'number',
            }
        )

        self.assertDictEqual(
            input_dict.get_var('BodyIyy'),
            {
                'unit': 'kg*m^2',
                'value': '$BodyIxx',
                'type': 'formula',
            }
        )

        self.assertDictEqual(
            input_dict.get_var('IntegratorRelTol'),
            {
                'unit': '-',
                'value': 0.00000001,
                'type': 'number',
            }
        )
    
    def test_get_var_units(self):
        # Check whether the value of a variable is correctly read from
        # a sample input dictionary and the units converted correctly
        input_dict = multics.files.InputDict()
        input_dict.read(SAMPLE_FILES_DIR / 'inputDict_01.txt')

        self.assertDictEqual(
            input_dict.get_var('BodyMass', units='g'),
            {
                'unit': 'g',
                'value': 1000,
                'type': 'number',
            }
        )

        self.assertDictEqual(
            input_dict.get_var('PrintInterval', units='ms'),
            {
                'unit': 'ms',
                'value': 10,
                'type': 'number',
            }
        )

    def test_get_file(self):
        # Check whether the value of a file path is correctly read from
        # a sample input dictionary
        input_dict = multics.files.InputDict()
        input_dict.read(SAMPLE_FILES_DIR / 'inputDict_01.txt')

        self.assertEqual(
            input_dict.get_file('resultsFile'),
            './simulation_results.txt'
        )

        self.assertEqual(
            input_dict.get_file('outputListFile'),
            '../outputlist.html'
        )

    def test_get_file_abs(self):
        # Check whether the value of a file path is correctly read
        # as an absolute path from a sample input dictionary
        input_dict = multics.files.InputDict()
        input_dict.read(SAMPLE_FILES_DIR / 'inputDict_01.txt')

        self.assertEqual(
            input_dict.get_file('resultsFile', abspath=True),
            str(SAMPLE_FILES_DIR / 'simulation_results.txt')
        )

        self.assertEqual(
            input_dict.get_file('outputListFile', abspath=True),
            str(SAMPLE_FILES_DIR.parent / 'outputlist.html')
        )
