import string
import unittest

from mahautils.units import parse_unit
from mahautils.units.parser import _add_to_dict, _check_dict_keys, _is_unit
from mahautils.units.exceptions import (
    InvalidExponentError,
    InvalidUnitError,
    ParserMaxIterationError,
)


class Test_AddToDict(unittest.TestCase):
    def test_add_new(self):
        # Verifies that a new unit (not already present in the dictionary)
        # is correctly added
        dictionary = {}

        _add_to_dict(dictionary, 'mm', 3)
        self.assertDictEqual(dictionary, {'mm': 3})

        _add_to_dict(dictionary, 'kg/s', -4.3)
        self.assertDictEqual(dictionary, {'mm': 3, 'kg/s': -4.3})

    def test_add_existing(self):
        # Verifies that an existing unit's exponent is correctly updated
        dictionary = {'mm': 3, 'kg/s': -4.3}

        _add_to_dict(dictionary, 'kg/s', 5)
        modified_dictionary = {'mm': 3, 'kg/s': 0.7}

        self.assertEqual(dictionary.keys(), modified_dictionary.keys())

        for key in dictionary.keys():
            self.assertAlmostEqual(dictionary[key], modified_dictionary[key])


class Test_CheckDictKeys(unittest.TestCase):
    def test_all_keys_units(self):
        # Verifies that function returns `True` if all dictionary keys are
        # fully-simplified units
        self.assertTrue(_check_dict_keys(
            {'mm': 3.2, 's': -3, 'kg': 2}, string.digits + '*/^().'))

        self.assertTrue(_check_dict_keys(
            {'m*s': 3.2, 'kg': 2}, 'abc'))

    def test_invalid_units(self):
        # Verifies that function returns `False` if any dictionary keys are
        # not fully-simplified units
        self.assertFalse(_check_dict_keys(
            {'mm': 3.2, 's/N': -3, 'kg': 2}, string.digits + '*/^().'))

        self.assertFalse(_check_dict_keys(
            {'m*s': 3.2, 'kg': 2}, 'k'))


class Test_IsUnit(unittest.TestCase):
    def test_is_unit_true(self):
        # Verify that fully-simplified units return `True`
        self.assertTrue(_is_unit('kg', '/*'))
        self.assertTrue(_is_unit('m*s', 'abcdef'))

    def test_is_unit_false(self):
        # Verify that compound units return `False`
        self.assertFalse(_is_unit('kg/s', '/*'))
        self.assertFalse(_is_unit('dog', 'abcdef'))


