import copy
import unittest

import numpy as np

from mahautils.shapes import (
    CartesianPoint2D,
    CartesianPoint3D,
    Point,
)
from tests import max_array_diff, TEST_FLOAT_TOLERANCE


class Test_Point(unittest.TestCase):
    def setUp(self):
        self.point = Point()

        self.point2D = Point()
        self.point2D._coordinates = (1.5, 2.5)

        self.point3D = Point()
        self.point3D._coordinates = (3, 4, 5)


class Test_Point_Properties(Test_Point):
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


class Test_CartesianPoint2D_Properties(Test_CartesianPoint2D):
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

        with self.subTest(type='attributes'):
            (pnt4 := CartesianPoint2D()).coordinates = (0, 0)
            pnt4.x = 0.24
            pnt4.y = -6.1
            self.assertTupleEqual(pnt4._coordinates, (0.24, -6.1))

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

    def test_get_x(self):
        # Verifies that the x-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.x, 3.09)

    def test_get_y(self):
        # Verifies that the y-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.y, -4)

    def test_points(self):
        # Verifies that x- and y-coordinates are generated correctly
        points = self.pnt1.points()

        self.assertEqual(len(points), 1)
        self.assertTrue(np.array_equal(points[0], np.array([3.09, -4])))

    def test_xy_coordinates(self):
        # Verifies that x- and y-coordinates are generated correctly
        self.assertTupleEqual(
            self.pnt1.xy_coordinates(), (np.array(3.09), np.array(-4))
        )


class Test_CartesianPoint2D_Distance(Test_CartesianPoint2D):
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


class Test_CartesianPoint2D_Transform(Test_CartesianPoint2D):
    def test_reflect(self):
        # Verifies that a point can be reflected about an arbitrary line
        with self.subTest(line='horizontal'):
            pntA = CartesianPoint2D(-1, 4)
            pntB = CartesianPoint2D(5, 4)

            point = CartesianPoint2D(2, -21)
            point.reflect(pntA=pntA, pntB=pntB)

            self.assertEqual(point, CartesianPoint2D(2, 29))

        with self.subTest(line='vertical'):
            pntA = CartesianPoint2D(-1, 4)
            pntB = CartesianPoint2D(-1, 9)

            point = CartesianPoint2D(2, -21)
            point.reflect(pntA=pntA, pntB=pntB)

            self.assertEqual(point, CartesianPoint2D(-4, -21))

        with self.subTest(line='angled'):
            pntA = CartesianPoint2D(0, 0)
            pntB = CartesianPoint2D(4, 3)

            point = CartesianPoint2D(1, 7)
            point.reflect(pntA=pntA, pntB=pntB)

            self.assertEqual(point, CartesianPoint2D(7, -1))

        with self.subTest(line='on_line'):
            pntA = CartesianPoint2D(-1, 4)
            pntB = CartesianPoint2D(5, 4)

            point = CartesianPoint2D(2, 4)
            point.reflect(pntA=pntA, pntB=pntB)

            self.assertEqual(point, CartesianPoint2D(2, 4))

        with self.subTest(line='tuple'):
            pntA = (-1, 4)
            pntB = (5, 4)

            point = CartesianPoint2D(2, -21)
            point.reflect(pntA=pntA, pntB=pntB)

            self.assertEqual(point, CartesianPoint2D(2, 29))

    def test_reflect_x(self):
        # Verifies that a point can be reflected about the x-axis
        point = CartesianPoint2D(2, -21)
        point.reflect_x()

        self.assertEqual(point, CartesianPoint2D(2, 21))

    def test_reflect_y(self):
        # Verifies that a point can be reflected about the y-axis
        point = CartesianPoint2D(2, -21)
        point.reflect_y()

        self.assertEqual(point, CartesianPoint2D(-2, -21))

    def test_reflect_invalid(self):
        # Verifies that an exception is thrown if attempting to specify a
        # line with one point
        pntA = CartesianPoint2D(-1, 4)
        pntB = CartesianPoint2D(-1, 4)

        point = CartesianPoint2D(2, -21)

        with self.assertRaises(ValueError):
            point.reflect(pntA=pntA, pntB=pntB)

    def test_rotate(self):
        # Verifies that a point can be rotated about another point
        with self.subTest(center=(0, 0)):
            with self.subTest(angle=90):
                point = CartesianPoint2D(2, 0)
                point.rotate(center=(0, 0), angle=90, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(point, CartesianPoint2D(0, 2)),
                    TEST_FLOAT_TOLERANCE,
                )

            with self.subTest(angle=-120):
                point = CartesianPoint2D(2, 0)
                point.rotate(center=(0, 0), angle=-120, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(point, CartesianPoint2D(-1, -3**0.5)),
                    TEST_FLOAT_TOLERANCE,
                )

        with self.subTest(center=(5, 0)):
            with self.subTest(angle=90):
                point = CartesianPoint2D(2, 0)
                point.rotate(center=(5, 0), angle=90, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(point, CartesianPoint2D(5, -3)),
                    TEST_FLOAT_TOLERANCE,
                )

            with self.subTest(angle=-120):
                point = CartesianPoint2D(2, 0)
                point.rotate(center=(5, 0), angle=-120, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(point, CartesianPoint2D(6.5, 1.5*3**0.5)),
                    TEST_FLOAT_TOLERANCE,
                )

    def test_translate(self):
        # Verifies that point can be translated
        with self.subTest(direction='x'):
            point = CartesianPoint2D(1.2, 3.5)
            point.translate(x=6)
            self.assertEqual(point, CartesianPoint2D(7.2, 3.5))

        with self.subTest(direction='y'):
            point = CartesianPoint2D(1.2, 3.5)
            point.translate(y=-3.5)
            self.assertEqual(point, CartesianPoint2D(1.2, 0))

        with self.subTest(direction='x,y'):
            point = CartesianPoint2D(1.2, 3.5)
            point.translate(x=6, y=-3.5)
            self.assertEqual(point, CartesianPoint2D(7.2, 0))


