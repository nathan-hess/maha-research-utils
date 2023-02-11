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
    SimResultsOverwriteError,
)
from mahautils.multics.simresults import _SimResultsEntry
from tests import (
    CapturePrint,
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


class Test_SimResults_General(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_repr(self):
        # Verifies that printable string representation is formatted correctly
        with self.subTest(contents=True):
            self.sim_results_01.clear_data()

            self.assertListEqual(
                self.sim_results_01.__repr__().split('\n'),
                ['<class \'mahautils.multics.simresults.SimResults\'>',
                 f'Title:      {self.sim_results_01.title}',
                 f'Time steps: {self.sim_results_01.num_time_steps}',
                 f'Hashes:     {self.sim_results_01.hashes}',
                 '',
                 'Body Position',
                 '  xBody    : [Optional] [Units: m] Body casing frame position in x',
                 '  yBody    : [Optional] [Units: mm] Body casing frame position in y',
                 '  zBody    : [Optional] [Units: m]',
                 'Speed',
                 '  vxBody   : [Optional] [Units: micron/s]',
                 'Spring Force',
                 '  FxSpring : [Optional] [Units: N]',
                 '  FySpring : [Optional] [Units: N] Spring Force y',
                 '  FzSpring : [Optional] [Units: N] Spring Force z',
                 'Torque',
                 '  MxBody   : [Optional] [Units: N*m]',
                 'No Group Assigned',
                 '  t        : [Required] [Units: s] Sim Time',]
            )

        with self.subTest(contents=False):
            self.assertEqual(
                self.sim_results_blank.__repr__(),
                ('<class \'mahautils.multics.simresults.SimResults\'>\n'
                 'Title:      None\n'
                 'Hashes:     {}\n'
                 '\n'
                 '[No simulation results variables found]')
            )


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


class Test_SimResults_AppendRemove(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_append(self):
        # Verifies that variables can be added to a simulation results file
        self.assertTupleEqual(self.sim_results_blank.variables, ())

        with self.subTest(key='valid'):
            self.sim_results_blank.append(key='velocity1', required=True, units='m/s')
            self.assertTupleEqual(self.sim_results_blank.variables, ('velocity1',))

            self.sim_results_blank.append(key='velocity2', required=True, units='mph', description='myDescription')
            self.assertTupleEqual(self.sim_results_blank.variables, ('velocity1', 'velocity2'))
            self.assertEqual(self.sim_results_blank._data['velocity2'].description, 'myDescription')

        with self.subTest(key='invalid'):
            with self.assertRaises(SimResultsOverwriteError):
                self.sim_results_blank.append(key='velocity1', required=True, units='m/s')

    def test_remove(self):
        # Verifies that variables can be removed from a simulation results file
        with self.subTest(key='valid'):
            self.assertIn('xBody', self.sim_results_01.variables)
            self.sim_results_01.remove('xBody')
            self.assertNotIn('xBody', self.sim_results_01.variables)

        with self.subTest(key='invalid'):
            with self.assertRaises(SimResultsKeyError):
                self.sim_results_01.remove('nonexistent_key')


class Test_SimResults_GetSetAttributes(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_clear_data(self):
        # Verifies that data can be cleared from desired variable(s)
        cleared_vars = self.sim_results_01.clear_data()

        with self.subTest(check='data'):
            for var in self.sim_results_01.variables:
                self.assertIsNone(self.sim_results_01._data[var].data)

        with self.subTest(check='cleared_vars'):
            self.assertListEqual(cleared_vars, list(self.sim_results_01.variables))

    def test_clear_data_regex(self):
        # Verifies that data can be cleared from desired variable(s)
        cleared_vars = self.sim_results_01.clear_data('.Body')

        with self.subTest(check='data'):
            for var in ['xBody', 'yBody', 'zBody']:
                self.assertIsNone(self.sim_results_01._data[var].data)

        with self.subTest(check='cleared_vars'):
            self.assertListEqual(cleared_vars, ['xBody', 'yBody', 'zBody'])

    def test_get_set_data(self):
        # Verifies that data can be read and set correctly from the simulation results
        # file (without unit conversions)
        with self.subTest(var='t'):
            with self.subTest(action='get'):
                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01.get_data('t', 's'),
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

            with self.subTest(action='set'):
                self.sim_results_01.set_data('t', None)

                with self.assertRaises(SimResultsDataNotFoundError):
                    self.sim_results_01.get_data('t', 's')

        with self.subTest(var='FySpring'):
            with self.subTest(action='get'):
                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01.get_data('FySpring', 'N'),
                        [933, 3, 3, 0, 32, -0.32, 5, 1, 0.543, 0.1, 10]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

            with self.subTest(action='set'):
                with self.assertRaises(TypeError):
                    self.sim_results_01.set_data('FySpring', [0, -1.2, 3.4])

                self.sim_results_01.set_data('FySpring', [0, -1.2, 3.4], 'N')

                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01.get_data('FySpring', 'N'),
                        [0, -1.2, 3.4]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

    def test_get_data_unit_conversion(self):
        # Verifies that data can be read and set correctly from the simulation results
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

    def test_get_set_description(self):
        # Verifies that the description of simulation results variables is
        # correctly retrieved and saved
        with self.subTest(action='get'):
            with self.subTest(description_available=True):
                self.assertEqual(self.sim_results_01.get_description('FySpring'),
                                 'Spring Force y')

            with self.subTest(description_available=False):
                self.assertIsNone(self.sim_results_01.get_description('FxSpring'))
                self.assertIsNone(self.sim_results_01.get_description('MxBody'))

        with self.subTest(action='set'):
            self.sim_results_01.set_description('FySpring', 'new Description')
            self.assertEqual(self.sim_results_01.get_description('FySpring'),
                             'new Description')

    def test_get_set_group(self):
        # Verifies that the group name of simulation results variables is
        # correctly retrieved and saved
        with self.subTest(action='get'):
            with self.subTest(group_available=True):
                self.assertEqual(self.sim_results_01.get_group('xBody'),
                                 'Body Position')
                self.assertEqual(self.sim_results_01.get_group('vxBody'),
                                 'Speed')
                self.assertEqual(self.sim_results_01.get_group('FzSpring'),
                                 'Spring Force')

            with self.subTest(group_available=False):
                self.assertIsNone(self.sim_results_01.get_group('t'))

        with self.subTest(action='set'):
            self.sim_results_01.set_group('xBody', 'newGroup')
            self.assertEqual(self.sim_results_01.get_group('xBody'),
                             'newGroup')

    def test_get_set_required(self):
        # Verifies that simulation results variables are correctly identified
        # as "required" or not
        with self.subTest(action='get'):
            self.assertTrue(self.sim_results_01.get_required('t'))
            self.assertFalse(self.sim_results_01.get_required('zBody'))
            self.assertFalse(self.sim_results_01.get_required('vxBody'))
            self.assertFalse(self.sim_results_01.get_required('FySpring'))

        with self.subTest(action='set'):
            self.sim_results_01.set_required('t', True)
            self.assertTrue(self.sim_results_01.get_required('t'))

            self.sim_results_01.set_required('t', False)
            self.assertFalse(self.sim_results_01.get_required('t'))

    def test_get_set_units_error(self):
        # Verifies that simulation results variable units can be retrieved
        # and stored as expected
        with self.subTest(data_present=True):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('t'), 's')

            with self.subTest(action='set'):
                self.sim_results_01.set_units('t', 's')

                with self.assertRaises(SimResultsOverwriteError):
                    self.sim_results_01.set_units('t', 'ms', 'error')

        with self.subTest(data_present=False):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'micron/s')

            with self.subTest(action='set'):
                self.sim_results_01.set_units('vxBody', 'mm/s', 'error')
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'mm/s')

    def test_get_set_units_convert_data(self):
        # Verifies that simulation results variable units can be retrieved
        # and stored as expected
        with self.subTest(data_present=True):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('t'), 's')

            with self.subTest(action='set'):
                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01._data['t'].data,
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

                self.sim_results_01.set_units('t', 'ms', 'convert_data')

                self.assertEqual(self.sim_results_01.get_units('t'), 'ms')

                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01._data['t'].data,
                        [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

        with self.subTest(data_present=False):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'micron/s')

            with self.subTest(action='set'):
                self.sim_results_01.set_units('vxBody', 'mm/s', 'convert_data')
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'mm/s')

    def test_get_set_units_keep_data_values(self):
        # Verifies that simulation results variable units can be retrieved
        # and stored as expected
        with self.subTest(data_present=True):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('t'), 's')

            with self.subTest(action='set'):
                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01._data['t'].data,
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

                self.sim_results_01.set_units('t', 'ms', 'keep_data_values')

                self.assertEqual(self.sim_results_01.get_units('t'), 'ms')

                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01._data['t'].data,
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

        with self.subTest(data_present=False):
            with self.subTest(action='get'):
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'micron/s')

            with self.subTest(action='set'):
                self.sim_results_01.set_units('vxBody', 'mm/s', 'keep_data_values')
                self.assertEqual(self.sim_results_01.get_units('vxBody'), 'mm/s')

    def test_get_set_units_invalid(self):
        # Verifies that simulation results variable units can be retrieved
        # and stored as expected
        with self.assertRaises(ValueError):
            self.sim_results_01.set_units('vxBody', 'mm/s', 'invalid_action')

    def test_list_groups(self):
        # Verifies that a unique list of groups can be identified correctly
        self.assertTupleEqual(
            self.sim_results_01.list_groups(),
            ('Body Position', 'Speed', 'Spring Force', 'Torque')
        )

        self.assertTupleEqual(self.sim_results_02.list_groups(), ())