class Test_ParseUnit(unittest.TestCase):
    def test_invalid_type(self):
        # Verifies that an error is thrown if attempting to pass an
        # invalid type
        with self.assertRaises(TypeError):
            parse_unit(100)

    def test_unmatched_parentheses(self):
        # Verifies that an error is thrown if attempting to pass a
        # unit with unmatched parentheses
        with self.assertRaises(ValueError):
            parse_unit('kg/(s')

        with self.assertRaises(ValueError):
            parse_unit('kg)/(s)')

    def test_missing_multiplication(self):
        # Verifies that an error is thrown if attempting to multiply units
        # without a multiplication sign
        with self.assertRaises(InvalidUnitError):
            parse_unit('(N)(m)')

    def test_parse_simple_unit(self):
        # Verifies that simple units with no exponent are parsed correctly
        self.assertDictEqual(parse_unit('kg'), {'kg': 1})
        self.assertDictEqual(parse_unit('m'), {'m': 1})
        self.assertDictEqual(parse_unit('micron'), {'micron': 1})
        self.assertDictEqual(parse_unit(''), {})

    def test_parse_simple_unit_whitespace(self):
        # Verifies that simple units with whitespace are parsed correctly
        self.assertDictEqual(parse_unit('kg  '), {'kg': 1})
        self.assertDictEqual(parse_unit('  m'), {'m': 1})
        self.assertDictEqual(parse_unit('micron\t'), {'micron': 1})
        self.assertDictEqual(parse_unit('\t'), {})

    def test_parse_simple_unit_multiplied(self):
        # Verifies that simple units with multiplication are parsed correctly
        self.assertDictEqual(parse_unit('kg*m'), {'kg': 1, 'm': 1})
        self.assertDictEqual(parse_unit('(N)*(m)'), {'N': 1, 'm': 1})
        self.assertDictEqual(parse_unit('kg*m*m'), {'kg': 1, 'm': 2})
        self.assertDictEqual(parse_unit('kg*((m))'), {'kg': 1, 'm': 1})
        self.assertDictEqual(parse_unit('kg*m *s'), {'kg': 1, 'm': 1, 's': 1})
        self.assertDictEqual(parse_unit('kg*(m *s)'), {'kg': 1, 'm': 1, 's': 1})
        self.assertDictEqual(parse_unit('(kg*m) *s'), {'kg': 1, 'm': 1, 's': 1})

    def test_parse_simple_unit_exponent(self):
        # Verifies that simple units with an exponent are parsed correctly
        self.assertDictEqual(parse_unit('kg**2'), {'kg': 2.0})
        self.assertDictEqual(parse_unit('m^2'), {'m': 2.0})
        self.assertDictEqual(parse_unit('(micron)^4\t'), {'micron': 4.0})
        self.assertDictEqual(parse_unit('((m))^(3)'), {'m': 3.0})
        self.assertDictEqual(parse_unit('(cm)^(-43)'), {'cm': -43.0})

    def test_parse_asterisk_exponent(self):
        # Verifies that units with "**" exponents are parsed correctly
        self.assertDictEqual(parse_unit('kg**2'), {'kg': 2.0})
        self.assertDictEqual(parse_unit('m/s**2'), {'m': 1.0, 's': -2.0})
        self.assertDictEqual(parse_unit('m^2/s**3'), {'m': 2.0, 's': -3.0})

    def test_parse_scientific_exponent(self):
        # Verifies that units with exponents in scientific notation are
        # parsed correctly
        self.assertDictEqual(parse_unit('kg**(2e0)'), {'kg': 2.0})
        self.assertDictEqual(parse_unit('m/s ^ 2e1'), {'m': 1.0, 's': -20.0})
        self.assertDictEqual(parse_unit('(m^2/s) **3e-2'), {'m': 0.06, 's': -0.03})

    def test_parse_fraction_unit(self):
        # Verifies that units with fractions are parsed correctly
        self.assertDictEqual(parse_unit('m/s'), {'m': 1, 's': -1})
        self.assertDictEqual(parse_unit('kg*m/s'), {'kg': 1, 'm': 1, 's': -1})
        self.assertDictEqual(parse_unit('m/s/s'), {'m': 1, 's': -2})
        self.assertDictEqual(parse_unit('m/m'), {})

    def test_parse_fraction_unit_parentheses(self):
        # Verifies that units with fractions with parentheses are
        # parsed correctly
        self.assertDictEqual(parse_unit('(m)/s'), {'m': 1, 's': -1})
        self.assertDictEqual(parse_unit('kg*(m/s)'), {'kg': 1, 'm': 1, 's': -1})
        self.assertDictEqual(parse_unit('(m/s/s)'), {'m': 1, 's': -2})
        self.assertDictEqual(parse_unit('(m/(s/((kg*m))/s))'), {'kg': 1, 'm': 2})

    def test_iteration_limit(self):
        # Verifies that error is thrown if iteration limit is reached
        n = 40
        unit1 = f"{'m/(s*'*n}m{')'*n}"

        self.assertDictEqual(parse_unit(unit1, max_iterations=80), {'m': 1})

        with self.assertRaises(ParserMaxIterationError):
            parse_unit(unit1, max_iterations=79)

        unit2 = 'm*(K/s)'
        with self.assertRaises(ParserMaxIterationError):
            parse_unit(unit2, max_iterations=1)

    def test_invalid_operator_usage(self):
        # Verifies that an error is thrown if attempting to parse a unit
        # that begins or ends with `*`, `/`, or `^`
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('*kg')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('kg*')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(*kg)/s')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(kg*)/s')

        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('/kg')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('kg/')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(/kg)*s')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(kg/)*s')

        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('^kg')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('kg^')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(^kg)/s')
        with self.assertRaises((InvalidUnitError, IndexError)):
            parse_unit('(kg^)/s')

    def test_non_numeric_exponent(self):
        # Verifies that an error is thrown if attempting to parse a unit with
        # a non-numeric exponent
        with self.assertRaises(InvalidExponentError):
            parse_unit('kg^a')
        with self.assertRaises(InvalidExponentError):
            parse_unit('kg^(a)')
        with self.assertRaises(InvalidExponentError):
            parse_unit('m^2*(kg^(a))')

    def test_invalid_base(self):
        # Verifies that an error is thrown if attempting to parse a unit with
        # a base (value raised to an exponent) not formatted as expected
        with self.assertRaises(InvalidUnitError):
            parse_unit('m*2^5')
        with self.assertRaises(InvalidUnitError):
            parse_unit('m^2^5')
        with self.assertRaises(InvalidUnitError):
            parse_unit('(2/m)^5')

    def test_negative_exponent_no_parentheses(self):
        # Verifies that unit parser handles negative units not enclosed in
        # parentheses as expected (this is bad practice, but should still be
        # parsed consistently)
        self.assertDictEqual(parse_unit('kg^-2'), {'kg': -2})
        self.assertDictEqual(
            parse_unit('mm*cm^-2/(ft^-4)/micron*mm^3'),
            {'mm': 4, 'cm': -2, 'micron': -1, 'ft': 4})

    def test_compound_unit(self):
        # Verifies unit parser functionality for relatively complex, compound
        # unit expressions
        self.assertDictEqual(
            parse_unit('m^5 * (kg/N)/s^(-2) / (mm**-4   * kg)^-6'),
            {'m': 5.0, 'kg': 7.0, 'N': -1.0, 's': 2.0, 'mm': -24.0})
        self.assertDictEqual(
            parse_unit('m*((((s/(kg/s)^2)^(4e0)  * kg/m)** -3)^7 / s^2/kg*m/m)^3'),
            {'kg': 438.0, 'm': 64.0, 's': -762.0})
