import unittest

import numpy as np
import pyxx

from mahautils.multics import (
    MahaMulticsUnitConverter,
    VTKFile,
)
from mahautils.multics.exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
)
from tests import (
    max_array_diff,
    SAMPLE_FILES_DIR,
    TEST_FLOAT_TOLERANCE,
)


class Test_VTKFile(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_vtk_001 = SAMPLE_FILES_DIR / 'sample_vtk.001.vtk'

        self.vtk = VTKFile()

        self.vtk_read_maha = VTKFile(
            path                     = self.sample_vtk_001,
            use_maha_name_convention = True,
            coordinate_units         = 'mm'
        )
        self.vtk_read_non_maha = VTKFile(
            path                     = self.sample_vtk_001,
            use_maha_name_convention = False
        )

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

        with self.subTest(attr='use_maha_name_convention'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.use_maha_name_convention

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

    def test_check_vtk_id_name(self):
        # Verifies that VTK name-checking correctly implements Maha naming
        # convention
        with self.subTest(issue='incorrect_type'):
            with self.assertRaises(TypeError):
                self.vtk._check_name_convention_compliance_id(10)

        maha_naming_convention = [
            'pFilm[bar]',
            'film_thickness[mm]',
            'ShearForce[N]',
            'velocity[m/s]',
            'a[m/s^2]',
        ]
        not_maha_naming_convention = [
            'film pressure[bar]',
            'film pressure [bar]',
            'filmpressure[Pa gauge]',
            '[bar]',
            'shearStress',
            'pFilm[bar] ',
            '   pFilm[bar]',
        ]

        with self.subTest(use_maha_name_convention=True):
            self.vtk._use_maha_name_convention = True

            for identifier in maha_naming_convention:
                with self.subTest(id=identifier):
                    self.vtk._check_name_convention_compliance_id(identifier)

            for identifier in not_maha_naming_convention:
                with self.subTest(id=identifier):
                    with self.assertRaises(VTKIdentifierNameError):
                        self.vtk._check_name_convention_compliance_id(identifier)

        with self.subTest(use_maha_name_convention=False):
            self.vtk._use_maha_name_convention = False

            for identifier in maha_naming_convention + not_maha_naming_convention:
                with self.subTest(id=identifier):
                    self.vtk._check_name_convention_compliance_id(identifier)

    def test_coordinates_maha(self):
        # Verifies that VTK grid coordinates can be retrieved correctly
        for axis in ('x', 'y', 'z'):
            with self.subTest(axis=axis):
                with self.subTest(units='mm'):
                    self.assertLessEqual(
                        max_array_diff(self.vtk_read_maha.coordinates(axis, 'mm'),
                                       self.sample_vtk_001_coordinates[axis]),
                        TEST_FLOAT_TOLERANCE
                    )

                with self.subTest(units='m'):
                    self.assertLessEqual(
                        max_array_diff(self.vtk_read_maha.coordinates(axis, 'm'),
                                       np.array(self.sample_vtk_001_coordinates[axis]) / 1000),
                        TEST_FLOAT_TOLERANCE
                    )

    def test_coordinates_non_maha(self):
        # Verifies that VTK grid coordinates can be retrieved correctly
        for axis in ('x', 'y', 'z'):
            with self.subTest(axis=axis):
                self.assertLessEqual(
                    max_array_diff(self.vtk_read_non_maha.coordinates(axis),
                                   self.sample_vtk_001_coordinates[axis]),
                    TEST_FLOAT_TOLERANCE
                )

    def test_coordinates_invalid(self):
        # Verifies that appropriate errors are thrown if attempting to
        # retrieve VTK grid point coordinates with invalid arguments
        with self.subTest(issue='not_xyz'):
            with self.assertRaises(ValueError):
                self.vtk_read_maha.coordinates('w')

        with self.subTest(issue='not_read'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.coordinates('x')

    def test_points_maha(self):
        # Verifies that VTK grid points can be retrieved correctly
        points = np.array([
            self.sample_vtk_001_coordinates['x'],
            self.sample_vtk_001_coordinates['y'],
            self.sample_vtk_001_coordinates['z'],
        ]).transpose()

        with self.subTest(unit='mm'):
            self.assertLessEqual(
                max_array_diff(self.vtk_read_maha.points('mm'), points),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(unit='m'):
            self.assertLessEqual(
                max_array_diff(self.vtk_read_maha.points('m'), points / 1000),
                TEST_FLOAT_TOLERANCE
            )

    def test_points_non_maha(self):
        # Verifies that VTK grid points can be retrieved correctly
        points = np.array([
            self.sample_vtk_001_coordinates['x'],
            self.sample_vtk_001_coordinates['y'],
            self.sample_vtk_001_coordinates['z'],
        ]).transpose()

        self.assertLessEqual(
            max_array_diff(self.vtk_read_non_maha.points(), points),
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
                self.assertEqual(self.vtk_read_maha.coordinate_units, 'mm')

            with self.subTest(attribute='use_maha_name_convention'):
                self.assertTrue(self.vtk_read_maha.use_maha_name_convention)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read_maha.num_points, 36)

        with self.subTest(iteration=2):
            self.vtk_read_maha.read(
                path                     = self.sample_vtk_001,
                use_maha_name_convention = False
            )

            with self.subTest(attribute='coordinate_units'):
                self.assertIsNone(self.vtk_read_maha.coordinate_units)

            with self.subTest(attribute='use_maha_name_convention'):
                self.assertFalse(self.vtk_read_maha.use_maha_name_convention)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read_maha.num_points, 36)

    def test_read_invalid(self):
        # Verifies that attempting to read a VTK file with invalid input
        # arguments results in an appropriate error being thrown
        with self.subTest(issue='provided_unit'):
            with self.assertRaises(TypeError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    coordinate_units         = 'km',
                    use_maha_name_convention = False)

        with self.subTest(issue='missing_unit'):
            with self.assertRaises(TypeError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    use_maha_name_convention = True)

        with self.subTest(issue='invalid_unit'):
            with self.assertRaises(ValueError):
                self.vtk.read(
                    path                     = self.sample_vtk_001,
                    use_maha_name_convention = True,
                    coordinate_units         = 'mm * N')
