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
                self.fluid_prop_01._viscosity,
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
