import unittest

from mahautils.units import (
    UnitSystem,
    UnitSystemSI,
)


class Test_UnitSystem(unittest.TestCase):
    def test_set_num_fundamental_units(self):
        # Verifies that number of fundamental units are set correctly
        self.assertEqual(UnitSystem(7).num_fundamental_units, 7)
        self.assertEqual(UnitSystem(3).num_fundamental_units, 3)

    def test_invalid_num_fundamental_units(self):
        # Verifies that an error is thrown if the number of fundamental
        # units provided is invalid
        with self.assertRaises(TypeError):
            UnitSystem(7.3)

        with self.assertRaises(TypeError):
            UnitSystem('9')

        with self.assertRaises(ValueError):
            UnitSystem(0)

        with self.assertRaises(ValueError):
            UnitSystem(-4)

    def test_set_name(self):
        # Verifies that name is set correctly
        self.assertEqual(UnitSystem(7, name='System').name, 'System')
        self.assertEqual(UnitSystem(7).name, '')

    def test_invalid_name(self):
        # Verifies that an error is thrown if the name provided is invalid
        with self.assertRaises(TypeError):
            UnitSystem(7, name=100)

    def test_set_description(self):
        # Verifies that description is set correctly
        self.assertEqual(UnitSystem(7, description='UnitSys').description, 'UnitSys')
        self.assertEqual(UnitSystem(7).description, '')

    def test_invalid_description(self):
        # Verifies that an error is thrown if the description
        # provided is invalid
        with self.assertRaises(TypeError):
            UnitSystem(7, description=100)

    def test_str(self):
        # Verifies that unit system string representation is correct
        unit_system_1 = UnitSystem(7)
        self.assertEqual(
            str(unit_system_1),
            "<class 'mahautils.units.unitsystem.UnitSystem'>")

        unit_system_2 = UnitSystem(7, name='TestName')
        self.assertEqual(
            str(unit_system_2),
            "<class 'mahautils.units.unitsystem.UnitSystem'> - TestName")

        unit_system_3 = UnitSystem(7, description='TestDescription')
        self.assertEqual(
            str(unit_system_3),
            "<class 'mahautils.units.unitsystem.UnitSystem'> - TestDescription")

        unit_system_4 = UnitSystem(7, name='TestName', description='TestDescription')
        self.assertEqual(
            str(unit_system_4),
            "<class 'mahautils.units.unitsystem.UnitSystem'> - TestName - TestDescription")

    def test_repr(self):
        # Verifies that unit system object representation is correct
        unit_system = UnitSystem(7, name='TestName', description='TestDescription')
        self.assertEqual(
            unit_system.__repr__(),
            "<class 'mahautils.units.unitsystem.UnitSystem'> - TestName - TestDescription")


class Test_UnitSystemSI(unittest.TestCase):
    def setUp(self):
        self.unit_system = UnitSystemSI()

    def test_num_fundamental_units(self):
        # Verifies that `mahautils.dictionary.units.UnitSystemSI` has the
        # correct number of fundamental units set
        self.assertEqual(self.unit_system.num_fundamental_units, 7)

    def test_name(self):
        # Verifies that `mahautils.dictionary.units.UnitSystemSI` has the
        # correct name set
        self.assertEqual(self.unit_system.name, 'SI')

    def test_description(self):
        # Verifies that `mahautils.dictionary.units.UnitSystemSI` has the
        # correct description set
        self.assertEqual(self.unit_system.description,
                         'International System of Units')
