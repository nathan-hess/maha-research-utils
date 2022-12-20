import unittest

from mahautils.multics import VTKFile
from mahautils.multics.exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
)
from tests import SAMPLE_FILES_DIR


class Test_VTKFile(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_vtk_001 = SAMPLE_FILES_DIR / 'sample_vtk.001.vtk'

        self.vtk = VTKFile()
        self.vtk_read = VTKFile(
            path                     = self.sample_vtk_001,
            use_maha_name_convention = True,
            coordinate_units         = 'mm'
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

        with self.subTest(attr='use_maha_name_convention'):
            with self.assertRaises(FileNotParsedError):
                self.vtk.use_maha_name_convention

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

    def test_read_set_attributes(self):
        # Verifies that reading a VTK file sets attributes correctly
        with self.subTest(iteration=1):
            with self.subTest(attribute='coordinate_units'):
                self.assertEqual(self.vtk_read.coordinate_units, 'mm')

            with self.subTest(attribute='use_maha_name_convention'):
                self.assertTrue(self.vtk_read.use_maha_name_convention)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read.num_points, 36)

        with self.subTest(iteration=2):
            self.vtk_read.read(
                path                     = self.sample_vtk_001,
                use_maha_name_convention = False
            )

            with self.subTest(attribute='coordinate_units'):
                self.assertIsNone(self.vtk_read.coordinate_units)

            with self.subTest(attribute='use_maha_name_convention'):
                self.assertFalse(self.vtk_read.use_maha_name_convention)

            with self.subTest(attribute='num_points'):
                self.assertEqual(self.vtk_read.num_points, 36)

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
