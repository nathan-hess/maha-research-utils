##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import unittest

# Custom package and module imports
import mahautils
from tests import SAMPLE_FILES_DIR


##############################################################################
# --- TEST CASES: SIMULATION RESULTS --------------------------------------- #
##############################################################################
class Test_SimResults(unittest.TestCase):
    def test_printvars(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and identifies the print variables
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertListEqual(
            list(data.printvars),
            ['t', 'xBody', 'yBody', 'zBody', 'FxSpring', 'FySpring', 'FzSpring']
        )

    def test_title(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and identifies the title
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertEqual(
            data.title,
            'Sample simulation Results 1'
        )

    def test_units(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and identifies the units
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertListEqual(
            data.units,
            ['s', 'm', 'm', 'm', 'N', 'N', 'N']
        )

    def test_descriptions(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and identifies the descriptions
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertListEqual(
            data.descriptions,
            ['Sim Time', 'Body casing frame position in x', 'Body casing frame position in y',
             'Body casing frame position in z', 'Spring Force x', 'Spring Force y', 'Spring Force z']
        )

    def test_get_01(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and extracts simulation result data
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.get('t'),
            {
                'units': 's',
                'description': 'Sim Time',
                'data': (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0)
            }
        )

    def test_get_02(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and extracts simulation result data
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.get('yBody'),
            {
                'units': 'm',
                'description': 'Body casing frame position in y',
                'data': (4.2, 0.0, 3.32, 23.323, 43.323, 23.5, 0.42343, 34.0, -232.0, 0.001, 10.0)
            }
        )

    def test_get_03(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and extracts simulation result data
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.get('FxSpring'),
            {
                'units': 'N',
                'description': 'Spring Force x',
                'data': (-1000.0, 9.0, 99.3, 3.0, -0.3, 32.0, 3.21, 3.0, 3.32, 9.4, 10.0)
            }
        )

    def test_search_noninteractive_01(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.search_noninteractive('t'),
            {
                'match_found': True,
                'match_type': 'printvar',
                'matches_printvar': ['t'],
            }
        )

    def test_search_noninteractive_02(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.search_noninteractive('Spring Force x'),
            {
                'match_found': True,
                'match_type': 'description',
                'matches_description': ['FxSpring'],
            }
        )

    def test_search_noninteractive_03(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertDictEqual(
            data.search_noninteractive('Position'),
            {
                'match_found': False,
                'matches_description': ['xBody', 'yBody', 'zBody'],
            }
        )

    def test_search_noninteractive_04(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertEqual(
            data.search_noninteractive('in'),
            {
                'match_found': False,
                'matches_printvar': ['FxSpring', 'FySpring', 'FzSpring'],
                'matches_description': ['xBody', 'yBody', 'zBody', 'FxSpring', 'FySpring', 'FzSpring']
            }
        )

    def test_search_noninteractive_05(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertEqual(
            data.search_noninteractive('nonExistentTerm'),
            {'match_found': False}
        )

    def test_search_noninteractive_case(self):
        # Checks that `mahautils.files.SimResults()` correctly reads a sample
        # file and searches for a term (case-sensitive)
        data = mahautils.files.SimResults(SAMPLE_FILES_DIR / 'simulation_results_01.txt')

        self.assertEqual(
            data.search_noninteractive('Position', case_sensitive=True),
            {'match_found': False}
        )