class Test_SimResults_Search(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

    def test_search_keys(self):
        # Verifies that searching keys works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='body', search_fields='keys',
                print_results=False, return_results=True),
            ('xBody', 'yBody', 'zBody', 'vxBody', 'MxBody')
        )

    def test_search_description(self):
        # Verifies that searching descriptions works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='body', search_fields='description',
                print_results=False, return_results=True),
            ('xBody', 'yBody')
        )

    def test_search_group(self):
        # Verifies that searching groups works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='body', search_fields='group',
                print_results=False, return_results=True),
            ('xBody', 'yBody', 'zBody')
        )

    def test_search_units(self):
        # Verifies that searching units works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='s', search_fields='units',
                print_results=False, return_results=True),
            ('t', 'vxBody')
        )

    def test_search_multiple(self):
        # Verifies that searching multiple fields works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='s', search_fields=('keys', 'units'),
                print_results=False, return_results=True),
            ('t', 'vxBody', 'FxSpring', 'FySpring', 'FzSpring')
        )

    def test_search_case_sensitive(self):
        # Verifies that searching multiple fields works correctly
        self.assertTupleEqual(
            self.sim_results_01.search(
                keyword='s', case_sensitive=True,
                search_fields=('keys', 'description', 'group', 'units'),
                print_results=False, return_results=True),
            ('t', 'xBody', 'yBody', 'zBody', 'vxBody')
        )

    def test_invalid_search_fields(self):
        # Verifies that an error is thrown if attempting to perform a search
        # within invalid search fields
        with self.assertRaises(ValueError):
            self.sim_results_01.search('', search_fields=('keys', 'invalid'))

    def test_search_print(self):
        # Verifies that search results are printed correctly
        self.sim_results_01.clear_data()

        with CapturePrint() as terminal_stdout:
            self.assertIsNone(self.sim_results_01.search(
                keyword='sp', print_results=True, return_results=False
            ))

            self.assertEqual(
                terminal_stdout.getvalue(),
                ('Speed\n'
                 '  vxBody   : [Optional] [Units: micron/s]\n'
                 'Spring Force\n'
                 '  FxSpring : [Optional] [Units: N]\n'
                 '  FySpring : [Optional] [Units: N] Spring Force y\n'
                 '  FzSpring : [Optional] [Units: N] Spring Force z\n')
            )


