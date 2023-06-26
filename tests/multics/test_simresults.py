import copy
import unittest

import numpy as np

from mahautils.multics import SimResults
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
        self.original_show_data = _SimResultsEntry.show_data

    def tearDown(self) -> None:
        _SimResultsEntry.show_data = self.original_show_data

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

    def test_repr_str_show_data(self):
        # Verifies that showing data can be enabled or disabled
        for method in ('__repr__', '__str__'):
            repr_str = getattr(self.entry, method)

            self.entry.units = 'm/s'
            self.entry._data = np.array([0, 2, 9])
            self.entry.description = 'My description'

            with self.subTest(method=method):
                with self.subTest(show_data=False):
                    _SimResultsEntry.show_data = False
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description')

                with self.subTest(show_data=True):
                    _SimResultsEntry.show_data = True
                    self.assertEqual(repr_str(), '[Required] [Units: m/s] My description, [0 2 9]')

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

        self.original_show_data = _SimResultsEntry.show_data

    def tearDown(self) -> None:
        _SimResultsEntry.show_data = self.original_show_data

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
                 'Time steps: 0\n'
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

    def test_missing_printdict(self):
        # Verifies that an error is thrown if attempting to read a simulation
        # results file without a "printDict" section
        with self.assertRaises(InvalidSimResultsFormatError):
            SimResults(SAMPLE_FILES_DIR / 'simulation_results_08.txt')


