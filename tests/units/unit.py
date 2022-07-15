import unittest

import numpy as np

from mahautils.units import (
    Unit,
    UnitLinear,
    UnitLinearSI,
    UnitSystem,
    UnitSystemSI,
)


class Test_Unit(unittest.TestCase):
    def setUp(self):
        self.unit01 = Unit(
            unit_system=UnitSystemSI(),
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            to_base_function=lambda x: x,
            from_base_function=lambda x: x,
            identifier='kg', name='kilogram')

        self.unit02 = Unit(
            unit_system=UnitSystem(5),
            derived_exponents=[0, 1, 0, 0, 0],
            to_base_function=lambda x: x / 1000.0,
            from_base_function=lambda x: x * 1000.0,
            identifier='ms', name='millisecond')

        self.unit03 = Unit(
            unit_system=UnitSystemSI(),
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            to_base_function=lambda x: x,
            from_base_function=lambda x: x,
            identifier='kg')

        self.unit04 = Unit(
            unit_system=UnitSystemSI(),
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            to_base_function=lambda x: x,
            from_base_function=lambda x: x,
            name='kilogram')

    def test_set_unit_system(self):
        # Verifies that unit system is set correctly
        self.assertIs(type(self.unit01.unit_system), UnitSystemSI)
        self.assertIs(type(self.unit02.unit_system), UnitSystem)

        self.assertIsNot(type(self.unit01.unit_system), UnitSystem)
        self.assertIsNot(type(self.unit02.unit_system), UnitSystemSI)

    def test_set_identifier(self):
        # Verifies that "identifier" attribute is set correctly
        self.assertEqual(self.unit01.identifier, 'kg')
        self.assertEqual(self.unit02.identifier, 'ms')

    def test_set_name(self):
        # Verifies that "name" attribute is set correctly
        self.assertEqual(self.unit01.name, 'kilogram')
        self.assertEqual(self.unit02.name, 'millisecond')

    def test_invalid_identifier(self):
        # Verifies that an invalid "identifier" attribute
        # results in an error being thrown
        with self.assertRaises(TypeError):
            Unit(
                unit_system=UnitSystemSI(),
                derived_exponents=[0, 0, 0, 0, 0, 0, 1],
                to_base_function=lambda x: x,
                from_base_function=lambda x: x,
                identifier=0, name='kilogram')

    def test_invalid_name(self):
        # Verifies that an invalid "name" attribute
        # results in an error being thrown
        with self.assertRaises(TypeError):
            Unit(
                unit_system=UnitSystemSI(),
                derived_exponents=[0, 0, 0, 0, 0, 0, 1],
                to_base_function=lambda x: x,
                from_base_function=lambda x: x,
                identifier='kg', name=0)

    def test_set_derived_exponents(self):
        # Verifies that derived exponents are set correctly
        self.assertTrue(np.array_equal(
            self.unit01.derived_exponents,
            np.array([0, 0, 0, 0, 0, 0, 1])))

        self.assertTrue(np.array_equal(
            self.unit02.derived_exponents,
            np.array([0, 1, 0, 0, 0])))

    def test_invalid_derived_exponents(self):
        # Verifies that an error is thrown if attempting to create
        # a unit with the wrong number of derived exponent values
        with self.assertRaises(ValueError):
            Unit(
                unit_system=UnitSystemSI(),
                derived_exponents=[0, 0, 0, 0, 0, 1],
                to_base_function=lambda x: x,
                from_base_function=lambda x: x)

        with self.assertRaises(ValueError):
            Unit(
                unit_system=UnitSystem(4),
                derived_exponents=[0, 0, 0, 0, 0, 0, 1],
                to_base_function=lambda x: x,
                from_base_function=lambda x: x)

    def test_str(self):
        # Verifies that string representation of unit is formatted correctly
        self.assertEqual(str(self.unit01),
                         'kg - kilogram - [0. 0. 0. 0. 0. 0. 1.]')

        self.assertEqual(str(self.unit02),
                         'ms - millisecond - [0. 1. 0. 0. 0.]')

        self.assertEqual(str(self.unit03),
                         'kg - [0. 0. 0. 0. 0. 0. 1.]')

        self.assertEqual(str(self.unit04),
                         'kilogram - [0. 0. 0. 0. 0. 0. 1.]')

    def test_repr(self):
        # Verifies that representation of unit is formatted correctly
        self.assertEqual(str(self.unit01.__repr__()),
            "<class 'mahautils.units.unit.Unit'> kg - kilogram - [0. 0. 0. 0. 0. 0. 1.]")

    def test_is_convert_valid(self):
        # Verifies that units that are compatible for conversion are
        # correctly identified
        self.assertTrue(self.unit01.is_convertible(self.unit03))

        unit02_convert = Unit(
            unit_system=UnitSystem(5),
            derived_exponents=[0, 1, 0, 0, 0],
            to_base_function=lambda x: x / 1000.0,
            from_base_function=lambda x: x * 1000.0,
            identifier='s', name='second')
        self.assertTrue(self.unit02.is_convertible(unit02_convert))

    def test_is_convert_invalid_type(self):
        # Verifies that units with different types are identified as
        # incompatible for conversion
        unit01_different_type = Unit(
            unit_system=UnitSystem(7),
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            to_base_function=lambda x: x,
            from_base_function=lambda x: x,
            identifier='kg', name='kilogram')
        self.assertFalse(self.unit01.is_convertible(unit01_different_type))

    def test_is_convert_invalid_exps(self):
        # Verifies that units with different `derived_exponents` attributes
        # are identified as incompatible for conversion
        unit01_different_exp = Unit(
            unit_system=UnitSystemSI(),
            derived_exponents=[0, 1, 0, 0, 0, 0, 1],
            to_base_function=lambda x: x,
            from_base_function=lambda x: x,
            identifier='kg', name='kilogram')
        self.assertFalse(self.unit01.is_convertible(unit01_different_exp))

        unit02_different_exp = Unit(
            unit_system=UnitSystem(6),
            derived_exponents=[0, 1, 0, 0, 0, 1],
            to_base_function=lambda x: x / 1000.0,
            from_base_function=lambda x: x * 1000.0,
            identifier='ms', name='millisecond')
        self.assertFalse(self.unit02.is_convertible(unit02_different_exp))

    def test_to_base_int(self):
        # Verifies that conversion of an integer value from
        # given object's units to base units is performed correctly
        self.assertAlmostEqual(self.unit01.to_base(1000), 1000)
        self.assertAlmostEqual(self.unit02.to_base(1000), 1)

    def test_to_base_float(self):
        # Verifies that conversion of a floating-point value from
        # given object's units to base units is performed correctly
        self.assertAlmostEqual(self.unit01.to_base(3.23), 3.23)
        self.assertAlmostEqual(self.unit02.to_base(932.3), 0.9323)

    def test_to_base_array(self):
        # Verifies that conversion of an array of values from
        # given object's units to base units is performed correctly
        inputs = [3.23, 1000, 5095.3, 1900]

        outputs = np.array([3.23, 1000, 5095.3, 1900])
        self.assertTrue(np.array_equal(
            self.unit01.to_base(np.array(inputs)),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit01.to_base(inputs),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit01.to_base(tuple(inputs)),
            outputs))

        outputs = np.array([0.00323, 1, 5.0953, 1.9])
        self.assertTrue(np.array_equal(
            self.unit02.to_base(np.array(inputs)),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit02.to_base(inputs),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit02.to_base(tuple(inputs)),
            outputs))

    def test_from_base_int(self):
        # Verifies that conversion of an integer value from
        # base units to the given object's units is performed correctly
        self.assertAlmostEqual(self.unit01.from_base(1000), 1000)
        self.assertAlmostEqual(self.unit02.from_base(1000), 1e6)

    def test_from_base_float(self):
        # Verifies that conversion of a floating-point value from
        # base units to the given object's units is performed correctly
        self.assertAlmostEqual(self.unit01.from_base(3.23), 3.23)
        self.assertAlmostEqual(self.unit02.from_base(932.3), 9.323e5)

    def test_from_base_array(self):
        # Verifies that conversion of an array of values from
        # base units to the given object's units is performed correctly
        inputs = [3.23, 1000, 5095.3, 1900]

        outputs = np.array([3.23, 1000, 5095.3, 1900])
        self.assertTrue(np.array_equal(
            self.unit01.from_base(np.array(inputs)),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit01.from_base(inputs),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit01.from_base(tuple(inputs)),
            outputs))

        outputs = np.array([3230, 1e6, 5.0953e6, 1.9e6])
        self.assertTrue(np.array_equal(
            self.unit02.from_base(np.array(inputs)),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit02.from_base(inputs),
            outputs))
        self.assertTrue(np.array_equal(
            self.unit02.from_base(tuple(inputs)),
            outputs))


