import copy
import unittest

import numpy as np

from mahautils.shapes import (
    CartesianPoint2D,
    Point,
)


class Test_Point(unittest.TestCase):
    def setUp(self):
        self.point = Point()

        self.point2D = Point()
        self.point2D._coordinates = (1.5, 2.5)

        self.point3D = Point()
        self.point3D._coordinates = (3, 4, 5)

    def test_initialize(self):
        # Verifies that `Point` class is initialized with empty coordinates
        self.assertTupleEqual(self.point._coordinates, ())

    def test_eq(self):
        # Verify that equality between `Point` objects functions as expected
        with self.subTest(case='same_point'):
            self.assertEqual(self.point, self.point)
            self.assertEqual(self.point2D, self.point2D)
            self.assertEqual(self.point3D, self.point3D)

        with self.subTest(case='same_point_different_type'):
            (pnt := Point())._coordinates = (3.0, 4, 5.0)
            self.assertEqual(pnt, self.point3D)

        with self.subTest(case='different_length'):
            self.assertNotEqual(self.point2D, self.point3D)

        with self.subTest(case='different_values'):
            (pnt := Point())._coordinates = (3, 4.001, 5)
            self.assertNotEqual(pnt, self.point3D)

        with self.subTest(cause='different_units'):
            point3D_units = copy.deepcopy(self.point3D)
            point3D_units.units = 'm'

            self.assertNotEqual(self.point3D, point3D_units)

    def test_len(self):
        # Verifies that the "length" attribute of points is returned correctly
        with self.subTest(len=0):
            self.assertEqual(len(self.point), 0)

        with self.subTest(len=2):
            self.assertEqual(len(self.point2D), 2)

        with self.subTest(len=3):
            self.assertEqual(len(self.point3D), 3)

    def test_repr(self):
        # Verifies that printable string representation of `Point` objects
        # is returned correctly
        class_name = "<class 'mahautils.shapes.geometry.point.Point'>"

        with self.subTest(dim=0):
            self.assertEqual(self.point.__repr__(), f'{class_name} ()')

        with self.subTest(dim=2):
            self.assertEqual(self.point2D.__repr__(), f'{class_name} (1.5, 2.5)')

        with self.subTest(dim=3):
            self.assertEqual(self.point3D.__repr__(), f'{class_name} (3, 4, 5)')

    def test_str(self):
        # Verifies that string representation of `Point` objects is
        # returned correctly
        with self.subTest(dim=0):
            self.assertEqual(str(self.point), '()')

        with self.subTest(dim=2):
            self.assertEqual(str(self.point2D), '(1.5, 2.5)')

        with self.subTest(dim=3):
            self.assertEqual(str(self.point3D), '(3, 4, 5)')

    def test_getitem(self):
        # Verifies that point coordinates can be retrieved by index
        with self.subTest(dimensions=2):
            with self.subTest(access='int'):
                self.assertEqual(self.point2D[0], 1.5)
                self.assertEqual(self.point2D[1], 2.5)

            with self.subTest(access='slice'):
                self.assertTupleEqual(self.point2D[0:], (1.5, 2.5))

        with self.subTest(dimensions=3):
            with self.subTest(access='int'):
                self.assertEqual(self.point3D[0], 3)
                self.assertEqual(self.point3D[1], 4)
                self.assertEqual(self.point3D[2], 5)

            with self.subTest(access='slice'):
                self.assertTupleEqual(self.point3D[1:], (4, 5))

    def test_iterable(self):
        # Verifies that it is possible to iterate over the coordinates of the
        # point. Each is tested twice to ensure iterables "reset" correctly
        self.assertListEqual(list(self.point2D), [1.5, 2.5])
        self.assertListEqual(list(self.point2D), [1.5, 2.5])

        next(self.point2D)
        self.assertListEqual(list(self.point2D), [1.5, 2.5])

        self.assertTupleEqual(tuple(self.point3D), (3, 4, 5))
        self.assertTupleEqual(tuple(self.point3D), (3, 4, 5))

    def test_get_coordinates(self):
        # Verifies that "coordinates" attribute correctly retrieves
        # point coordinates
        with self.subTest(dim=0):
            self.assertTupleEqual(self.point.coordinates, ())

        with self.subTest(dim=2):
            self.assertTupleEqual(self.point2D.coordinates, (1.5, 2.5))

        with self.subTest(dim=3):
            self.assertTupleEqual(self.point3D.coordinates, (3, 4, 5))


