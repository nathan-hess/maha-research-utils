import unittest

from mahautils.multics import PolygonFile
from mahautils.multics.exceptions import (
    PolygonFileFormatError,
    PolygonFileMissingDataError,
)
from mahautils.shapes import Layer, Polygon
from tests import max_array_diff, SAMPLE_FILES_DIR, TEST_FLOAT_TOLERANCE


class Test_PolygonFile(unittest.TestCase):
    def setUp(self) -> None:
        self.polygon_file_blank = PolygonFile()

        self.polygon_file_001_p1_t1 = PolygonFile(SAMPLE_FILES_DIR / 'polygon_file_001.txt')
        self.polygon_file_002_p2_t1 = PolygonFile(SAMPLE_FILES_DIR / 'polygon_file_002.txt')
        self.polygon_file_003_p1_t3 = PolygonFile(SAMPLE_FILES_DIR / 'polygon_file_003.txt')
        self.polygon_file_004_p2_t3 = PolygonFile(SAMPLE_FILES_DIR / 'polygon_file_004.txt')


class Test_PolygonFile_Properties(Test_PolygonFile):
    def test_num_time_steps(self):
        # Verifies that number of time steps in polygon files are computed correctly
        with self.subTest(file='blank'):
            self.assertEqual(self.polygon_file_blank.num_time_steps, 0)

        with self.subTest(file='polygon_file_001.txt'):
            self.assertEqual(self.polygon_file_001_p1_t1.num_time_steps, 1)

        with self.subTest(file='polygon_file_002.txt'):
            self.assertEqual(self.polygon_file_002_p2_t1.num_time_steps, 1)

        with self.subTest(file='polygon_file_003.txt'):
            self.assertEqual(self.polygon_file_003_p1_t3.num_time_steps, 3)

        with self.subTest(file='polygon_file_004.txt'):
            self.assertEqual(self.polygon_file_004_p2_t3.num_time_steps, 3)

    def test_polygon_data_read_only(self):
        # Verifies that "polygon_data" property can always be read
        with self.subTest(action='read'):
            polygon_data = self.polygon_file_blank.polygon_data(writable=False)
            self.assertDictEqual(polygon_data, {})

        with self.subTest(action='write'):
            polygon_data[50] = Layer()
            self.assertDictEqual(self.polygon_file_blank._polygon_data, {})

    def test_polygon_data_write(self):
        # Verifies that "polygon_data" property is only accessible to write
        # operations if required attributes are set
        with self.subTest(action='read', accessible=False):
            with self.assertRaises(PolygonFileMissingDataError):
                self.polygon_file_blank.polygon_data(writable=True)

        with self.subTest(action='read', accessible=True):
            self.polygon_file_blank.polygon_merge_method = 0
            self.polygon_file_blank.time_extrap_method = 0
            self.polygon_file_blank.time_units = 's'

            polygon_data = self.polygon_file_blank.polygon_data(writable=True)
            self.assertDictEqual(polygon_data, {})

        with self.subTest(operation='write'):
            self.assertEqual(len(self.polygon_file_blank._polygon_data), 0)
            polygon_data[50] = Layer()
            self.assertEqual(len(self.polygon_file_blank._polygon_data), 1)
            polygon_data[50.5] = Layer()
            self.assertEqual(len(self.polygon_file_blank._polygon_data), 2)

    def test_polygon_merge_method(self):
        # Verifies that "polygon_merge_method" property can be set and
        # retrieved correctly and that inputs are validated
        with self.subTest(action='get'):
            with self.assertRaises(PolygonFileMissingDataError):
                self.polygon_file_blank.polygon_merge_method

        for value in (0, 1, 2):
            with self.subTest(valid=True, value=value):
                self.polygon_file_blank.polygon_merge_method = value
                self.assertEqual(self.polygon_file_blank.polygon_merge_method, value)

        for value in (-1, 0.1, 3, 10):
            with self.subTest(valid=False, value=value):
                with self.assertRaises(ValueError):
                    self.polygon_file_blank.polygon_merge_method = value

    def test_time_extrap_method(self):
        # Verifies that "time_extrap_method" property can be set and
        # retrieved correctly and that inputs are validated
        with self.subTest(action='get'):
            with self.assertRaises(PolygonFileMissingDataError):
                self.polygon_file_blank.time_extrap_method

        for value in (0, 2, 3):
            with self.subTest(valid=True, value=value):
                self.polygon_file_blank.time_extrap_method = value
                self.assertEqual(self.polygon_file_blank.time_extrap_method, value)

        for value in (-1, 0.1, 1, 10):
            with self.subTest(valid=False, value=value):
                with self.assertRaises(ValueError):
                    self.polygon_file_blank.time_extrap_method = value

    def test_time_units(self):
        # Verifies that "time_units" property can be set and
        # retrieved correctly and that inputs are validated
        with self.subTest(action='get'):
            with self.assertRaises(PolygonFileMissingDataError):
                self.polygon_file_blank.time_units

        with self.subTest(valid=True):
            self.polygon_file_blank.time_units = 'ms'
            self.assertEqual(self.polygon_file_blank.time_units, 'ms')

        with self.subTest(valid=False):
            with self.assertRaises(ValueError):
                self.polygon_file_blank.time_units = 'nonexistentUnit'

    def test_time_values(self):
        # Verifies that a list of all time values in the polygon file can be
        # correctly retrieved
        with self.subTest(file='blank'):
            self.assertListEqual(self.polygon_file_blank.time_values, [])

        with self.subTest(file='polygon_file_001.txt'):
            self.assertListEqual(self.polygon_file_001_p1_t1.time_values, [0])

        with self.subTest(file='polygon_file_002.txt'):
            self.assertListEqual(self.polygon_file_002_p2_t1.time_values, [0])

        with self.subTest(file='polygon_file_003.txt'):
            self.assertListEqual(self.polygon_file_003_p1_t3.time_values, [0, 1, 2])

        with self.subTest(file='polygon_file_004.txt'):
            self.assertListEqual(self.polygon_file_004_p2_t3.time_values, [0, 1, 2])


