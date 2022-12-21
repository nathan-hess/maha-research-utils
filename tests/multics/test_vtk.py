import unittest

import numpy as np
import pandas as pd
import pyxx

from mahautils.multics import (
    MahaMulticsUnitConverter,
    VTKFile,
)
from mahautils.multics.exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
    VTKInvalidIdentifierError,
)
from tests import (
    max_array_diff,
    SAMPLE_FILES_DIR,
    TEST_FLOAT_TOLERANCE,
)


class Test_VTKFile(unittest.TestCase):
    def setUp(self) -> None:
        # Define sample VTK file locations and data
        self.sample_vtk_001 = SAMPLE_FILES_DIR / 'sample_vtk.001.vtk'

        self.sample_vtk_001_coordinates = {
            'x': [
                1, 0.86602538824081420898, 0.5, 0, -0.5, -0.86602538824081420898,
                -1, -0.86602538824081420898, -0.5, 0, 0.5, 0.86602538824081420898,
                2, 1.73205077648162841797, 1, 0, -1, -1.73205077648162841797, -2,
                -1.73205077648162841797, -1, 0, 1, 1.73205077648162841797, 3,
                2.59807610511779785156, 1.5, 0, -1.5, -2.59807610511779785156, -3,
                -2.59807610511779785156, -1.5, 0, 1.5, 2.59807610511779785156
            ],
            'y': [
                0, 0.5, 0.86602538824081420898, 1, 0.86602538824081420898, 0.5, 0,
                -0.5, -0.86602538824081420898, -1, -0.86602538824081420898, -0.5,
                0, 1, 1.732050776481628418, 2, 1.732050776481628418, 1, 0, -1,
                -1.732050776481628418, -2, -1.732050776481628418, -1, 0, 1.5,
                2.5980761051177978516, 3, 2.5980761051177978516, 1.5, 0, -1.5,
                -2.5980761051177978516, -3, -2.5980761051177978516, -1.5
            ],
            'z': [0.0] * 36
        }

        self.sample_vtk_001_pFilm = {
            'bar': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0.98322153091430664062, 0.98322182893753051758, 0.98322403430938720703,
                0.98322749137878417969, 0.98323130607604980469, 0.98323452472686767578,
                0.98323613405227661133, 0.98323583602905273438, 0.98323363065719604492,
                0.98323017358779907227, 0.98322635889053344727, 0.98322314023971557617,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ],
            'Pa_a': [
                101325, 101325, 101325, 101325, 101325, 101325,
                101325, 101325, 101325, 101325, 101325, 101325,
                199647.15309143066406, 199647.18289375305176, 199647.4034309387207,
                199647.74913787841797, 199648.13060760498047, 199648.45247268676758,
                199648.61340522766113, 199648.58360290527344, 199648.36306571960449,
                199648.01735877990723, 199647.63588905334473, 199647.31402397155762,
                101325, 101325, 101325, 101325, 101325, 101325,
                101325, 101325, 101325, 101325, 101325, 101325
            ],
        }

        self.sample_vtk_001_hRigid = {
            'micron': [
                20.001745223999023438, 20.0015106201171875, 20.000873565673828125,
                20, 19.999126434326171875, 19.9984893798828125, 19.998254776000976562,
                19.9984893798828125, 19.999126434326171875, 20, 20.000873565673828125,
                20.0015106201171875, 20.003490447998046875, 20.003023147583007812,
                20.001745223999023438, 20, 19.998254776000976562, 19.996976852416992188,
                19.996509552001953125, 19.996976852416992188, 19.998254776000976562,
                20, 20.001745223999023438, 20.003023147583007812, 20.005235671997070312,
                20.004533767700195312, 20.002618789672851562, 20, 19.997381210327148438,
                19.995466232299804688, 19.994764328002929688, 19.995466232299804688,
                19.997381210327148438, 20, 20.002618789672851562, 20.004533767700195312
            ],
            'in': [
                0.00078747028440941037753, 0.00078746104803610974567, 0.00078743596715251287354,
                0.00078740157480314959537, 0.00078736718245378620878, 0.0007873421015701895535,
                0.00078733286519688892163, 0.0007873421015701895535, 0.00078736718245378620878,
                0.00078740157480314959537, 0.00078743596715251287354, 0.00078746104803610974567,
                0.00078753899401567105127, 0.00078752059636153577855, 0.00078747028440941037753,
                0.00078740157480314959537, 0.00078733286519688892163, 0.00078728255324476341219,
                0.00078726415559062803105, 0.00078728255324476341219, 0.00078733286519688892163,
                0.00078740157480314959537, 0.00078747028440941037753, 0.00078752059636153577855,
                0.00078760770362193194185, 0.00078758006959449592885, 0.00078750467675877376412,
                0.00078740157480314959537, 0.00078729847284752553505, 0.00078722308001180337032,
                0.00078719544598436735731, 0.00078722308001180337032, 0.00078729847284752553505,
                0.00078740157480314959537, 0.00078750467675877376412, 0.00078758006959449592885
            ],
        }

        # Create `VTKFile` objects to represent files
        self.vtk = VTKFile()

        self.vtk_read_unit_convert = VTKFile(
            path=self.sample_vtk_001,
            unit_conversion_enabled=True,
            coordinate_units='mm'
        )
        self.vtk_read_no_unit_convert = VTKFile(
            path=self.sample_vtk_001,
            unit_conversion_enabled=False
        )

    def test_uninitialized_attr(self):
        # Verifies that prior to reading a file, an error is thrown or `None`
        # is returned if attempting to access particular attribute
        with self.subTest(attr='coordinate_units'):
            self.assertIsNone(self.vtk.coordinate_units)

        with self.subTest(attr='num_points'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.num_points

        with self.subTest(attr='pointdata_df'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.pointdata_df

        with self.subTest(attr='unit_conversion_enabled'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.unit_conversion_enabled

        with self.subTest(method='extract_data_series'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.extract_data_series('pFilm[bar]')

        with self.subTest(method='extract_dataframe'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.extract_dataframe(['pFilm[bar]'])

    def test_set_unit_converter(self):
        # Verifies that unit converter can set correctly using any
        # available method
        with self.subTest(method='constructor_default'):
            self.assertIs(type(self.vtk.unit_converter), MahaMulticsUnitConverter)

        with self.subTest(method='constructor_arg'):
            vtk = VTKFile(unit_converter=pyxx.units.UnitConverterSI())
            self.assertIs(type(vtk.unit_converter), pyxx.units.UnitConverterSI)

        with self.subTest(method='attribute'):
            self.vtk.unit_converter = pyxx.units.UnitConverterSI()
            self.assertIs(type(self.vtk.unit_converter), pyxx.units.UnitConverterSI)

    def test_set_unit_converter_invalid(self):
        # Verifies that an error is thrown if attempting to set a VTK file
        # unit converter to an invalid type
        with self.assertRaises(TypeError):
            self.vtk.unit_converter = print

    def test_check_unit_conversion_compliance_args(self):
        # Verifies that appropriate errors are thrown (or not thrown) if units
        # are provided or omitted with unit conversion enabled/disabled
        with self.subTest(unit_conversion_enabled=True):
            with self.subTest(args='mm'):
                self.vtk_read_unit_convert._check_unit_conversion_compliance_args('mm')

            with self.subTest(args=None):
                with self.assertRaises(TypeError):
                    self.vtk_read_unit_convert._check_unit_conversion_compliance_args(None)

        with self.subTest(unit_conversion_enabled=False):
            with self.subTest(args='mm'):
                with self.assertRaises(TypeError):
                    self.vtk_read_no_unit_convert._check_unit_conversion_compliance_args('mm')

            with self.subTest(args=None):
                self.vtk_read_no_unit_convert._check_unit_conversion_compliance_args(None)

    def test_check_unit_conversion_compliance_id(self):
        # Verifies that VTK name-checking correctly identifies VTK data
        # identifiers with/without expected naming conventions
        with self.subTest(issue='incorrect_type'):
            with self.assertRaises(TypeError):
                self.vtk._check_unit_conversion_compliance_id(10)

        follows_naming_convention = [
            'pFilm[bar]',
            'film_thickness[mm]',
            'ShearForce[N]',
            'velocity[m/s]',
            'a[m/s^2]',
        ]
        violates_naming_convention = [
            'film pressure[bar]',
            'film pressure [bar]',
            'filmpressure[Pa gauge]',
            '[bar]',
            'shearStress',
            'pFilm[bar] ',
            '   pFilm[bar]',
        ]

        with self.subTest(unit_conversion_enabled=True):
            self.vtk._unit_conversion_enabled = True

            for identifier in follows_naming_convention:
                with self.subTest(id=identifier):
                    self.vtk._check_unit_conversion_compliance_id(identifier)

            for identifier in violates_naming_convention:
                with self.subTest(id=identifier):
                    with self.assertRaises(VTKIdentifierNameError):
                        self.vtk._check_unit_conversion_compliance_id(identifier)

        with self.subTest(unit_conversion_enabled=False):
            self.vtk._unit_conversion_enabled = False

            for identifier in follows_naming_convention + violates_naming_convention:
                with self.subTest(id=identifier):
                    self.vtk._check_unit_conversion_compliance_id(identifier)

    def test_find_column_id_unit_conversion(self):
        # Verifies that column identifier can be retrieved correctly (or an
        # appropriate error thrown) with unit conversions enabled
        for identifier in ('pFilm', 'pFilm[bar]'):
            with self.subTest(identifier=identifier):
                self.assertEqual(
                    self.vtk_read_unit_convert._find_column_id(identifier),
                    'pFilm[bar]'
                )

        with self.subTest(issue='invalid_identifier'):
            with self.assertRaises(VTKInvalidIdentifierError):
                self.vtk_read_unit_convert._find_column_id('Pa')

        with self.subTest(issue='not_string'):
            with self.assertRaises(TypeError):
                self.vtk_read_unit_convert._find_column_id(0)

    def test_find_column_id_no_unit_conversion(self):
        # Verifies that column identifier can be retrieved correctly (or an
        # appropriate error thrown) with unit conversions disabled
        with self.subTest(identifier='pFilm[bar]'):
            self.assertEqual(
                self.vtk_read_no_unit_convert._find_column_id('pFilm[bar]'),
                'pFilm[bar]'
            )

        with self.subTest(issue='invalid_identifier'):
            with self.assertRaises(VTKInvalidIdentifierError):
                self.vtk_read_no_unit_convert._find_column_id('pFilm')

        with self.subTest(issue='not_string'):
            with self.assertRaises(TypeError):
                self.vtk_read_no_unit_convert._find_column_id(0)

    def test_parse_column_id(self):
        # Verifies that identifier names and units can be parsed for VTK
        # data identifiers
        with self.subTest(target='name'):
            self.assertEqual(
                self.vtk_read_unit_convert._parse_column_id('myName[unit0/unit1]', 'name'),
                'myName'
            )

        with self.subTest(target='unit'):
            self.assertEqual(
                self.vtk_read_unit_convert._parse_column_id('myName[unit0/unit1]', 'unit'),
                'unit0/unit1'
            )

    def test_parse_column_id_invalid(self):
        # Verifies that an error is thrown if attempting to extract an invalid
        # "target" value from a VTK data identifier
        with self.subTest(issue='invalid_target'):
            with self.assertRaises(ValueError):
                self.vtk_read_unit_convert._parse_column_id('pFilm[bar]', 'invalid_target')

        with self.subTest(issue='invalid_id'):
            with self.assertRaises(VTKIdentifierNameError):
                self.vtk_read_unit_convert._parse_column_id('pFilm', 'name')

    def test_parse_column_id_no_unit_convert(self):
        # Verifies that an error is thrown if attempting to parse a VTK data
        # identifier with unit conversions disabled
        with self.assertRaises(AttributeError):
            self.vtk_read_no_unit_convert._parse_column_id('pFilm[bar]', 'name')

        with self.assertRaises(AttributeError):
            self.vtk_read_no_unit_convert._parse_column_id('pFilm[bar]', 'unit')

    def test_coordinates_unit_conversion(self):
        # Verifies that VTK grid coordinates can be retrieved correctly
        for axis in ('x', 'y', 'z'):
            with self.subTest(axis=axis):
                with self.subTest(units='mm'):
                    self.assertLessEqual(
                        max_array_diff(self.vtk_read_unit_convert.coordinates(axis, 'mm'),
                                       self.sample_vtk_001_coordinates[axis]),
                        TEST_FLOAT_TOLERANCE
                    )

                with self.subTest(units='m'):
                    self.assertLessEqual(
                        max_array_diff(self.vtk_read_unit_convert.coordinates(axis, 'm'),
                                       np.array(self.sample_vtk_001_coordinates[axis]) / 1000),
                        TEST_FLOAT_TOLERANCE
                    )

    def test_coordinates_no_unit_conversion(self):
        # Verifies that VTK grid coordinates can be retrieved correctly
        for axis in ('x', 'y', 'z'):
            with self.subTest(axis=axis):
                self.assertLessEqual(
                    max_array_diff(self.vtk_read_no_unit_convert.coordinates(axis),
                                   self.sample_vtk_001_coordinates[axis]),
                    TEST_FLOAT_TOLERANCE
                )

    def test_coordinates_invalid(self):
        # Verifies that appropriate errors are thrown if attempting to
        # retrieve VTK grid point coordinates with invalid arguments
        with self.subTest(issue='not_xyz'):
            with self.assertRaises(ValueError):
                self.vtk_read_unit_convert.coordinates('w')

        with self.subTest(issue='not_read'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.coordinates('x')

    def test_extract_data_series_unit_conversion(self):
        # Verifies that a single column of VTK data can be retrieved correctly
        for unit, data in self.sample_vtk_001_pFilm.items():
            with self.subTest(id='pFilm', unit=unit):
                self.assertLessEqual(
                    max_array_diff(
                        self.vtk_read_unit_convert.extract_data_series('pFilm', unit),
                        data
                    ),
                    TEST_FLOAT_TOLERANCE
                )

        for unit, data in self.sample_vtk_001_hRigid.items():
            with self.subTest(id='hRigid', unit=unit):
                self.assertLessEqual(
                    max_array_diff(
                        self.vtk_read_unit_convert.extract_data_series('hRigid', unit),
                        data
                    ),
                    TEST_FLOAT_TOLERANCE
                )

    def test_extract_data_series_no_unit_conversion(self):
        # Verifies that a single column of VTK data can be retrieved correctly
        with self.subTest(id='pFilm[bar]'):
            self.assertLessEqual(
                max_array_diff(
                    self.vtk_read_no_unit_convert.extract_data_series('pFilm[bar]'),
                    self.sample_vtk_001_pFilm['bar']
                ),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(id='hRigid[micron]'):
            self.assertLessEqual(
                max_array_diff(
                    self.vtk_read_no_unit_convert.extract_data_series('hRigid[micron]'),
                    self.sample_vtk_001_hRigid['micron']
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_extract_dataframe_unit_conversion(self):
        # Verifies that a multiple columns of VTK data can be retrieved correctly
        with self.subTest(case='bar,micron'):
            df = self.vtk_read_unit_convert.extract_dataframe(['pFilm', 'hRigid'],
                                                              ['bar',   'micron'])

            df_expected = pd.DataFrame({
                'pFilm[bar]': self.sample_vtk_001_pFilm['bar'],
                'hRigid[micron]': self.sample_vtk_001_hRigid['micron'],
            })

            self.assertTrue(df.equals(df_expected))

        with self.subTest(case='Pa_a,in'):
            df = self.vtk_read_unit_convert.extract_dataframe(['pFilm', 'hRigid'],
                                                              ['Pa_a',  'in'])

            df_expected = pd.DataFrame({
                'pFilm[Pa_a]': self.sample_vtk_001_pFilm['Pa_a'],
                'hRigid[in]': self.sample_vtk_001_hRigid['in'],
            })

            self.assertTrue(df.equals(df_expected))

        with self.subTest(case='Pa_a,micron'):
            df = self.vtk_read_unit_convert.extract_dataframe(['pFilm', 'hRigid'],
                                                              ['Pa_a',  'micron'])

            df_expected = pd.DataFrame({
                'pFilm[Pa_a]': self.sample_vtk_001_pFilm['Pa_a'],
                'hRigid[micron]': self.sample_vtk_001_hRigid['micron'],
            })

            self.assertTrue(df.equals(df_expected))

        with self.subTest(case='invalid_inputs'):
            with self.assertRaises(ValueError):
                df = self.vtk_read_unit_convert.extract_dataframe(['pFilm', 'pFilm'], ['bar'])

    def test_extract_dataframe_no_unit_conversion(self):
        # Verifies that a multiple columns of VTK data can be retrieved correctly
        df = self.vtk_read_no_unit_convert.extract_dataframe(['pFilm[bar]', 'hRigid[micron]'])

        df_expected = pd.DataFrame({
            'pFilm[bar]': self.sample_vtk_001_pFilm['bar'],
            'hRigid[micron]': self.sample_vtk_001_hRigid['micron'],
        })

        df_not_expected = pd.DataFrame({
            'pFilm[bar]': self.sample_vtk_001_pFilm['bar'],
            'hRigid[micron]': self.sample_vtk_001_hRigid['in'],
        })

        self.assertTrue(df.equals(df_expected))
        self.assertFalse(df.equals(df_not_expected))

    def test_points_unit_conversion(self):
        # Verifies that VTK grid points can be retrieved correctly
        points = np.array([
            self.sample_vtk_001_coordinates['x'],
            self.sample_vtk_001_coordinates['y'],
            self.sample_vtk_001_coordinates['z'],
        ]).transpose()

        with self.subTest(unit='mm'):
            self.assertLessEqual(
                max_array_diff(self.vtk_read_unit_convert.points('mm'), points),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(unit='m'):
            self.assertLessEqual(
                max_array_diff(self.vtk_read_unit_convert.points('m'), points / 1000),
                TEST_FLOAT_TOLERANCE
            )

    def test_points_no_unit_conversion(self):
        # Verifies that VTK grid points can be retrieved correctly
        points = np.array([
            self.sample_vtk_001_coordinates['x'],
            self.sample_vtk_001_coordinates['y'],
            self.sample_vtk_001_coordinates['z'],
        ]).transpose()

        self.assertLessEqual(
            max_array_diff(self.vtk_read_no_unit_convert.points(), points),
            TEST_FLOAT_TOLERANCE
        )

    def test_points_invalid(self):
        # Verifies that appropriate errors are thrown if attempting to
        # retrieve VTK grid point coordinates with invalid arguments
        with self.assertRaises(FileNotParsedError):
            self.vtk.points()

    def test_read_set_attributes(self):
        # Verifies that reading a VTK file sets attributes correctly
        with self.subTest(iteration=1):
            with self.subTest(attribute='coordinate_units'):
                self.assertEqual(self.vtk_read_unit_convert.coordinate_units, 'mm')

            with self.subTest(attribute='unit_conversion_enabled'):
                self.assertTrue(self.vtk_read_unit_convert.unit_conversion_enabled)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read_unit_convert.num_points, 36)

        with self.subTest(iteration=2):
            self.vtk_read_unit_convert.read(
                path                     = self.sample_vtk_001,
                unit_conversion_enabled = False
            )

            with self.subTest(attribute='coordinate_units'):
                self.assertIsNone(self.vtk_read_unit_convert.coordinate_units)

            with self.subTest(attribute='unit_conversion_enabled'):
                self.assertFalse(self.vtk_read_unit_convert.unit_conversion_enabled)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read_unit_convert.num_points, 36)

    def test_read_invalid(self):
        # Verifies that attempting to read a VTK file with invalid input
        # arguments results in an appropriate error being thrown
        with self.subTest(issue='provided_unit'):
            with self.assertRaises(TypeError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    coordinate_units         = 'km',
                    unit_conversion_enabled = False)

        with self.subTest(issue='missing_unit'):
            with self.assertRaises(TypeError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    unit_conversion_enabled = True)

        with self.subTest(issue='invalid_unit'):
            with self.assertRaises(ValueError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    unit_conversion_enabled = True,
                    coordinate_units         = 'mm * N')
