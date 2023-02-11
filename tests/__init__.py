import io
import math
import pathlib
import sys

import numpy as np


# Define variables available to all tests
PROJECT_TEST_DIR = pathlib.Path(__file__).resolve().parent
SAMPLE_FILES_DIR = PROJECT_TEST_DIR / '_sample_files'
TEST_TMP_DIR = PROJECT_TEST_DIR / 'tmp'

TEST_FLOAT_TOLERANCE = 1e-12
TEST_FLOAT_TOLERANCE_DECIMAL_PLACES = int(-math.log10(TEST_FLOAT_TOLERANCE))


# Define context managers to facilitate testing
class CapturePrint:
    """Captures text printed to the terminal when running commands"""
    def __enter__(self):
        self.terminal_stdout = io.StringIO()
        sys.stdout = self.terminal_stdout
        return self.terminal_stdout

    def __exit__(self, *args, **kwargs):
        sys.stdout = sys.__stdout__


# Define basic testing utilities
def max_array_diff(array1, array2):
    return np.max(np.abs(np.array(array1) - np.array(array2)))


# Import and run tests
from .dictionaries import *
from .multics import *