class Test_PolygonFile_Parse(Test_PolygonFile):
    def test_parse_p1_t1(self):
        # Verifies that a polygon file with a single polygon and single time
        # step is parsed correctly
        layer = self.polygon_file_001_p1_t1.polygon_data()[0]
        self.assertEqual(len(layer), 1)
        polygon: Polygon = layer[0]

        with self.subTest(quantity='enclosed_conv'):
            self.assertEqual(polygon.polygon_file_enclosed_conv, 1)

        with self.subTest(quantity='vertices'):
            self.assertLessEqual(
                max_array_diff(
                    polygon.vertices,
                    ((1, 0), (5, 0), (5, 2.5), (1, 2.5))
                ),
                TEST_FLOAT_TOLERANCE
            )

    def test_parse_p2_t3(self):
        # Verifies that a polygon file with multiple polygons and multiple time
        # steps is parsed correctly
        layers = list(self.polygon_file_004_p2_t3.polygon_data().values())
        self.assertEqual(len(layers), 3)

        with self.subTest(t=0):
            layer = layers[0]

            with self.subTest(quantity='num_polygons'):
                self.assertEqual(len(layer), 2)

            polygon1: Polygon = layer[0]
            polygon2: Polygon = layer[1]

            with self.subTest(quantity='enclosed_conv'):
                self.assertEqual(polygon1.polygon_file_enclosed_conv, 1)
                self.assertEqual(polygon2.polygon_file_enclosed_conv, 0)

            with self.subTest(quantity='vertices'):
                self.assertLessEqual(
                    max_array_diff(
                        polygon1.vertices,
                        ((1, 1), (3, 1), (3, 2), (1, 2))
                    ),
                    TEST_FLOAT_TOLERANCE)

                self.assertLessEqual(
                    max_array_diff(
                        polygon2.vertices,
                        ((1, 1), (2, 1), (1, 2))
                    ),
                    TEST_FLOAT_TOLERANCE)

        with self.subTest(t=1):
            layer = layers[1]

            with self.subTest(quantity='num_polygons'):
                self.assertEqual(len(layer), 2)

            polygon1: Polygon = layer[0]
            polygon2: Polygon = layer[1]

            with self.subTest(quantity='enclosed_conv'):
                self.assertEqual(polygon1.polygon_file_enclosed_conv, 0)
                self.assertEqual(polygon2.polygon_file_enclosed_conv, 0)

            with self.subTest(quantity='vertices'):
                self.assertLessEqual(
                    max_array_diff(
                        polygon1.vertices,
                        ((2, 1), (4, 1), (4, 2), (2, 2))
                    ),
                    TEST_FLOAT_TOLERANCE)

                self.assertLessEqual(
                    max_array_diff(
                        polygon2.vertices,
                        ((1, 2), (2, 2), (1, 3))
                    ),
                    TEST_FLOAT_TOLERANCE)

        with self.subTest(t=2):
            layer = layers[2]

            with self.subTest(quantity='num_polygons'):
                self.assertEqual(len(layer), 2)

            polygon1: Polygon = layer[0]
            polygon2: Polygon = layer[1]

            with self.subTest(quantity='enclosed_conv'):
                self.assertEqual(polygon1.polygon_file_enclosed_conv, 1)
                self.assertEqual(polygon2.polygon_file_enclosed_conv, 1)

            with self.subTest(quantity='vertices'):
                self.assertLessEqual(
                    max_array_diff(
                        polygon1.vertices,
                        ((3, 1), (5, 1), (5, 2), (3, 2))
                    ),
                    TEST_FLOAT_TOLERANCE)

                self.assertLessEqual(
                    max_array_diff(
                        polygon2.vertices,
                        ((1, 3), (2, 3), (1, 4))
                    ),
                    TEST_FLOAT_TOLERANCE)

    def test_non_integer(self):
        # Verifies that an error is thrown if values that must be an integer
        # are not an integer
        x_original = [2, 1, 0, 0, 4]

        for i in range(len(x_original)):
            with self.subTest(i=i):
                x = x_original.copy()
                x[i] += 0.1

                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'{x[0]} {x[1]} {x[2]}',
                    f'ms: 0 1 {x[3]}',
                    f'{x[4]} 1',
                    f'cm: 1  3  3  1',
                    f'cm: 1  1  2  2',
                    f'4 1',
                    f'cm: 2  4  4  2',
                    f'cm: 1  1  2  2',
                ])

                with self.assertRaises(PolygonFileFormatError):
                    self.polygon_file_blank.parse()

    def test_not_number(self):
        # Verifies that an error is thrown if values that must be a number
        # are not numbers
        x_original = [0, 1, 3, 2]

        for i in range(len(x_original)):
            with self.subTest(i=i):
                x = x_original.copy()
                x[i] = 'ee'

                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'2 1 0',
                    f'ms: {x[0]} {x[1]} 0',
                    f'4 1',
                    f'cm: 1  {x[2]}  3  1',
                    f'cm: 1  1  {x[3]}  2',
                    f'4 1',
                    f'cm: 2  4  4  2',
                    f'cm: 1  1  2  2',
                ])

                with self.assertRaises(PolygonFileFormatError):
                    self.polygon_file_blank.parse()

    def test_missing_data(self):
        # Verifies that an error is thrown if required values are not present
        x_original = [0, 0, 4]

        for i in range(len(x_original)):
            with self.subTest(i=i):
                x = x_original.copy()
                x[i] = ''

                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'2 1 {x[0]}',
                    f'ms: 0 1 {x[1]}',
                    f'{x[2]} 1',
                    f'cm: 1  3  3  1',
                    f'cm: 1  1  2  2',
                    f'4 1',
                    f'cm: 2  4  4  2',
                    f'cm: 1  1  2  2',
                ])

                with self.assertRaises(PolygonFileFormatError):
                    self.polygon_file_blank.parse()

    def test_undefined_units(self):
        # Verifies that an error is thrown if units are not recognized
        x_original = ['ms', 'cm']

        for i in range(len(x_original)):
            with self.subTest(i=i):
                x = x_original.copy()
                x[i] = 'nonexistentUnit'

                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'2 1 0',
                    f'{x[0]}: 0 1 0',
                    f'4 1',
                    f'cm: 1  3  3  1',
                    f'{x[1]}: 1  1  2  2',
                    f'4 1',
                    f'cm: 2  4  4  2',
                    f'cm: 1  1  2  2',
                ])

                with self.assertRaises((PolygonFileFormatError, ValueError)):
                    self.polygon_file_blank.parse()

    def test_read_polygon_merge_method(self):
        # Verifies that files with different "polygon_merge_method" attributes
        # are parsed correctly
        for i, valid in ((0, True), (1, True), (2, True), ('1.0', True), (3, False)):
            with self.subTest(polygon_merge_method=i):
                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'1 1 {i}',
                    '4 1',
                    'm: 1  5  5    1',
                    'm: 0  0  2.5  2.5',
                ])

                if valid:
                    self.polygon_file_blank.parse()
                    self.assertEqual(self.polygon_file_blank.polygon_merge_method, float(i))
                else:
                    with self.assertRaises(ValueError):
                        self.polygon_file_blank.parse()

    def test_read_time_extrap_method(self):
        # Verifies that files with different "time_extrap_method" attributes
        # are parsed correctly
        for i, valid in ((0, True), (2, True), (3, True), ('2.0', True), (1, False)):
            with self.subTest(time_extrap_method=i):
                self.polygon_file_blank.contents.clear()
                self.polygon_file_blank.contents.extend([
                    f'2 1 0',
                    f'ms: 0 1 {i}',
                    f'4 1',
                    f'cm: 1  3  3  1',
                    f'cm: 1  1  2  2',
                    f'4 1',
                    f'cm: 2  4  4  2',
                    f'cm: 1  1  2  2',
                ])

                if valid:
                    self.polygon_file_blank.parse()
                    self.assertEqual(self.polygon_file_blank.time_extrap_method, float(i))
                else:
                    with self.assertRaises(ValueError):
                        self.polygon_file_blank.parse()

    def test_different_coordinate_units(self):
        # Verifies that an exception is thrown if x- and y-coordinates for a
        # polygon have different units
        self.polygon_file_blank.contents.clear()
        self.polygon_file_blank.contents.extend([
            '1 1 0',
            '4 1',
            'm: 1  5  5    1',
            'mm: 0  0  2.5  2.5',
        ])

        with self.assertRaises(PolygonFileFormatError):
            self.polygon_file_blank.parse()

    def test_different_num_coordinates(self):
        # Verifies that an exception is thrown if different numbers of x- and
        # y-coordinates for a polygon are provided
        with self.subTest(x_correct=False, y_correct=True):
            self.polygon_file_blank.contents.clear()
            self.polygon_file_blank.contents.extend([
                '1 1 0',
                '4 1',
                'm: 1  5  5',
                'm: 0  0  2.5  2.5',
            ])

            with self.assertRaises(PolygonFileFormatError):
                self.polygon_file_blank.parse()

        with self.subTest(x_correct=False, y_correct=False):
            self.polygon_file_blank.contents.clear()
            self.polygon_file_blank.contents.extend([
                '1 1 0',
                '3 1',
                'm: 1  5  5    1',
                'm: 0  0  2.5  2.5',
            ])

            with self.assertRaises(PolygonFileFormatError):
                self.polygon_file_blank.parse()

    def test_file_too_short(self):
        # Verifies that an exception is thrown if polygon file does not
        # contain data it should contain
        self.polygon_file_blank.contents.clear()
        self.polygon_file_blank.contents.extend([
            '3 2 0',
            'ms: 0 1 0',
            '4 1',
            'cm: 1  3  3  1',
            'cm: 1  1  2  2',
            '3 0',
            'cm: 1  2  1',
            'cm: 1  1  2',
        ])

        with self.assertRaises(PolygonFileFormatError):
            self.polygon_file_blank.parse()

    def test_file_too_long(self):
        # Verifies that an exception is thrown if polygon file contains more
        # polygon data than it should
        self.polygon_file_blank.contents.clear()
        self.polygon_file_blank.contents.extend([
            '3 1 0',
            'ms: 0 1 0',
            '4 1',
            'cm: 1  3  3  1',
            'cm: 1  1  2  2',
            '3 0',
            'cm: 1  2  1',
            'cm: 1  1  2',
            '4 0',
            'cm: 2  4  4  2',
            'cm: 1  1  2  2',
            '3 0',
            'cm: 1  2  1',
            'cm: 2  2  3',
            '4 1',
            'cm: 3  5  5  3',
            'cm: 1  1  2  2',
            '3 1',
            'cm: 1  2  1',
            'cm: 3  3  4',
        ])

        with self.assertRaises(PolygonFileFormatError):
            self.polygon_file_blank.parse()
