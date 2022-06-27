import unittest

from mahautils.utils.vartools import convert_to_tuple


class Test_ConvertToTuple(unittest.TestCase):
    def test_pass_through_tuple(self):
        # Verify that existing tuples are returned unaltered
        self.assertTupleEqual(
            convert_to_tuple(('value1',)),
            ('value1',)
        )

        self.assertTupleEqual(
            convert_to_tuple(('value1', 3.4, print)),
            ('value1', 3.4, print)
        )

    def test_convert_single_to_tuple(self):
        # Verify that inputs that are not already tuples are
        # correctly converted to tuples
        self.assertTupleEqual(
            convert_to_tuple('value1'),
            ('value1',)
        )

        self.assertTupleEqual(
            convert_to_tuple(('value1')),
            ('value1',)
        )

        self.assertTupleEqual(
            convert_to_tuple(93232),
            (93232,)
        )

        self.assertTupleEqual(
            convert_to_tuple(print),
            (print,)
        )
