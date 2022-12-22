import math

import numpy as np


# Define variables available to all tests
TEST_FLOAT_TOLERANCE = 1e-12
TEST_FLOAT_TOLERANCE_DECIMAL_PLACES = int(-math.log10(TEST_FLOAT_TOLERANCE))


# Define basic testing utilities
def max_array_diff(array1, array2):
    return np.max(np.abs(np.array(array1) - np.array(array2)))


# Import and run tests
from .dictionaries import *
from .multics import *
