import unittest

import numpy as np
import pyxx

from mahautils.multics import (
    SimResults,
    MahaMulticsUnitConverter,
)
from mahautils.multics.exceptions import (
    FileNotParsedError,
    InvalidSimResultsFormatError,
    SimResultsDataNotFoundError,
    SimResultsKeyError,
)
from mahautils.multics.simresults import _SimResultsEntry
from tests import (
    SAMPLE_FILES_DIR,
    max_array_diff,
    TEST_FLOAT_TOLERANCE,
)


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
                self.entry._data = np.array([0, 2, 9])

                with self.subTest(required=False, description=True, data=True):
                    self.assertEqual(repr_str(), '[Optional] [Units: m/s] My description, [0 2 9]')

                self.entry.required = True

                with self.subTest(required=True, description=True, data=True):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description, [0 2 9]')

                self.entry._data = None

                with self.subTest(required=True, description=True, data=False):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description')

                self.entry.description = None
                self.entry._data = np.array([0, 2, 9])

                with self.subTest(required=True, description=False, data=True):
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] [0 2 9]')

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


class Test_SimResults_Parse(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_file_not_read(self):
        # Verifies that an error is thrown if attempting to parse a file which
        # has not been read
        with self.assertRaises(FileNotParsedError):
            self.sim_results_blank.parse()

    def test_missing_description(self):
        # Verifies that an error is thrown if attempting to read a simulation
        # results file where the data array variables line (beginning with "$")
        # is missing a variable description
        with self.assertRaises(InvalidSimResultsFormatError):
            SimResults(SAMPLE_FILES_DIR / 'simulation_results_03.txt')

    def test_data_array_printdict_inconsistency(self):
        # Verifies that an error is thrown if attempting to read a simulation
        # results file where the data array variables line (beginning with "$")
        # and the "printDict" section contain inconsistent data
        with self.subTest(issue='mismatched_variables'):
            with self.assertRaises(InvalidSimResultsFormatError):
                SimResults(SAMPLE_FILES_DIR / 'simulation_results_04.txt')

        with self.subTest(issue='mismatched_units'):
            with self.assertRaises(InvalidSimResultsFormatError):
                SimResults(SAMPLE_FILES_DIR / 'simulation_results_05.txt')

    def test_mismatched_data_array(self):
        # Verifies that an error is thrown if attempting to read a simulation
        # results file where the number of data array variables (listed in the
        # line beginning with "$") and shape of the data array differ
        with self.assertRaises(InvalidSimResultsFormatError):
            SimResults(SAMPLE_FILES_DIR / 'simulation_results_07.txt')

    def test_read_single_data(self):
        # Verifies that a simulation results file with a single outputted
        # variable can be successfully read
        self.assertLessEqual(
            max_array_diff(
                (SimResults(SAMPLE_FILES_DIR / 'simulation_results_06.txt')
                    .get_data('xBody', 'micron')),
                [3.4, 0, 3.32, 434, 4, 5, -232.4, 10]
            ),
            TEST_FLOAT_TOLERANCE
        )


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


class Test_SimResults_Get(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_get_data(self):
        # Verifies that data can be read correctly from the simulation results
        # file (without unit conversions)
        with self.subTest(var='t'):
            self.assertLessEqual(
                max_array_diff(
                    self.sim_results_01.get_data('t', 's'),
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                ),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(var='FySpring'):
            self.assertLessEqual(
                max_array_diff(
                    self.sim_results_01.get_data('FySpring', 'N'),
                    [933, 3, 3, 0, 32, -0.32, 5, 1, 0.543, 0.1, 10]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_get_data_unit_conversion(self):
        # Verifies that data can be read correctly from the simulation results
        # file (with unit conversions)
        with self.subTest(var='t'):
            self.assertLessEqual(
                max_array_diff(
                    self.sim_results_01.get_data('t', 'ms'),
                    [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
                ),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(var='yBody'):
            self.assertLessEqual(
                max_array_diff(
                    self.sim_results_01.get_data('yBody', 'cm'),
                    [0.42, 0, 0.332, 2.3323, 4.3323, 2.35, 0.042343, 3.4, -23.2, 0.0001, 1]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_get_data_invalid(self):
        # Verifies that an error is thrown if attempting to retrieve data
        # that cannot be retrieved
        with self.subTest(issue='nonexistent_var'):
            with self.assertRaises(SimResultsKeyError):
                self.sim_results_01.get_data('nonexistent', 'mm')

        with self.subTest(issue='no_data'):
            with self.assertRaises(SimResultsDataNotFoundError):
                self.sim_results_01.get_data('vxBody', 'micron/s')

    def test_get_description(self):
        # Verifies that the description of simulation results variables is
        # correctly retrieved
        with self.subTest(description_available=True):
            self.assertEqual(self.sim_results_01.get_description('FySpring'),
                             'Spring Force y')

        with self.subTest(description_available=False):
            self.assertIsNone(self.sim_results_01.get_description('FxSpring'))
            self.assertIsNone(self.sim_results_01.get_description('MxBody'))

    def test_get_group(self):
        # Verifies that the group name of simulation results variables is
        # correctly retrieved
        with self.subTest(group_available=True):
            self.assertEqual(self.sim_results_01.get_group('xBody'),
                             'Body Position')
            self.assertEqual(self.sim_results_01.get_group('vxBody'),
                             'Speed')
            self.assertEqual(self.sim_results_01.get_group('FzSpring'),
                             'Spring Force')

        with self.subTest(group_available=False):
            self.assertIsNone(self.sim_results_01.get_group('t'))

    def test_get_required(self):
        # Verifies that simulation results variables are correctly identified
        # as "required" or not
        self.assertTrue(self.sim_results_01.get_required('t'))
        self.assertFalse(self.sim_results_01.get_required('zBody'))
        self.assertFalse(self.sim_results_01.get_required('vxBody'))
        self.assertFalse(self.sim_results_01.get_required('FySpring'))

    def test_list_groups(self):
        # Verifies that a unique list of groups can be identified correctly
        self.assertTupleEqual(
            self.sim_results_01.list_groups(),
            ('Body Position', 'Speed', 'Spring Force', 'Torque')
        )

        self.assertTupleEqual(self.sim_results_02.list_groups(), ())
