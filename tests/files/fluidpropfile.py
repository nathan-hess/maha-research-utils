##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import unittest

# Custom package and module imports
import mahautils
from mahautils.files.exceptions import InvalidFileFormat
from tests import SAMPLE_FILES_DIR


##############################################################################
# --- TEST CASES: FLUID PROPERTY FILE -------------------------------------- #
##############################################################################
class Test_FluidPropertyFile(unittest.TestCase):
    def test_num_temp(self):
        # Check whether the number of temperature steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertEqual(fluid_prop.num_temperature, 4)

    def test_num_pressure(self):
        # Check whether the number of pressure steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertEqual(fluid_prop.num_pressure, 3)

    def test_temp_step(self):
        # Check whether the size of temperature steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertAlmostEqual(fluid_prop.step_temperature, 1)

    def test_pressure_step(self):
        # Check whether the size of pressure steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertAlmostEqual(fluid_prop.step_pressure, 1000)

    def test_temp_vals(self):
        # Check whether the list of temperature steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertListEqual(
            fluid_prop.vals_temperature,
            [201, 202, 203, 204]
        )

    def test_pressure_vals(self):
        # Check whether the list of pressure steps is read correctly
        fluid_prop = mahautils.files.FluidPropertyFile()
        fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_001.txt')

        self.assertListEqual(
            fluid_prop.vals_pressure,
            [4151.56846, 5151.5684600000000, 6151.56846]
        )

    def test_invalid_temp_step(self):
        # Check whether an error is correctly thrown if the stated temperature
        # step in a fluid property file does not match the difference between
        # stated temperature values
        fluid_prop = mahautils.files.FluidPropertyFile()

        with self.assertRaises(ValueError):
            fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_002.txt')

    def test_invalid_pressure_step(self):
        # Check whether an error is correctly thrown if the stated pressure
        # step in a fluid property file does not match the difference between
        # stated pressure values
        fluid_prop = mahautils.files.FluidPropertyFile()

        with self.assertRaises(ValueError):
            fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_003.txt')

    def test_invalid_num_lines(self):
        # Check whether an error is correctly thrown if the number of lines
        # in a fluid property file does not match the stated number of
        # temperature and pressure steps
        fluid_prop = mahautils.files.FluidPropertyFile()

        with self.assertRaises(InvalidFileFormat):
            fluid_prop.read(SAMPLE_FILES_DIR / 'fluidProperties_004.txt')