class Test_CartesianPoint3D(unittest.TestCase):
    def setUp(self):
        self.pnt1 = CartesianPoint3D(3.09, -4, 9.5)

        self.pnt2 = CartesianPoint3D(83.3, 494.82, 449.5)
        self.pnt1_pnt2_distance = 669.9664443089669


class Test_CartesianPoint3D_Properties(Test_CartesianPoint3D):
    def test_eq(self):
        # Verify that equality between `CartesianPoint3D` objects functions as expected
        with self.subTest(case='same_point'):
            self.assertEqual(self.pnt1, self.pnt1)
            self.assertEqual(self.pnt2, self.pnt2)

        with self.subTest(case='different_values'):
            self.assertNotEqual(CartesianPoint3D(-1.23, 45, 6), CartesianPoint3D(-1.24, 45, 6))

        with self.subTest(case='different_type'):
            (point := Point())._coordinates = (1, 2, 3)
            self.assertNotEqual(point, CartesianPoint3D(1, 2, 3))

    def test_get_coordinates(self):
        # Verifies that point coordinates are retrieved correctly
        self.assertTupleEqual(self.pnt1.coordinates, (3.09, -4, 9.5))

    def test_set_coordinates(self):
        # Verifies that "coordinates" attribute can be set correctly
        with self.subTest(type='CartesianPoint3D'):
            (pnt1 := CartesianPoint3D()).coordinates = self.pnt1
            self.assertTupleEqual(pnt1._coordinates, (3.09, -4, 9.5))

        with self.subTest(type='tuple'):
            (pnt2 := CartesianPoint3D()).coordinates = (5, 6, 7)
            self.assertTupleEqual(pnt2._coordinates, (5, 6, 7))

        with self.subTest(type='list'):
            (pnt3 := CartesianPoint3D()).coordinates = [7.8, -9.12, 13.14]
            self.assertTupleEqual(pnt3._coordinates, (7.8, -9.12, 13.14))

        with self.subTest(type='attributes'):
            (pnt4 := CartesianPoint3D()).coordinates = (0, 0, 0)
            pnt4.x = 0.24
            pnt4.y = -6.1
            pnt4.z = 5.2
            self.assertTupleEqual(pnt4._coordinates, (0.24, -6.1, 5.2))

    def test_set_coordinates_invalid(self):
        # Verifies that appropriate errors are thrown if attempting to set
        # point coordinates to an invalid value
        with self.subTest(issue='no_length_attr'):
            with self.assertRaises(ValueError):
                CartesianPoint3D().coordinates = 12.345

        with self.subTest(issue='length_not_3'):
            with self.assertRaises(ValueError):
                CartesianPoint3D().coordinates = (1, 2)

        with self.subTest(issue='not_numeric'):
            with self.assertRaises(ValueError):
                CartesianPoint3D().coordinates = ('abc', 123, 456)

    def test_initialize(self):
        # Verifies that the `CartesianPoint3D` constructor correctly initializes
        # point location using different input formats
        with self.subTest(arg='none'):
            self.assertTupleEqual(CartesianPoint3D()._coordinates, ())
            self.assertTupleEqual(CartesianPoint3D(w=2, v=4)._coordinates, ())

        with self.subTest(arg='positional'):
            with self.subTest(type='float'):
                self.assertTupleEqual(CartesianPoint3D(-1, 2.3, 4)._coordinates, (-1.0, 2.3, 4))

            with self.subTest(type='tuple'):
                self.assertTupleEqual(CartesianPoint3D((-1, 2.3, 4))._coordinates, (-1.0, 2.3, 4))

            with self.subTest(type='list'):
                self.assertTupleEqual(CartesianPoint3D([-1, 2.3, 4])._coordinates, (-1.0, 2.3, 4))

            with self.subTest(type='np.ndarray'):
                self.assertTupleEqual(CartesianPoint3D(np.array([-1, 2.3, 4]))._coordinates, (-1.0, 2.3, 4))

        with self.subTest(arg='keyword'):
            self.assertTupleEqual(CartesianPoint3D(x=-1, y=2.3, z=4)._coordinates, (-1.0, 2.3, 4))

    def test_initialize_invalid(self):
        # Verifies that the `CartesianPoint3D` constructor throws an error if
        # provided invalid arguments
        with self.subTest(arg='positional'):
            with self.assertRaises(ValueError):
                CartesianPoint3D(1, 2, 3, 4)

            with self.assertRaises(ValueError):
                CartesianPoint3D(1, 2)

        with self.subTest(arg='keyword'):
            with self.assertRaises(TypeError):
                CartesianPoint3D(x=1)

            with self.assertRaises(TypeError):
                CartesianPoint3D(x=1, z=2)

            with self.assertRaises(TypeError):
                CartesianPoint3D(y=1)

            with self.assertRaises(TypeError):
                CartesianPoint3D(y=1, z=2)

        with self.subTest(arg='both'):
            with self.assertRaises(TypeError):
                CartesianPoint3D(0, 1, 2, x=3, y=4, z=5)

    def test_get_x(self):
        # Verifies that the x-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.x, 3.09)

    def test_get_y(self):
        # Verifies that the y-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.y, -4)

    def test_get_z(self):
        # Verifies that the z-coordinate of a point is retrieved correctly
        self.assertEqual(self.pnt1.z, 9.5)


class Test_CartesianPoint3D_Distance(Test_CartesianPoint3D):
    def test_distance_to(self):
        # Verifies that the distance between two points is calculated correctly
        with self.subTest(type='self'):
            self.assertAlmostEqual(self.pnt1.distance_to(self.pnt1), 0.0)
            self.assertAlmostEqual(self.pnt2.distance_to(self.pnt2), 0.0)

        with self.subTest(type='CartesianPoint3D'):
            self.assertAlmostEqual(self.pnt1.distance_to(self.pnt2),
                                   self.pnt1_pnt2_distance)
            self.assertAlmostEqual(self.pnt2.distance_to(self.pnt1),
                                   self.pnt1_pnt2_distance)

        with self.subTest(type='tuple'):
            self.assertAlmostEqual(self.pnt1.distance_to((83.3, 494.82, 449.5)),
                                   self.pnt1_pnt2_distance)

        with self.subTest(type='list'):
            self.assertAlmostEqual(self.pnt1.distance_to([83.3, 494.82, 449.5]),
                                   self.pnt1_pnt2_distance)