class Test_SimResults_RemoveAsteriskVars(Test_SimResults):
    def test_replace_variables(self):
        # Verifies that variables with an asterisk are removed prior to
        # parsing simulation results files
        self.sim_results_blank.set_contents(
            [
                'printDict{',
                '    @firstVar_** [m]',
                '    @secondVar [m]',
                '    ?thirdVar_** [m]',
                '    @fourthVar_*(1,5) [m]',
                '    @fifthVar_*(1,5) [m]',
                '    ?sixthVar [m]',
                '    ?seventhVar_**.*(1,2)data [m]',
                '    ?eighthVar [m]',
                '}',
                ('$firstVar_1::$firstVar_2::$secondVar::$fourthVar_3::$fourthVar_60::'
                 '$fourthVar_7::$seventhVar_12.3data::$seventhVar_3.142data::'),
            ],
            trailing_newline=True,
        )

        self.sim_results_blank._remove_vars_with_asterisk()

        self.assertListEqual(
            self.sim_results_blank.contents,
            [
                'printDict{',
                '    @firstVar_1 [m]',
                '    @firstVar_2 [m]',
                '    @secondVar [m]',
                '    @fourthVar_3 [m]',
                '    @fourthVar_60 [m]',
                '    @fourthVar_7 [m]',
                '    ?sixthVar [m]',
                '    ?seventhVar_12.3data [m]',
                '    ?seventhVar_3.142data [m]',
                '    ?eighthVar [m]',
                '}',
                ('$firstVar_1::$firstVar_2::$secondVar::$fourthVar_3::$fourthVar_60::'
                 '$fourthVar_7::$seventhVar_12.3data::$seventhVar_3.142data::'),
            ],
        )

    def test_replace_variables_first_line(self):
        # Verifies that variables with an asterisk are removed prior to
        # parsing simulation results files
        self.sim_results_blank.set_contents(
            [
                'printDict{@firstVar_** [m]',
                '    @secondVar [m]',
                '    ?thirdVar_** [m]',
                '}',
                '$firstVar_1::$firstVar_2::$secondVar::',
            ],
            trailing_newline=True,
        )

        self.sim_results_blank._remove_vars_with_asterisk()

        self.assertListEqual(
            self.sim_results_blank.contents,
            [
                'printDict{',
                '    @firstVar_1 [m]',
                '    @firstVar_2 [m]',
                '    @secondVar [m]',
                '}',
                '$firstVar_1::$firstVar_2::$secondVar::',
            ],
        )

    def test_missing_sim_results(self):
        # Verifies that if variables with an asterisk are present in the
        # "printDict" section but no simulation results data are present, an
        # exception is thrown
        self.sim_results_blank.set_contents(
            [
                'printDict{',
                '    @myVar** [m]',
                '}',
            ],
            trailing_newline=True,
        )

        with self.assertRaises(SimResultsDataNotFoundError):
            self.sim_results_blank.parse()


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
            self.assertEqual(SimResults().num_time_steps, 0)

    def test_metadata(self):
        # Verifies that metadata fields are read correctly from simulation results file
        attributes = ['title', 'maha_multics_version', 'maha_multics_commit', 'sim_version']
        values = ['Sample simulation Results 1', 'v4116.7.30', 'fb8aa721e23fb7b0c751ec31c258cdc3f85a4c31', 'v8.2.8']

        for attr, value in zip(attributes, values):
            with self.subTest(field=attr):
                with self.subTest(attr_present=True):
                    self.assertEqual(getattr(self.sim_results_01, attr), value)

                with self.subTest(attr_present=False):
                    self.assertIsNone(getattr(self.sim_results_02, attr))

    def test_set_metadata(self):
        # Verifies that metadata fields can be changed
        for attr in ['title', 'maha_multics_version', 'maha_multics_commit', 'sim_version']:
            with self.subTest(field=attr):
                with self.subTest(valid=True):
                    setattr(self.sim_results_01, attr, 'my New Title')
                    self.assertEqual(getattr(self.sim_results_01, attr), 'my New Title')

                with self.subTest(valid=False):
                    with self.assertRaises(TypeError):
                        setattr(self.sim_results_01, attr, 75992)

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

    def test_clear_data_num_time_steps(self):
        # Verifies that number of time steps is updated correctly when clearing data
        sim_results = copy.deepcopy(self.sim_results_01)
        with self.subTest(clear_all=True):
            self.assertEqual(sim_results.num_time_steps, 11)
            _ = sim_results.clear_data()
            self.assertEqual(sim_results.num_time_steps, 0)

        sim_results = copy.deepcopy(self.sim_results_01)
        with self.subTest(clear_all=False):
            self.assertEqual(sim_results.num_time_steps, 11)
            _ = sim_results.clear_data('.Body')
            self.assertEqual(sim_results.num_time_steps, 11)

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

                self.sim_results_01.set_data(
                    'FySpring', [0, -1.2, 3.4, 5, -6, 7, 8, 9, 10, 11, 12], 'N')

                self.assertLessEqual(
                    max_array_diff(
                        self.sim_results_01.get_data('FySpring', 'N'),
                        [0, -1.2, 3.4, 5, -6, 7, 8, 9, 10, 11, 12]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

                with self.assertRaises(ValueError):
                    self.sim_results_01.set_data('FySpring', [0, -1.2, 3.4], 'N')

    def test_set_data_num_time_steps(self):
        # Verifies that number of time steps is updated correctly when setting data
        self.assertEqual(self.sim_results_02.num_time_steps, 0)
        self.sim_results_02.set_data('yBody', [0, 1, 2, 3], 'm')
        self.assertEqual(self.sim_results_02.num_time_steps, 4)

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
        _SimResultsEntry.show_data = False

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
                '# Multics Version: v4116.7.30',
                '# Multics Git Commit Hash: fb8aa721e23fb7b0c751ec31c258cdc3f85a4c31',
                '# Main Sketch Version: v8.2.8',
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
                '# Multics Version: v4116.7.30',
                '# Multics Git Commit Hash: fb8aa721e23fb7b0c751ec31c258cdc3f85a4c31',
                '# Main Sketch Version: v8.2.8',
            ]
        )

    def test_update_content_no_compile_options(self):
        # Verifies that "contents" attribute can be updated with a simulation results
        # file populated with data but no compilation options
        self.sim_results_01.compile_options.clear()
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
                '# Multics Version: v4116.7.30',
                '# Multics Git Commit Hash: fb8aa721e23fb7b0c751ec31c258cdc3f85a4c31',
                '# Main Sketch Version: v8.2.8',
                ('$t:s:Sim Time$xBody:m:Body casing frame position in x'
                 '$yBody:mm:Body casing frame position in y$zBody:m:$FxSpring:N:'
                 '$FySpring:N:Spring Force y$FzSpring:N:Spring Force z'),
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
