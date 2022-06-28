import unittest

from mahautils.utils.vartools import (
    convert_to_tuple,
    max_list_item_len,
)


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


class Test_MaxListLength(unittest.TestCase):
    def test_string_list(self):
        # Verifies that the maximum length of a list of strings
        # is correctly identified
        self.assertEqual(
            max_list_item_len(['item1', 'phrase with spaces', 'newline\n', '']), 18)

        self.assertEqual(max_list_item_len(['', '', '', '', '']), 0)

    def test_mixed_list(self):
        # Verifies that the maximum length of a list of mixed types
        # is correctly identified
        self.assertEqual(
            max_list_item_len(['item1', [1, 2, 0], (int, dict), '']), 5)

        self.assertEqual(
            max_list_item_len(['m1', [1, 2, 0], (int, dict), '']), 3)

    def test_max_length_tuple(self):
        # Verifies that the maximum length of items in a tuple is
        # correctly identified
        self.assertEqual(
            max_list_item_len(('item1', 'phrase with spaces', 'newline\n', '')), 18)

        self.assertEqual(
            max_list_item_len(('m1', [1, 2, 0], (int, dict), '')), 3)

    def test_invalid_object_list(self):
        # Verifies that an error is thrown if attempting to determine the
        # maximum length of a list with types whose lengths are not defined
        with self.assertRaises(TypeError):
            max_list_item_len([2, 'string'])
