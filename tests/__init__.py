# Define variables available to all tests
import pathlib

TEST_DIR = pathlib.Path(__file__).resolve().parent
SAMPLE_FILES_DIR = TEST_DIR / 'sample_files'

# Import and run tests
from .dict import *
from .files import *
