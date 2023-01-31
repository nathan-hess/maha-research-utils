import unittest

from mahautils.multics import SimResults
from mahautils.multics.exceptions import (
    FileNotParsedError,
)
from tests import SAMPLE_FILES_DIR


class Test_SimResults(unittest.TestCase):
    def setUp(self) -> None:
        self.file01 = SAMPLE_FILES_DIR / 'simulation_results_01.txt'
        self.sim_results_01 = SimResults(self.file01)

        self.file02 = SAMPLE_FILES_DIR / 'simulation_results_02.txt'
        self.sim_results_02 = SimResults(self.file02)


class Test_SimResults_ReadProperties(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_compile_options(self):
        # Verifies that the simulation options with which Maha Multics was
        # compiled are read correctly
        self.assertDictEqual(
            self.sim_results_01.compile_options,
            {'THERMAL': '0', 'CAV': '0', 'FFI': '1', 'MASS_CON': '0', 'INTERP': '1'}
        )

        self.assertDictEqual(self.sim_results_02.compile_options, {})

    def test_num_time_steps(self):
        # Verifies that the number of time steps is identified correctly
        with self.subTest(file_read=True, contains_data_array=True):
            self.assertEqual(self.sim_results_01.num_time_steps, 11)

        with self.subTest(file_read=True, contains_data_array=False):
            self.assertEqual(self.sim_results_02.num_time_steps, 0)

        with self.subTest(file_read=False):
            with self.assertRaises(FileNotParsedError):
                SimResults().num_time_steps

    def test_title(self):
        # Verifies that title is read correctly from simulation results file
        with self.subTest(title_present=True):
            self.assertEqual(self.sim_results_01.title, 'Sample simulation Results 1')

        with self.subTest(title_present=False):
            self.assertIsNone(self.sim_results_02.title)

    def test_set_title(self):
        # Verifies that the title can be changed
        with self.subTest(valid=True):
            self.sim_results_01.title = 'my New Title'
            self.assertEqual(self.sim_results_01.title, 'my New Title')

        with self.subTest(valid=False):
            with self.assertRaises(TypeError):
                self.sim_results_01.title = 75992
