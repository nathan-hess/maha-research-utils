import unittest
from unittest.mock import Mock

import numpy as np

from mahautils.shapes import (
    ClosedShape2D,
    OpenShape2D,
    Shape2D,
)


class Test_Shape(unittest.TestCase):
    def test_set_construction(self):
        # Verifies that "construction" attribute is set correctly
        with self.subTest(method='constructor'):
            shape = Shape2D(is_closed=True, construction=True)
            self.assertTrue(shape._construction)

        with self.subTest(method='attribute'):
            shape.construction = False
            self.assertFalse(shape._construction)

    def test_get_construction(self):
        # Verifies that "construction" attribute can be retrieved correctly
        shape = Shape2D(is_closed=True)

        shape._construction = True
        self.assertTrue(shape.construction)

        shape._construction = False
        self.assertFalse(shape.construction)

    def test_set_construction_invalid(self):
        # Verifies that an error is thrown if attempting to set the
        # "construction" attribute to an invalid value
        shape = Shape2D(is_closed=True)

        with self.assertRaises(TypeError):
            shape.construction = 1

    def test_set_is_closed(self):
        # Verifies that the "is_closed" attribute is set correctly
        with self.subTest(type=bool):
            self.assertTrue(Shape2D(is_closed=True)._is_closed)
            self.assertFalse(Shape2D(is_closed=False)._is_closed)

        with self.subTest(type=int):
            self.assertTrue(Shape2D(is_closed=1)._is_closed)
            self.assertFalse(Shape2D(is_closed=0)._is_closed)

        with self.subTest(type='error'):
            with self.assertRaises(AttributeError):
                Shape2D(is_closed=True).is_closed = False

    def test_get_is_closed(self):
        # Verifies that the "is_closed" attribute is retrieved correctly
        shape = Shape2D(is_closed=True)

        shape._is_closed = True
        self.assertTrue(shape.is_closed)

        shape._is_closed = False
        self.assertFalse(shape.is_closed)

    def test_set_default_num_coordinates(self):
        # Verifies that "default_num_coordinates" correctly stores the default
        # number of coordinates with which to plot shapes
        with self.subTest(method='initialize'):
            self.assertIsNone(Shape2D(is_closed=True)._default_num_coordinates)

        with self.subTest(method='constructor'):
            self.assertEqual(
                Shape2D(is_closed=True, default_num_coordinates=30)._default_num_coordinates,
                30)

        with self.subTest(method='attribute'):
            shape = Shape2D(is_closed=True)
            shape.default_num_coordinates = 2
            self.assertEqual(shape._default_num_coordinates, 2)

    def test_unset_default_num_coordinates(self):
        # Verifies that the "default_num_coordinates" attribute can be set to empty
        shape = Shape2D(is_closed=True, default_num_coordinates=30)
        shape.default_num_coordinates = None
        self.assertIsNone(shape._default_num_coordinates)

    def test_set_default_num_coordinates_invalid(self):
        # Verifies that the expected error is thrown if attempting to set
        # "default_num_coordinates" to an invalid value
        shape = Shape2D(is_closed=True)

        with self.subTest(issue='invalid_type'):
            with self.assertRaises(ValueError):
                shape.default_num_coordinates = 'abcdefg'

        with self.subTest(issue='float'):
            with self.assertRaises(ValueError):
                shape.default_num_coordinates = 3.14

        with self.subTest(issue='negative'):
            with self.assertRaises(ValueError):
                shape.default_num_coordinates = -3

    def test_get_default_num_coordinates(self):
        # Verifies that the "default_num_coordinates" attribute is
        # retrieved correctly
        shape = Shape2D(is_closed=True)

        shape._default_num_coordinates = 5000
        self.assertEqual(shape.default_num_coordinates, 5000)

    def test_get_num_coordinates(self):
        # Verifies that precedence is respected when retrieving the number of
        # coordinates with which to plot shapes
        with self.subTest(arg=True, attr=True):
            shape = Shape2D(is_closed=True, default_num_coordinates=100)
            self.assertEqual(shape._get_num_coordinates(200), 200)

        with self.subTest(arg=True, attr=False):
            shape = Shape2D(is_closed=True)
            self.assertEqual(shape._get_num_coordinates(200), 200)

        with self.subTest(arg=False, attr=True):
            shape = Shape2D(is_closed=True, default_num_coordinates=100)
            self.assertEqual(shape._get_num_coordinates(), 100)

        with self.subTest(arg=False, attr=False):
            shape = Shape2D(is_closed=True)
            with self.assertRaises(ValueError):
                shape._get_num_coordinates()

    def test_convert_points(self):
        # Verifies that the "xy_coordinates()" output can be correctly
        # converted to a list of points
        shape = Shape2D(is_closed=True)
        shape.xy_coordinates = Mock(
            return_value=(np.array([1, 2, 3,   4.5, -6.7]),
                          np.array([9, 0, 8.1, 0.6, 7]))
        )

        points = shape._convert_xy_coordinates_to_points()
        shape.xy_coordinates.assert_called_once()

        self.assertTrue(isinstance(points, tuple))

        points_actual = (np.array([1, 9]), np.array([2, 0]), np.array([3, 8.1]),
                         np.array([4.5, 0.6]), np.array([-6.7, 7]))
        for i, point in enumerate(points):
            self.assertTrue(np.array_equal(point, points_actual[i]))


class Test_ClosedShape(unittest.TestCase):
    def test_initialize(self):
        self.assertTrue(ClosedShape2D().is_closed)


class Test_OpenShape(unittest.TestCase):
    def test_initialize(self):
        self.assertFalse(OpenShape2D().is_closed)
