import unittest

from mahautils.shapes import Geometry


class Test_Geometry(unittest.TestCase):
    def test_get_set_units(self):
        # Verifies that units can be set and retrieved correctly
        geometry = Geometry()

        with self.subTest(method='default'):
            self.assertIsNone(geometry.units)

        with self.subTest(method='constructor'):
            self.assertEqual(Geometry(units='mm/s').units, 'mm/s')

        with self.subTest(method='attributes'):
            geometry.units = 'kg*ft'
            self.assertEqual(geometry.units, 'kg*ft')

    def test_has_identical_units(self):
        # Verifies that geometry units are considered identical if (1) both
        # are `None` or (2) they are an equal string
        geometry1 = Geometry(units=None)
        geometry2 = Geometry(units='mm')
        geometry3 = Geometry(units='kg')

        with self.subTest(equal=True, none=True):
            self.assertTrue(geometry1._has_identical_units(geometry1))

        with self.subTest(equal=True, none=False):
            self.assertTrue(geometry2._has_identical_units(geometry2))

        with self.subTest(equal=False, first='str', second='str'):
            self.assertFalse(geometry2._has_identical_units(geometry3))

        with self.subTest(equal=False, first='None', second='str'):
            self.assertFalse(geometry1._has_identical_units(geometry2))

        with self.subTest(equal=False, first='str', second='None'):
            self.assertFalse(geometry2._has_identical_units(geometry1))
