import unittest

import numpy as np
import pyxx

from mahautils.multics import (
    SimResults,
    MahaMulticsUnitConverter,
)
from mahautils.multics.exceptions import (
    FileNotParsedError,
)
from mahautils.multics.simresults import _SimResultsEntry
from tests import SAMPLE_FILES_DIR


class Test_SimResultsEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.entry = _SimResultsEntry(True, '')

    def test_repr_str(self):
        # Verifies that string representation is constructed correctly
        for method in ('__repr__', '__str__'):
            repr_str = getattr(self.entry, method)

            self.entry.units = 'm/s'

            with self.subTest(method=method):
                self.entry.required = False
                self.entry.description = 'My description'
                self.entry._data = [0, 2, 9]

                with self.subTest(required=False, description=True, data=True):
                    self.assertEqual(repr_str(), '[Optional] [Units: m/s] My description, [0, 2, 9]')

                self.entry.required = True

                with self.subTest(required=True, description=True, data=True):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description, [0, 2, 9]')

                self.entry._data = None

                with self.subTest(required=True, description=True, data=False):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description')

                self.entry.description = None
                self.entry._data = [0, 2, 9]

                with self.subTest(required=True, description=False, data=True):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] [0, 2, 9]')

                self.entry._data = None

                with self.subTest(required=True, description=False, data=False):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s]')

    def test_data(self):
        # Verifies that "data" attribute correctly converts inputs
        inputs = np.random.rand(50)

        with self.subTest(input_type=None):
            self.entry.data = None
            self.assertIsNone(self.entry.data)

        for type_class in (list, tuple, np.ndarray):
            with self.subTest(input_type=type(type_class)):
                if type_class is np.ndarray:
                    self.entry.data = inputs
                else:
                    self.entry.data = type_class(inputs)

                self.assertIsInstance(self.entry.data, np.ndarray)
                self.assertTrue(np.array_equal(self.entry.data, inputs))
                self.assertEqual(self.entry.data.dtype, np.float64)

        with self.subTest(input_type='invalid'):
            with self.assertRaises(ValueError):
                self.entry.data = np.random.rand(50, 2)

    def test_description(self):
        # Verifies that "description" attribute correctly converts inputs
        with self.subTest(str_input=True, is_none=False):
            self.entry.description = 'my Description'
            self.assertEqual(self.entry.description, 'my Description')

        with self.subTest(str_input=False, is_none=False):
            self.entry.description = 12345
            self.assertEqual(self.entry.description, '12345')

        with self.subTest(is_none=True):
            self.entry.description = None
            self.assertIsNone(self.entry.description)

    def test_group(self):
        # Verifies that "group" attribute correctly converts inputs
        with self.subTest(str_input=True, is_none=False):
            self.entry.group = 'myGroup'
            self.assertEqual(self.entry.group, 'myGroup')

        with self.subTest(str_input=False, is_none=False):
            self.entry.group = 12345
            self.assertEqual(self.entry.group, '12345')

        with self.subTest(is_none=True):
            self.entry.group = None
            self.assertIsNone(self.entry.group)

    def test_required(self):
        # Verifies that "required" attribute correctly validates inputs
        with self.subTest(boolean_input=True):
            self.entry.required = True
            self.assertTrue(self.entry.required)

            self.entry.required = False
            self.assertFalse(self.entry.required)
        
        with self.subTest(boolean_input=False):
            self.entry.required = 1
            self.assertTrue(self.entry.required)

            self.entry.required = 0
            self.assertFalse(self.entry.required)

    def test_units(self):
        # Verifies that "units" attribute correctly converts inputs
        with self.subTest(str_input=True):
            self.entry.units = 'myUnits'
            self.assertEqual(self.entry.units, 'myUnits')

        with self.subTest(str_input=False):
            self.entry.units = 12345
            self.assertEqual(self.entry.units, '12345')


class Test_SimResults(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_results_blank = SimResults()

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

    def test_unit_converter(self):
        # Verifies that a unit converter can be stored and retrieved
        unit_converter = pyxx.units.UnitConverterSI()

        with self.subTest(comment='default'):
            self.assertIsInstance(self.sim_results_blank.unit_converter, MahaMulticsUnitConverter)
            self.assertIsNot(self.sim_results_blank.unit_converter, unit_converter)

        with self.subTest(comment='custom'):
            self.sim_results_blank.unit_converter = unit_converter
            self.assertIs(self.sim_results_blank.unit_converter, unit_converter)

            self.assertIs(SimResults(unit_converter=unit_converter).unit_converter, unit_converter)

        with self.subTest(comment='invalid'):
            with self.assertRaises(TypeError):
                SimResults(unit_converter=print)

    def test_variables(self):
        # Verifies that "variables" attribute functions correctly
        self.assertTupleEqual(
            self.sim_results_01.variables,
            ('t', 'xBody', 'yBody', 'zBody', 'vxBody', 'FxSpring', 'FySpring', 'FzSpring', 'MxBody')
        )

        self.assertTupleEqual(
            self.sim_results_02.variables,
            ('t', 'xBody', 'yBody', 'zBody', 'vxBody', 'FxSpring', 'FySpring', 'FzSpring', 'MxBody')
        )

        self.assertTupleEqual(self.sim_results_blank.variables, ())
