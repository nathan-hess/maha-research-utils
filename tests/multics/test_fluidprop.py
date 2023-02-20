import unittest

from mahautils.multics import FluidPropertyFile
from mahautils.multics.exceptions import (
    FileNotParsedError,
    FluidPropertyFileError,
)
from tests import (
    max_array_diff,
    SAMPLE_FILES_DIR,
    TEST_FLOAT_TOLERANCE,
)


class Test_FluidPropertyFile(unittest.TestCase):
    def setUp(self) -> None:
        self.fluid_prop_blank = FluidPropertyFile()
        self.fluid_prop_01 = FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_001.txt')


class Test_FluidPropertyFile_Properties(Test_FluidPropertyFile):
    def setUp(self) -> None:
        super().setUp()

    def test_get_properties_before_parse(self):
        # Verifies that an error is thrown if attempting to retrieve file
        # properties before parsing file
        test_cases = [
            ('get_pressure_step', ('Pa_a',)),
            ('get_pressure_values', ('Pa_a',)),
            ('get_temperature_step', ('K',)),
            ('get_temperature_values', ('K',)),
        ]

        for method, args in test_cases:
            with self.assertRaises(FileNotParsedError):
                getattr(self.fluid_prop_blank, method)(*args)

    def test_num_pressure(self):
        # Checks functionality of "num_pressure" attribute
        with self.subTest(file_read=True):
            self.assertEqual(self.fluid_prop_01.num_pressure, 3)

        with self.subTest(file_read=False):
            with self.assertRaises(FileNotParsedError):
                self.fluid_prop_blank.num_pressure

    def test_num_temperature(self):
        # Checks functionality of "num_temperature" attribute
        with self.subTest(file_read=True):
            self.assertEqual(self.fluid_prop_01.num_temperature, 4)

        with self.subTest(file_read=False):
            with self.assertRaises(FileNotParsedError):
                self.fluid_prop_blank.num_temperature

    def test_get_pressure_step(self):
        # Verifies that pressure step is retrieved correctly
        with self.subTest(units='Pa_a'):
            self.assertEqual(self.fluid_prop_01.get_pressure_step('Pa_a'), 1000)

        with self.subTest(units='bar_a'):
            self.assertEqual(self.fluid_prop_01.get_pressure_step('bar_a'), 0.01)

    def test_get_pressure_values(self):
        # Verifies that pressure values list is retrieved correctly
        with self.subTest(units='Pa_a'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.get_pressure_values('Pa_a'),
                    [4151.56846, 5151.56846, 6151.56846]
                ),
                TEST_FLOAT_TOLERANCE)

        with self.subTest(units='bar_a'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.get_pressure_values('bar_a'),
                    [0.0415156846, 0.0515156846, 0.0615156846]
                ),
                TEST_FLOAT_TOLERANCE)

    def test_get_temperature_step(self):
        # Verifies that temperature step is retrieved correctly
        with self.subTest(units='K'):
            self.assertEqual(self.fluid_prop_01.get_temperature_step('K'), 1)

        with self.subTest(units='degC_diff'):
            self.assertEqual(self.fluid_prop_01.get_temperature_step('degC_diff'), 1)

    def test_get_temperature_values(self):
        # Verifies that temperature values list is retrieved correctly
        with self.subTest(units='K'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.get_temperature_values('K'),
                    [201, 202, 203, 204]
                ),
                TEST_FLOAT_TOLERANCE)

        with self.subTest(units='degC'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.get_temperature_values('degC'),
                    [-72.15, -71.15, -70.15, -69.15]
                ),
                TEST_FLOAT_TOLERANCE)


class Test_FluidPropertyFile_Parse(Test_FluidPropertyFile):
    def setUp(self) -> None:
        super().setUp()

    def test_parse_density(self):
        # Verifies that values are read correctly from the fluid property file
        # when parsing
        self.assertLessEqual(
            max_array_diff(
                self.fluid_prop_01._density,
                [[5,                  6,      201                ],
                 [434.343,            64.33,  0.38810113248511946],
                 [0.6375546402996267, 0.7343, 0.0321             ],
                 [0.1975,             93,     285                ]]
            ),
            TEST_FLOAT_TOLERANCE
        )

    def test_parse_kinematic_viscosity(self):
        # Verifies that values are read correctly from the fluid property file
        # when parsing
        self.assertLessEqual(
            max_array_diff(
                self.fluid_prop_01._viscosity_k,
                [[4.5,                 2,      203                ],
                 [5454.3,              322,    0.16381575692650774],
                 [0.39334265876273344, 0.9544, 0.0278             ],
                 [0.8646,              149,    111                ]]
            ),
            TEST_FLOAT_TOLERANCE
        )

    def test_invalid_incorrect_temperature_step(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_002.txt')

    def test_invalid_incorrect_pressure_step(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_003.txt')

    def test_invalid_incorrect_num_samples(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_004.txt')

    def test_invalid_non_numeric_data(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_005.txt')

    def test_invalid_non_2D_array(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_006.txt')

    def test_invalid_6_fluid_properties(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.assertRaises(FluidPropertyFileError):
            FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_007.txt')

    def test_invalid_missing_metadata(self):
        # Verifies that an error is thrown if attempting to parse files with
        # invalid formatting
        with self.subTest(issue='file_too_short'):
            with self.assertRaises(FluidPropertyFileError):
                FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_008.txt')

        with self.subTest(issue='missing_pressure_temperature'):
            with self.assertRaises(FluidPropertyFileError):
                FluidPropertyFile(SAMPLE_FILES_DIR / 'fluid_properties_009.txt')