class Test_CartesianPoint2D(unittest.TestCase):
    def setUp(self):
        self.pnt1 = CartesianPoint2D(3.09, -4)

        self.pnt2 = CartesianPoint2D(83.3, 494.82)
        self.pnt1_pnt2_distance = 505.2277075735257

    def test_eq(self):
        # Verify that equality between `CartesianPoint2D` objects functions as expected
        with self.subTest(case='same_point'):
            self.assertEqual(self.pnt1, self.pnt1)
            self.assertEqual(self.pnt2, self.pnt2)

        with self.subTest(case='different_values'):
            self.assertNotEqual(CartesianPoint2D(-1.23, 45), CartesianPoint2D(-1.24, 45))

        with self.subTest(case='different_type'):
            (point := Point())._coordinates = (1, 2)
            self.assertNotEqual(point, CartesianPoint2D(1, 2))

    def test_get_coordinates(self):
        # Verifies that point coordinates are retrieved correctly
        self.assertTupleEqual(self.pnt1.coordinates, (3.09, -4))

    def test_set_coordinates(self):
        # Verifies that "coordinates" attribute can be set correctly
        with self.subTest(type='CartesianPoint2D'):
            (pnt1 := CartesianPoint2D()).coordinates = self.pnt1
            self.assertTupleEqual(pnt1._coordinates, (3.09, -4))

        with self.subTest(type='tuple'):
            (pnt2 := CartesianPoint2D()).coordinates = (5, 6)
            self.assertTupleEqual(pnt2._coordinates, (5, 6))

        with self.subTest(type='list'):
            (pnt3 := CartesianPoint2D()).coordinates = [7.8, -9.12]
            self.assertTupleEqual(pnt3._coordinates, (7.8, -9.12))

    def test_set_coordinates_invalid(self):
        # Verifies that appropriate errors are thrown if attempting to set
        # point coordinates to an invalid value
        with self.subTest(issue='no_length_attr'):
            with self.assertRaises(ValueError):
                CartesianPoint2D().coordinates = 12.345

        with self.subTest(issue='length_not_2'):
            with self.assertRaises(ValueError):
                CartesianPoint2D().coordinates = (1, 2, 3)

        with self.subTest(issue='not_numeric'):
            with self.assertRaises(ValueError):
                CartesianPoint2D().coordinates = ('abc', 123)

    def test_initialize(self):
        # Verifies that the `CartesianPoint2D` constructor correctly initializes
        # point location using different input formats
        with self.subTest(arg='none'):
            self.assertTupleEqual(CartesianPoint2D()._coordinates, ())
            self.assertTupleEqual(CartesianPoint2D(w=2, z=4)._coordinates, ())

        with self.subTest(arg='positional'):
            with self.subTest(type='float'):
                self.assertTupleEqual(CartesianPoint2D(-1, 2.3)._coordinates, (-1.0, 2.3))

            with self.subTest(type='tuple'):
                self.assertTupleEqual(CartesianPoint2D((-1, 2.3))._coordinates, (-1.0, 2.3))

            with self.subTest(type='list'):
                self.assertTupleEqual(CartesianPoint2D([-1, 2.3])._coordinates, (-1.0, 2.3))

            with self.subTest(type='np.ndarray'):
                self.assertTupleEqual(CartesianPoint2D(np.array([-1, 2.3]))._coordinates, (-1.0, 2.3))

        with self.subTest(arg='keyword'):
            self.assertTupleEqual(CartesianPoint2D(x=-1, y=2.3)._coordinates, (-1.0, 2.3))

    def test_initialize_invalid(self):
        # Verifies that the `CartesianPoint2D` constructor throws an error if
        # provided invalid arguments
        with self.subTest(arg='positional'):
            with self.assertRaises(ValueError):
                CartesianPoint2D(1, 2, 3)

        with self.subTest(arg='keyword'):
            with self.assertRaises(TypeError):
                CartesianPoint2D(x=1)

            with self.assertRaises(TypeError):
                CartesianPoint2D(x=1, z=2)

            with self.assertRaises(TypeError):
                CartesianPoint2D(y=1)

            with self.assertRaises(TypeError):
                CartesianPoint2D(y=1, z=2)

        with self.subTest(arg='both'):
            with self.assertRaises(TypeError):
                CartesianPoint2D(0, 1, x=2, y=3)

    def test_distance_to(self):
        # Verifies that the distance between two points is calculated correctly
        with self.subTest(type='self'):
            self.assertAlmostEqual(self.pnt1.distance_to(self.pnt1), 0.0)
            self.assertAlmostEqual(self.pnt2.distance_to(self.pnt2), 0.0)

        with self.subTest(type='CartesianPoint2D'):
            self.assertAlmostEqual(self.pnt1.distance_to(self.pnt2),
                                   self.pnt1_pnt2_distance)
            self.assertAlmostEqual(self.pnt2.distance_to(self.pnt1),
                                   self.pnt1_pnt2_distance)

        with self.subTest(type='tuple'):
            self.assertAlmostEqual(self.pnt1.distance_to((83.3, 494.82)),
                                   self.pnt1_pnt2_distance)

        with self.subTest(type='list'):
            self.assertAlmostEqual(self.pnt1.distance_to([83.3, 494.82]),
                                   self.pnt1_pnt2_distance)

    def test_get_x(self):
        # Verifies that the x-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.x, 3.09)

    def test_get_y(self):
        # Verifies that the y-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.y, -4)