class Test_SimResults_UpdateContents(Test_SimResults):
    def setUp(self) -> None:
        super().setUp()

        self.sim_results_01.contents.clear()
        self.assertListEqual(self.sim_results_01.contents, [])

        self.sim_results_blank.contents.clear()
        self.assertListEqual(self.sim_results_blank.contents, [])

    def test_update_content_blank(self):
        # Verifies that "contents" attribute can be updated with a minimal set of data
        self.sim_results_blank.update_contents()

        self.assertListEqual(
            self.sim_results_blank.contents,
            [
                'printDict{',
                '}',
            ]
        )

    def test_update_content_data(self):
        # Verifies that "contents" attribute can be updated with a simulation results
        # file populated with data
        self.sim_results_01.update_contents()

        self.assertListEqual(
            self.sim_results_01.contents,
            [
                '# Title: Sample simulation Results 1',
                '',
                'printDict{',
                '    @t           [s]',
                '',
                '    # Body Position',
                '    ?xBody       [m]',
                '    ?yBody       [mm]',
                '    ?zBody       [m]',
                '',
                '    # Speed',
                '    ?vxBody      [micron/s]',
                '',
                '    # Spring Force',
                '    ?FxSpring    [N]',
                '    ?FySpring    [N]',
                '    ?FzSpring    [N]',
                '',
                '    # Torque',
                '    ?MxBody      [N*m]',
                '}',
                ('$t:s:Sim Time$xBody:m:Body casing frame position in x'
                 '$yBody:mm:Body casing frame position in y$zBody:m:$FxSpring:N:'
                 '$FySpring:N:Spring Force y$FzSpring:N:Spring Force z'),
                '#_OPTIONs: THERMAL = 0, CAV = 0, FFI = 1, MASS_CON = 0, INTERP = 1',
                '0.0 3.4 4.2 2.1 -1000.0 933.0 0.0',
                '1.0 0.0 0.0 -4.0 9.0 3.0 933.0',
                '2.0 9.0 3.32 3.0 99.3 3.0 0.0021',
                '3.0 434.0 23.323 93.24323 3.0 0.0 -220.32332',
                '4.0 323.0 43.323 399.0 -0.3 32.0 959.0',
                '5.0 4.32 23.5 69.0 32.0 -0.32 3.54993',
                '6.0 34.0 0.42343 2.34e-08 3.21 5.0 1.0',
                '7.0 4.3 34.0 990.0 3.0 1.0 2.0',
                '8.0 3000.0 -232.0 43.0 3.32 0.543 114.0',
                '9.0 0.0 0.001 3693.3 9.4 0.1 3332.4',
                '10.0 10.0 10.0 10.0 10.0 10.0 10.0',
            ]
        )

    def test_update_content_no_data(self):
        # Verifies that "contents" attribute can be updated with a simulation results
        # file populated with data, excluding the simulation results data
        self.sim_results_01.update_contents(add_sim_data=False)

        self.assertListEqual(
            self.sim_results_01.contents,
            [
                '# Title: Sample simulation Results 1',
                '',
                'printDict{',
                '    @t           [s]',
                '',
                '    # Body Position',
                '    ?xBody       [m]',
                '    ?yBody       [mm]',
                '    ?zBody       [m]',
                '',
                '    # Speed',
                '    ?vxBody      [micron/s]',
                '',
                '    # Spring Force',
                '    ?FxSpring    [N]',
                '    ?FySpring    [N]',
                '    ?FzSpring    [N]',
                '',
                '    # Torque',
                '    ?MxBody      [N*m]',
                '}',
            ]
        )
