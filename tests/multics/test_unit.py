import math
import unittest

import numpy as np

from mahautils.multics import (
    MahaMulticsUnitSystem,
    MahaMulticsUnit,
    MahaMulticsUnitConverter,
)
from tests import (
    max_array_diff,
    TEST_FLOAT_TOLERANCE,
    TEST_FLOAT_TOLERANCE_DECIMAL_PLACES,
)


class Test_MahaMulticsUnitSystem(unittest.TestCase):
    def test_num_base_units(self):
        # Verifies that Maha Multics-specific system of units contains the
        # correct number of base units
        self.assertEqual(MahaMulticsUnitSystem().num_base_units, 7)


class Test_MahaMulticsUnit(unittest.TestCase):
    def setUp(self):
        self.unit = MahaMulticsUnit(
            base_unit_exps=[0, 1, 0, 0, 0, 1, 0],
            scale=0.001, offset=3
        )

    def test_unit_system(self):
        # Verifies that Maha Multics-specific unit contains the
        # correct system of units
        self.assertIs(type(self.unit.unit_system), MahaMulticsUnitSystem)

    def test_convert_unit(self):
        # Verifies that Maha Multics-specific units function the same way as
        # PyXX linear units
        with self.subTest(conversion='to_base'):
            self.assertLessEqual(
                max_array_diff(
                    self.unit.to_base_function(np.array([28, -67.46, 95.13]), 1),
                    [3.028, 2.93254, 3.09513]),
                TEST_FLOAT_TOLERANCE
            )

        with self.subTest(conversion='from_base'):
            self.assertLessEqual(
                max_array_diff(
                    self.unit.from_base_function(np.array([3.028, 2.93254, 3.09513]), 1),
                    [28, -67.46, 95.13]),
                TEST_FLOAT_TOLERANCE
            )


class Test_MahaMulticsUnitConverter(unittest.TestCase):
    def test_unit_conversions(self):
        # Verifies that a variety of unit conversions are performed correctly
        test_cases = [
            {'quantity': 1,   'from': 'm',         'to': 'm',     'expected': 1},
            {'quantity': 1,   'from': 'mm',        'to': 'm',     'expected': 0.001},
            {'quantity': 1,   'from': 'm',         'to': 'cm',    'expected': 100},
            {'quantity': 20,  'from': 'kg*m/s^2',  'to': 'N',     'expected': 20},
            {'quantity': 1,   'from': 'm^3',       'to': 'L',     'expected': 1000},
            {'quantity': 0,   'from': 'Pa',        'to': 'Pa_a',  'expected': 101325},
            {'quantity': 10,  'from': 'bar_a',     'to': 'Pa_a',  'expected': 1000000},
            {'quantity': 10,  'from': 'psi_a',     'to': 'Pa_a',  'expected': 68947.57293168361},
            {'quantity': 32,  'from': 'degF',      'to': 'K',     'expected': 273.15},
            {'quantity': 32,  'from': 'degF',      'to': 'degR',  'expected': 491.67},
            {'quantity': 30,  'from': 'deg',       'to': 'rad',   'expected': math.pi/6},
            {'quantity': 1,   'from': 'rev/min',   'to': 'rad/s', 'expected': math.pi/30},
        ]

        for case in test_cases:
            quantity       = case['quantity']
            from_unit      = case['from']
            to_unit        = case['to']
            expected_value = case['expected']

            unit_conversion \
                = f'{quantity} {from_unit} --> {expected_value} {to_unit}'

            with self.subTest(case=unit_conversion):
                self.assertAlmostEqual(
                    MahaMulticsUnitConverter().convert(quantity=quantity,
                        from_unit=from_unit, to_unit=to_unit),
                    expected_value,
                    places=TEST_FLOAT_TOLERANCE_DECIMAL_PLACES
                )
