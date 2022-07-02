import unittest

from mahautils.utils.vartools import (
    convert_to_tuple,
    max_list_item_len,
    check_len_equal,
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


class Test_CheckLenEqual(unittest.TestCase):
    def test_check_2_list_equal(self):
        # Verifies that lengths of two lists are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(['a', 'b', 'c'], [1, 2, 3]),
            (True, 3)
        )
        self.assertTupleEqual(check_len_equal(['a'], [1]), (True, 1))

    def test_check_3_list_equal(self):
        # Verifies that lengths of three lists are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(['a', 'b'], [1, 2], ['cd', 3]),
            (True, 2)
        )
        self.assertTupleEqual(check_len_equal(['a'], [1], ['c']), (True, 1))

    def test_check_4_list_equal(self):
        # Verifies that lengths of four lists are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(['a', 'b'], [1, 2], ['cd', 3], [None, None]),
            (True, 2)
        )
        self.assertTupleEqual(check_len_equal(['a'], [1], ['c'], [None]), (True, 1))

    def test_check_2_tuple_equal(self):
        # Verifies that lengths of two tuples are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(('a', 'b', 'c'), (1, 2, 3)),
            (True, 3)
        )
        self.assertTupleEqual(check_len_equal(('a',), (1,)), (True, 1))

    def test_check_3_tuple_equal(self):
        # Verifies that lengths of three tuples are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(('a', 'b'), (1, 2), ('cd', 3)),
            (True, 2)
        )
        self.assertTupleEqual(check_len_equal(('a',), (1,), ('cd',)), (True, 1))

    def test_check_4_tuple_equal(self):
        # Verifies that lengths of four tuples are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(('a', 'b'), (1, 2), ('cd', 3), (None, None)),
            (True, 2)
        )
        self.assertTupleEqual(check_len_equal(('a',), (1,), ('cd',), (None,)), (True, 1))

    def test_check_2_str_equal(self):
        # Verifies that lengths of two strings are evaluated correctly
        self.assertTupleEqual(
            check_len_equal('abc', '123'),
            (True, 3)
        )

    def test_check_3_str_equal(self):
        # Verifies that lengths of three strings are evaluated correctly
        self.assertTupleEqual(
            check_len_equal('ab', '12', 'c3'),
            (True, 2)
        )

    def test_check_4_str_equal(self):
        # Verifies that lengths of four strings are evaluated correctly
        self.assertTupleEqual(
            check_len_equal('ab', '12', 'c3', 'No'),
            (True, 2)
        )

    def test_check_mixed_type_equal(self):
        # Verifies that lengths of mixed list/tuple/string arguments
        # are evaluated correctly
        self.assertTupleEqual(
            check_len_equal(['a', 'b'], (1, 2), ('cd', 3), (None, None), 'ce'),
            (True, 2)
        )
        self.assertTupleEqual(check_len_equal(('a',), (1,), ('cd',), (None,), 'c'), (True, 1))

    def test_check_2_mixed_type_unequal(self):
        # Verifies that lengths of 2 mixed list/tuple/string arguments with
        # different lengths are compared correctly
        self.assertTupleEqual(
            check_len_equal((1, 2), 'abcdefjkl'),
            (False, [2, 9])
        )

    def test_check_3_mixed_type_unequal(self):
        # Verifies that lengths of 3 mixed list/tuple/string arguments with
        # different lengths are compared correctly
        self.assertTupleEqual(
            check_len_equal(('cd', 3), (None, None), 'abcdefjkl'),
            (False, [2, 2, 9])
        )

    def test_check_5_mixed_type_unequal(self):
        # Verifies that lengths of 5 mixed list/tuple/string arguments with
        # different lengths are compared correctly
        self.assertTupleEqual(
            check_len_equal(['a', 'b', 'c'], (1, 2), ('cd', 3), (None, None), 'abcdefjkl'),
            (False, [3, 2, 2, 2, 9])
        )
