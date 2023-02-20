import copy
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


class Test_FluidPropertyFile_Interpolate(Test_FluidPropertyFile):
    def setUp(self) -> None:
        super().setUp()

    def test_input_format(self):
        # Verifies that various input format combinations can be used to
        # interpolate data
        with self.subTest(pressure='float',  temperature='float'):
            self.assertListEqual(
                list(self.fluid_prop_01.interpolate(
                    fluid_property='rho', output_units='kg/m^3',
                    pressures=5151.56846, pressure_units='Pa_a',
                    temperatures=202, temperature_units='K',
                    interpolator_type='interpn'
                )),
                [64.33]
            )

        with self.subTest(pressure='float',  temperature='list'):
            self.assertListEqual(
                list(self.fluid_prop_01.interpolate(
                    fluid_property='rho', output_units='kg/m^3',
                    pressures=5151.56846, pressure_units='Pa_a',
                    temperatures=[202, 204, 201], temperature_units='K',
                    interpolator_type='interpn'
                )),
                [64.33, 93, 6]
            )

        with self.subTest(pressure='list',  temperature='float'):
            self.assertListEqual(
                list(self.fluid_prop_01.interpolate(
                    fluid_property='rho', output_units='kg/m^3',
                    pressures=[4151.56846, 5151.56846, 6151.56846], pressure_units='Pa_a',
                    temperatures=202, temperature_units='K',
                    interpolator_type='interpn'
                )),
                [434.343, 64.33, 0.38810113248511946]
            )

        with self.subTest(pressure='list',  temperature='float'):
            self.assertListEqual(
                list(self.fluid_prop_01.interpolate(
                    fluid_property='rho', output_units='kg/m^3',
                    pressures=[5151.56846, 6151.56846, 6151.56846], pressure_units='Pa_a',
                    temperatures=[202, 203, 204], temperature_units='K',
                    interpolator_type='interpn'
                )),
                [64.33, 0.0321, 285]
            )

    def test_interpolator(self):
        # Verify that different interpolation functions produce expected output
        for interpolator in ('interpn', 'griddata'):
            with self.subTest(interpolator=interpolator):
                self.assertLessEqual(
                    max_array_diff(
                        self.fluid_prop_01.interpolate(
                            fluid_property='rho', output_units='kg/m^3',
                            pressures=[4151.56846, 4651.56846, 4151.56846, 4151.56846], pressure_units='Pa_a',
                            temperatures=[203, 201, 201.5, 201.75], temperature_units='K',
                            interpolator_type=interpolator
                        ),
                        [0.6375546402996267, 5.5, 219.6715, 327.00725]
                    ),
                    TEST_FLOAT_TOLERANCE
                )

        # The previous interpolation functions use linear interpolation, so it
        # is easy to calculate the exact, true value.  However, for RBF and
        # Clough-Tocher, the exact solution is harder to calculate, so instead
        # check for similar results on grid points
        for interpolator in ('RBFInterpolator', 'CloughTocher2DInterpolator'):
            with self.subTest(interpolator=interpolator):
                self.assertLessEqual(
                    max_array_diff(
                        self.fluid_prop_01.interpolate(
                            fluid_property='rho', output_units='kg/m^3',
                            pressures=[4151.56846, 5151.56846, 6151.56846], pressure_units='Pa_a',
                            temperatures=201, temperature_units='K',
                            interpolator_type=interpolator
                        ),
                        [5, 6, 201]
                    ),
                    1e-5
                )

                self.assertLessEqual(
                    max_array_diff(
                        self.fluid_prop_01.interpolate(
                            fluid_property='rho', output_units='kg/m^3',
                            pressures=5151.56846, pressure_units='Pa_a',
                            temperatures=[201, 202, 203, 204], temperature_units='K',
                            interpolator_type=interpolator
                        ),
                        [6, 64.33, 0.7343, 93]
                    ),
                    1e-5
                )

    def test_extract_density(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('rho', 'density'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='kg/m^3',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [434.343, 64.33, 0.38810113248511946, 201, 0.38810113248511946, 0.0321, 285]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_bulk_modulus(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('k', 'bulk modulus'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='Pa_a',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [322.3, 434, 0.9379711124129727, 202, 0.9379711124129727, 0.9001, 77]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_kinematic_viscosity(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('nu', 'kinematic viscosity'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='m^2/s',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [5454.3, 322, 0.16381575692650774, 203, 0.16381575692650774, 0.0278, 111]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_specific_heat_capacity(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('cp', 'specific heat capacity'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='J/kg/K',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [55.22, -44394, 0.21676887587733973, 204, 0.21676887587733973, 0.9677, 225]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_thermal_conductivity(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('lambda', 'thermal conductivity'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='W/m/K',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [0.323, 0.0323, 0.42417361438975043, 4151.56846, 0.42417361438975043, 0.0893, 130]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_volumetric_expansion_coefficient(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('alpha', 'volumetric expansion coefficient'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='K^(-1)',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [32.32, 5.4, 0.14077082336360036, 5151.56846, 0.14077082336360036, 0.441, 154]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_specific_enthalpy(self):
        # Verifies that fluid properties directly stored in the fluid property
        # file are extracted correctly
        for prop in ('h', 'specific enthalpy'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='J/kg',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [5, 39.393243943, 0.17791233665353812, 6151.56846, 0.17791233665353812, 0.6033, 152]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_calc_dynamic_viscosity(self):
        # Verifies that dynamic viscosity is calculated correctly based on density
        # and kinematic viscosity
        for prop in ('mu', 'absolute viscosity', 'dynamic viscosity'):
            self.assertLessEqual(
                max_array_diff(
                    self.fluid_prop_01.interpolate(
                        fluid_property=prop, output_units='Pa_a*s',
                        pressures=[4151.56846, 5151.56846, 6151.56846, 6151.56846,
                                   6151.56846, 6151.56846, 6151.56846],
                        pressure_units='Pa_a',
                        temperatures=[202, 202, 202, 201, 202, 203, 204],
                        temperature_units='K',
                        interpolator_type='interpn'
                    ),
                    [2369037.02490000007674098015, 20714.25999999999839928932, 0.06357708078208471059,
                     40803, 0.06357708078208471059, 0.0008923799999999998, 31635]
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_pressure_unit_conversion(self):
        # Verifies that the correct result is interpolated when converting
        # pressure units
        self.assertEqual(
            self.fluid_prop_01.interpolate(
                fluid_property='rho', output_units='kg/m^3',
                pressures=0.0515156846, pressure_units='bar_a',
                temperatures=202, temperature_units='K',
                interpolator_type='interpn'
            )[0],
            64.33
        )

    def test_temperature_unit_conversion(self):
        # Verifies that the correct result is interpolated when converting
        # temperature units
        self.assertAlmostEqual(
            self.fluid_prop_01.interpolate(
                fluid_property='rho', output_units='kg/m^3',
                pressures=5151.56846, pressure_units='Pa_a',
                temperatures=-71.15, temperature_units='degC',
                interpolator_type='interpn'
            )[0],
            64.33
        )

    def test_output_unit_conversion(self):
        # Verifies that the correct result is interpolated when converting
        # output units
        self.assertEqual(
            self.fluid_prop_01.interpolate(
                fluid_property='rho', output_units='g/m^3',
                pressures=5151.56846, pressure_units='Pa_a',
                temperatures=202, temperature_units='K',
                interpolator_type='interpn'
            )[0],
            64330
        )

    def test_not_parsed(self):
        # Verifies that an error is thrown if attempting to interpolate fluid
        # properties before parsing the file
        with self.subTest(read=False):
            with self.assertRaises(FileNotParsedError):
                self.fluid_prop_blank.interpolate(
                    'rho', 'kg/m^3', 0, 'bar', 273.15, 'K', 'interpn')

        with self.subTest(read=True, missing_property='density'):
            file1 = copy.deepcopy(self.fluid_prop_01)
            file1._density = None

            with self.assertRaises(FileNotParsedError):
                file1.interpolate('rho', 'kg/m^3', 0, 'bar', 273.15, 'K', 'interpn')

        with self.subTest(read=True, missing_property='temperature'):
            file2 = copy.deepcopy(self.fluid_prop_01)
            file2._temperature_values = None

            with self.assertRaises(FileNotParsedError):
                file2.interpolate('rho', 'kg/m^3', 0, 'bar', 273.15, 'K', 'interpn')

    def test_incompatible_inputs(self):
        # Verifies that an error is thrown if users provide pressure and
        # temperature inputs of incompatible sizes
        with self.assertRaises(ValueError):
            self.fluid_prop_01.interpolate(
                fluid_property='rho',
                output_units='kg/m^3',
                pressures=[0, 1, 2],
                pressure_units='bar',
                temperatures=[3, 4],
                temperature_units='K',
                interpolator_type='interpn',
            )

    def test_invalid_property(self):
        # Verifies that an error is thrown if users request an invalid fluid property
        with self.assertRaises(ValueError):
            self.fluid_prop_01.interpolate(
                fluid_property='nonexistent_property',
                output_units='kg/m^3',
                pressures=0,
                pressure_units='bar',
                temperatures=273.15,
                temperature_units='K',
                interpolator_type='interpn',
            )

    def test_invalid_interpolator(self):
        # Verifies that an error is thrown if users request an invalid
        # interpolation function
        with self.assertRaises(ValueError):
            self.fluid_prop_01.interpolate(
                fluid_property='rho',
                output_units='kg/m^3',
                pressures=0,
                pressure_units='bar',
                temperatures=273.15,
                temperature_units='K',
                interpolator_type='nonexistent_interpolator',
            )
