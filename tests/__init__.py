import io
import pathlib
import sys


class CapturePrint:
    """Captures text printed to the terminal when running commands"""
    def __enter__(self):
        self.terminal_stdout = io.StringIO()
        sys.stdout = self.terminal_stdout
        return self.terminal_stdout

    def __exit__(self, *args, **kwargs):
        sys.stdout = sys.__stdout__


# Define variables available to all tests
PROJECT_TEST_DIR = pathlib.Path(__file__).resolve().parent
SAMPLE_FILES_DIR = PROJECT_TEST_DIR / 'sample_files'


# Import and run tests
from .dictionary import *
from .files import *
from .units import *
from .utils import *
