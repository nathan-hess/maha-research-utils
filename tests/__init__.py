import pathlib

# Define variables available to all tests
PROJECT_TEST_DIR = pathlib.Path(__file__).resolve().parent
SAMPLE_FILES_DIR = PROJECT_TEST_DIR / 'sample_files'

# Import and run tests
from .files import *
from .utils import *
