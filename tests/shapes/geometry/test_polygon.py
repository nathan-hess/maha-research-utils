import copy
import unittest

import numpy as np

from mahautils.shapes import Polygon


class Test_Polygon(unittest.TestCase):
    def setUp(self) -> None:
        self.vertices = [[3, 4], [3, 6], [1.5, 6], [1, 3.5], [2, 2]]

        # Polygon with points ordered counterclockwise
        self.polygon_ccw = Polygon(self.vertices)

        # Polygon with points ordered clockwise
        self.polygon_cw = Polygon(list(reversed(self.vertices)))

    def test_set_vertices(self):
        # Verifies that polygon vertices are set correctly
        with self.subTest(repeat=False):
            self.assertTrue(np.array_equal(
                self.polygon_ccw.vertices,
                np.array([[3, 4], [3, 6], [1.5, 6], [1, 3.5], [2, 2]])
            ))

        with self.subTest(repeat=True):
            self.assertTrue(np.array_equal(
                Polygon(self.vertices + [self.vertices[0]]).vertices,
                np.array([[3, 4], [3, 6], [1.5, 6], [1, 3.5], [2, 2]])
            ))

    def test_set_vertices_invalid(self):
        # Verifies that an appropriate error is thrown if attempting to set
        # polygon vertices with an invalid input
        with self.subTest(issue='not_rectangular'):
            with self.assertRaises(ValueError):
                Polygon([1, [2, 3], [4, 5]])

        with self.subTest(issue='not_2D'):
            with self.assertRaises(ValueError):
                Polygon([[[1, 2], [3, 4]], [[2, 3], [4, 5]]])

        with self.subTest(issue='points_not_2D'):
            with self.assertRaises(ValueError):
                Polygon([[1, 2, 3], [2, 3, 4]])

    def test_is_inside(self):
        # Verifies that points inside or outside the polygon are correctly
        # identified
        points = {
            'inside': (2, 4),
            'outside': (4, 5.5),
            'boundary': (2, 2),
        }

        for direction in ('cw', 'ccw'):
            with self.subTest(direction=direction):
                polygon: Polygon = getattr(self, f'polygon_{direction}')

                with self.subTest(perimeter_is_inside=True):
                    with self.subTest(point_location='inside'):
                        self.assertTrue(polygon.is_inside(points['inside'],
                                                          perimeter_is_inside=True))

                    with self.subTest(point_location='outside'):
                        self.assertFalse(polygon.is_inside(points['outside'],
                                                           perimeter_is_inside=True))

                    with self.subTest(point_location='boundary'):
                        self.assertTrue(polygon.is_inside(points['boundary'],
                                                          perimeter_is_inside=True))

                with self.subTest(perimeter_is_inside=False):
                    with self.subTest(point_location='inside'):
                        self.assertTrue(polygon.is_inside(points['inside'],
                                                          perimeter_is_inside=False))

                    with self.subTest(point_location='outside'):
                        self.assertFalse(polygon.is_inside(points['outside'],
                                                           perimeter_is_inside=False))

                    with self.subTest(point_location='boundary'):
                        self.assertFalse(polygon.is_inside(points['boundary'],
                                                           perimeter_is_inside=False))

    def test_points(self):
        # Verify that polygon points are retrieved correctly
        with self.subTest(repeat_end=True):
            self.assertTrue(np.array_equal(
                self.polygon_ccw.points(repeat_end=True),
                np.array([[3, 4], [3, 6], [1.5, 6], [1, 3.5], [2, 2], [3, 4]])
            ))

        with self.subTest(repeat_end=False):
            self.assertTrue(np.array_equal(
                self.polygon_ccw.points(repeat_end=False),
                np.array([[3, 4], [3, 6], [1.5, 6], [1, 3.5], [2, 2]])
            ))

    def test_translate(self):
        # Verifies that polygon can be translated
        with self.subTest(direction='x'):
            polygon = copy.deepcopy(self.polygon_ccw)
            polygon.translate(x=6)
            self.assertTrue(np.array_equal(
                polygon.points(repeat_end=True),
                np.array([[9, 4], [9, 6], [7.5, 6], [7, 3.5], [8, 2], [9, 4]])
            ))

        with self.subTest(direction='y'):
            polygon = copy.deepcopy(self.polygon_ccw)
            polygon.translate(y=-3.5)
            self.assertTrue(np.array_equal(
                polygon.points(repeat_end=True),
                np.array([[3, 0.5], [3, 2.5], [1.5, 2.5], [1, 0], [2, -1.5], [3, 0.5]])
            ))

        with self.subTest(direction='x,y'):
            polygon = copy.deepcopy(self.polygon_ccw)
            polygon.translate(x=6, y=-3.5)
            self.assertTrue(np.array_equal(
                polygon.points(repeat_end=True),
                np.array([[9, 0.5], [9, 2.5], [7.5, 2.5], [7, 0], [8, -1.5], [9, 0.5]])
            ))

    def test_xy_coordinates(self):
        # Verify that polygon coordinates are retrieved correctly
        with self.subTest(repeat_end=True):
            self.assertTrue(np.array_equal(
                self.polygon_ccw.xy_coordinates(repeat_end=True),
                np.array([[3, 3, 1.5, 1, 2, 3], [4, 6, 6, 3.5, 2, 4]])
            ))

        with self.subTest(repeat_end=False):
            self.assertTrue(np.array_equal(
                self.polygon_ccw.xy_coordinates(repeat_end=False),
                np.array([[3, 3, 1.5, 1, 2], [4, 6, 6, 3.5, 2]])
            ))
