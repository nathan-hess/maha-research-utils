import copy
import math
import unittest

import numpy as np

from mahautils.shapes import (
    CartesianPoint2D,
    Circle,
)
from tests import max_array_diff, TEST_FLOAT_TOLERANCE


class Test_Circle(unittest.TestCase):
    def setUp(self):
        self.circle_center = CartesianPoint2D(1.2, 3.5)
        self.circle_radius = 5

        self.circle = Circle(
            center=self.circle_center,
            radius=self.circle_radius
        )

    def test_eq(self):
        # Verifies that equality between `Circle` objects is assessed correctly
        with self.subTest(case='same_object'):
            self.assertEqual(self.circle, self.circle)

        with self.subTest(case='equal_circles'):
            self.assertEqual(
                Circle(center=(0, 1), radius=2),
                Circle(center=(0, 1), diameter=4))

        with self.subTest(case='different_type'):
            self.assertNotEqual(self.circle, (0, 1))

        with self.subTest(case='different_center'):
            self.assertNotEqual(
                Circle(center=(0, -1), radius=2),
                Circle(center=(0, 1), diameter=4))

        with self.subTest(case='different_radius'):
            self.assertNotEqual(
                Circle(center=(0, 1), radius=2),
                Circle(center=(0, 1), diameter=4.5))

        with self.subTest(cause='different_units'):
            circle_units = copy.deepcopy(self.circle)
            circle_units.units = 'm'

            self.assertNotEqual(self.circle, circle_units)

    def test_repr(self):
        # Verifies that printable string representation of `Circle` objects is
        # generated correctly
        self.assertEqual(
            self.circle.__repr__(),
            "<class 'mahautils.shapes.geometry.circle.Circle'> center=(1.2, 3.5), radius=5.0"
        )

    def test_str(self):
        # Verifies that printable string representation of `Circle` objects is
        # generated correctly
        self.assertEqual(
            str(self.circle),
            "<class 'mahautils.shapes.geometry.circle.Circle'> center=(1.2, 3.5), radius=5.0"
        )

    def test_area(self):
        # Verifies that the circle area is calculated correctly
        self.assertAlmostEqual(self.circle.area, 78.53981633974483)

    def test_set_center(self):
        # Verifies that circle center point can be set correctly
        with self.subTest(method='constructor'):
            self.assertEqual(self.circle._center, self.circle_center)

        with self.subTest(method='attribute'):
            self.circle.center = (0.67, -8.9)
            self.assertEqual(self.circle._center, CartesianPoint2D(0.67, -8.9))

    def test_get_center(self):
        # Verifies that circle center point can be retrieved correctly
        self.assertEqual(self.circle.center, self.circle_center)

    def test_set_radius(self):
        # Verifies that circle radius can be set correctly
        with self.subTest(metric='radius'):
            with self.subTest(method='constructor'):
                self.assertEqual(self.circle._radius, self.circle_radius)

            with self.subTest(method='attribute'):
                self.circle.radius = 9
                self.assertEqual(self.circle._radius, 9)

        with self.subTest(metric='diameter'):
            with self.subTest(method='constructor'):
                circle = Circle(center=(0, 0), diameter=12)
                self.assertEqual(circle._radius, 6)

            with self.subTest(method='attribute'):
                circle.diameter = 14
                self.assertEqual(circle._radius, 7)

    def test_set_radius_invalid(self):
        # Verifies that an appropriate error is thrown if attempting to set
        # circle radius to an invalid value
        with self.subTest(issue='type'):
            with self.assertRaises(ValueError):
                self.circle.radius = 'abc'

        with self.subTest(issue='negative'):
            with self.assertRaises(ValueError):
                self.circle.radius = -1e-15

        with self.subTest(issue='duplicate_argument'):
            with self.assertRaises(TypeError):
                Circle(center=(1,2), radius=3, diameter=6)

    def test_get_radius(self):
        # Verifies that circle radius can be retrieved correctly
        with self.subTest(metric='radius'):
            self.assertEqual(self.circle.radius, self.circle_radius)

        with self.subTest(metric='diameter'):
            self.assertEqual(self.circle.diameter, 2*self.circle_radius)

    def test_intersection_area(self):
        # Verifies that the intersection area of two circles is calculated correctly
        r = 68.25331284
        dx = 673
        dy = 3.2
        circle1 = Circle(center=(dx, r + dy), radius=r)
        circle2 = Circle(center=(r + dx, dy), radius=r)

        analytical_area = r**2 * 0.25 * (2*math.pi - 4)
        self.assertAlmostEqual(circle1.intersection_area(circle2), analytical_area)
        self.assertAlmostEqual(circle2.intersection_area(circle1), analytical_area)

    def test_intersection_area_zero(self):
        # Verifies that the intersection area of two circles is calculated correctly
        circle1 = Circle(center=(0, 0), radius=5)
        circle2 = Circle(center=(0, 50), radius=5)
        circle3 = Circle(center=(0, -10), radius=5)

        self.assertEqual(circle1.intersection_area(circle2), 0)
        self.assertEqual(circle2.intersection_area(circle1), 0)

        self.assertEqual(circle1.intersection_area(circle3), 0)
        self.assertEqual(circle3.intersection_area(circle1), 0)

    def test_intersection_area_contained(self):
        # Verifies that the intersection area of two circles is calculated correctly
        circle1 = Circle(center=(0.5, 6.7), radius=50)
        circle2 = Circle(center=(5, 6.7), radius=5)

        self.assertEqual(circle1.intersection_area(circle2), circle2.area)
        self.assertEqual(circle2.intersection_area(circle1), circle2.area)

    def test_intersection_area_invalid_units(self):
        # Verifies that an exception is thrown if attempting to find the area of
        # intersection of two circles with different units
        circle1 = Circle(center=(0, 0), radius=5, units='mm')
        circle2 = Circle(center=(0, 50), radius=5)

        with self.assertRaises(ValueError):
            circle1.intersection_area(circle2)

    def test_intersection_area_invalid_shape(self):
        # Verifies that an exception is thrown if attempting to find the area of
        # intersection of a circle and a shape that isn't a circle
        circle1 = Circle(center=(0, 0), radius=5, units='mm')
        shape2 = CartesianPoint2D(0, 0)

        with self.assertRaises(TypeError):
            circle1.intersection_area(shape2)

    def test_is_inside(self):
        # Verifies that points can be correctly identified as inside or
        # outside the circle

        # First value: point to check
        # Second value: expected output if `perimeter_is_inside` is `True`
        #   (first element of tuple) or `False` (second element of tuple)
        test_cases = (
            (( 1.2,  3.5), (True,  True)),
            (( 3.6, -0.8), (True,  True)),
            (( 6.2,  3.5), (True,  False)),
            ((-3.8,  3.5), (True,  False)),
            (( 1.2,  8.5), (True,  False)),
            (( 1.2, -1.5), (True,  False)),
            ((  15,  -30), (False, False)),
        )

        for point, expected_values in test_cases:
            with self.subTest(point=point):
                for i, arg in enumerate((True, False)):
                    with self.subTest(perimeter_is_inside=arg):
                        self.assertIs(
                            self.circle.is_inside(
                                point=point,
                                perimeter_is_inside=arg),
                            expected_values[i]
                        )

    def test_points(self):
        # Verifies that points on circle circumference can be generated correctly
        test_cases = ((5, True), (4, False))

        expected_points = (
            np.array((6.2, 3.5)),
            np.array((1.2, 8.5)),
            np.array((-3.8, 3.5)),
            np.array((1.2, -1.5)),
            np.array((6.2, 3.5)),
        )

        for num_coordinates, repeat_end in test_cases:
            with self.subTest(num_coordinates=num_coordinates, repeat_end=repeat_end):
                points = self.circle.points(repeat_end=repeat_end,
                                            num_coordinates=num_coordinates)

                self.assertEqual(len(points), num_coordinates)

                for i in range(num_coordinates):
                    self.assertTrue(np.allclose(points[i], expected_points[i]))

    def test_reflect(self):
        # Verifies that a circle can be reflected about an arbitrary line
        pntA = CartesianPoint2D(6, 0)
        pntB = CartesianPoint2D(6, 3)

        self.circle.reflect(pntA=pntA, pntB=pntB)

        with self.subTest(quantity='position'):
            self.assertLessEqual(
                self.circle.center.distance_to(CartesianPoint2D(10.8, 3.5)),
                TEST_FLOAT_TOLERANCE,
            )

        with self.subTest(quantity='radius'):
            self.assertEqual(self.circle.radius, self.circle_radius)

    def test_rotate(self):
        # Verifies that circle can be rotated about a point
        with self.subTest(center=(0, 0)):
            with self.subTest(angle=90):
                circle = Circle(center=(2, 0), radius=1)
                circle.rotate(center=(0, 0), angle=90, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(circle.center, CartesianPoint2D(0, 2)),
                    TEST_FLOAT_TOLERANCE,
                )

            with self.subTest(angle=-120):
                circle = Circle(center=(2, 0), radius=1)
                circle.rotate(center=(0, 0), angle=-120, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(circle.center, CartesianPoint2D(-1, -3**0.5)),
                    TEST_FLOAT_TOLERANCE,
                )

        with self.subTest(center=(5, 0)):
            with self.subTest(angle=90):
                circle = Circle(center=(2, 0), radius=1)
                circle.rotate(center=(5, 0), angle=90, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(circle.center, CartesianPoint2D(5, -3)),
                    TEST_FLOAT_TOLERANCE,
                )

            with self.subTest(angle=-120):
                circle = Circle(center=(2, 0), radius=1)
                circle.rotate(center=(5, 0), angle=-120, angle_units='deg')
                self.assertLessEqual(
                    max_array_diff(circle.center, CartesianPoint2D(6.5, 1.5*3**0.5)),
                    TEST_FLOAT_TOLERANCE,
                )

    def test_translate(self):
        # Verifies that circle can be translated
        self.assertEqual(self.circle.center, CartesianPoint2D(1.2, 3.5))

        with self.subTest(direction='x'):
            circle = copy.deepcopy(self.circle)
            circle.translate(x=6)
            self.assertEqual(circle.center, CartesianPoint2D(7.2, 3.5))

        with self.subTest(direction='y'):
            circle = copy.deepcopy(self.circle)
            circle.translate(y=-3.5)
            self.assertEqual(circle.center, CartesianPoint2D(1.2, 0))

        with self.subTest(direction='x,y'):
            circle = copy.deepcopy(self.circle)
            circle.translate(x=6, y=-3.5)
            self.assertEqual(circle.center, CartesianPoint2D(7.2, 0))

    def test_xy_coordinates(self):
        # Verifies that x- and y-coordinates of circle circumference can be
        # generated correctly
        with self.subTest(num_coordinates=5, repeat_end=True):
            coordinates = self.circle.xy_coordinates(repeat_end=True,
                                                     num_coordinates=5)

            self.assertEqual(len(coordinates), 2)

            self.assertTrue(np.allclose(coordinates[0],
                                        np.array([6.2, 1.2, -3.8, 1.2, 6.2])))
            self.assertTrue(np.allclose(coordinates[1],
                                        np.array([3.5, 8.5, 3.5, -1.5, 3.5])))

        with self.subTest(num_coordinates=4, repeat_end=False):
            coordinates = self.circle.xy_coordinates(repeat_end=False,
                                                     num_coordinates=4)

            self.assertEqual(len(coordinates), 2)

            self.assertTrue(np.allclose(coordinates[0],
                                        np.array([6.2, 1.2, -3.8, 1.2])))
            self.assertTrue(np.allclose(coordinates[1],
                                        np.array([3.5, 8.5, 3.5, -1.5])))