class Test_LinearUnit(unittest.TestCase):
    def setUp(self):
        self.unit01 = UnitLinear(
            unit_system=UnitSystemSI(),
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            scale=0.001, offset=0,
            identifier='g', name='gram')

        self.unit02 = UnitLinear(
            unit_system=UnitSystem(5),
            derived_exponents=[0, 1, 0, 0, 0],
            scale=5/9, offset=273.15-32*5/9,
            identifier='°F', name='degrees Fahrenheit')

    def test_set_scale(self):
        # Verifies that "scale" attribute is set correctly
        self.assertAlmostEqual(self.unit01.scale, 0.001)
        self.assertAlmostEqual(self.unit02.scale, 5/9)

    def test_set_offset(self):
        # Verifies that "offset" attribute is set correctly
        self.assertAlmostEqual(self.unit01.offset, 0)
        self.assertAlmostEqual(self.unit02.offset, 273.15-32*5/9)

    def test_str(self):
        # Verifies that string representation of object is formatted correctly
        self.assertEqual(
            str(self.unit01),
            'g - gram - [0. 0. 0. 0. 0. 0. 1.] - scale: 0.001 - offset: 0.0')

        self.assertEqual(
            str(self.unit02),
            ('°F - degrees Fahrenheit - [0. 1. 0. 0. 0.] '
             '- scale: 0.5555555555555556 - offset: 255.3722222222222'))

    def test_to_base(self):
        # Verifies that conversion of from base units to the given object's
        # units is performed correctly
        self.assertTrue(np.array_equal(
            self.unit01.to_base([2, 4.3, 930]),
            np.array([0.002, 0.0043, 0.93])))

        diff = self.unit02.to_base([32, 9.332, 14, -40]) \
            - np.array([273.15, 273.15+(9.332-32)*(5/9), 263.15, 233.15])
        self.assertLessEqual(np.max(np.abs(diff)), 1e-12)

    def test_from_base(self):
        # Verifies that conversion of from the given object's
        # units to the base units is performed correctly
        self.assertTrue(np.array_equal(
            self.unit01.from_base([0.002, 0.0043, 0.93]),
            np.array([2, 4.3, 930])))

        diff = self.unit02.from_base([273.15, 273.15+(9.332-32)*(5/9), 263.15, 233.15]) \
            - np.array([32, 9.332, 14, -40])
        self.assertLessEqual(np.max(np.abs(diff)), 1e-12)


class Test_LinearUnitSI(unittest.TestCase):
    def test_unit_system(self):
        # Verifies that the unit system is set to "SI"
        unit = UnitLinearSI(
            derived_exponents=[0, 0, 0, 0, 0, 0, 1],
            scale=0.001, offset=0)

        self.assertIs(type(unit.unit_system), UnitSystemSI)
