import unittest

import numpy as np

from mahautils.utils import to_np_1D_array
from tests import max_array_diff, TEST_FLOAT_TOLERANCE


class Test_ToNumPy1DArray(unittest.TestCase):
    def test_convert_float(self):
        # Verifies that a single number can be converted to a 1D NumPy array
        with self.subTest(flatten=True):
            outputs = to_np_1D_array(2.5, dtype=np.float64, flatten=True)

            self.assertLessEqual(max_array_diff(outputs, [2.5]), TEST_FLOAT_TOLERANCE)
            self.assertEqual(outputs.ndim, 1)

        with self.subTest(flatten=False):
            outputs = to_np_1D_array(2.5, dtype=np.float64, flatten=False)

            self.assertLessEqual(max_array_diff(outputs, [2.5]), TEST_FLOAT_TOLERANCE)
            self.assertEqual(outputs.ndim, 1)

    def test_convert_list(self):
        # Verifies that a list can be converted to a 1D NumPy array
        for method in (list, tuple, np.array):
            with self.subTest(method=str(method)):
                outputs = to_np_1D_array(method([0, 1, -2.5, 3e4]))

                self.assertLessEqual(max_array_diff(outputs, [0, 1, -2.5, 3e4]),
                                     TEST_FLOAT_TOLERANCE)
                self.assertEqual(outputs.ndim, 1)

    def test_convert_matrix(self):
        # Verifies that a matrix can be converted to a 1D NumPy array
        inputs = [[1,    -2.3, 4],
                  [-5.6, 7.89, 0]]

        with self.subTest(flatten=True):
            outputs = to_np_1D_array(inputs, flatten=True)

            self.assertLessEqual(max_array_diff(outputs, [1, -2.3, 4, -5.6, 7.89, 0]),
                                 TEST_FLOAT_TOLERANCE)
            self.assertEqual(outputs.ndim, 1)

        with self.subTest(flatten=False):
            with self.assertRaises(ValueError):
                to_np_1D_array(inputs, flatten=False)
