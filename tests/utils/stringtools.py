import unittest

from mahautils.utils.stringtools import (
    find_matching_parenthesis,
    strip_parentheses,
)


class Test_FindMatchingParenthesis(unittest.TestCase):
    def test_find_index_forward(self):
        # Verify that matching parenthesis index is identified correctly
        # when searching in the forward direction
        self.assertEqual(find_matching_parenthesis('(  )', 0), 3)
        self.assertEqual(find_matching_parenthesis(' ()', 1), 2)
        self.assertEqual(find_matching_parenthesis('(()(()))  )', 0), 7)
        self.assertEqual(find_matching_parenthesis('(()(()))  )', 1), 2)

    def test_find_index_reverse(self):
        # Verify that matching parenthesis index is identified correctly
        # when searching in the reverse direction
        self.assertEqual(find_matching_parenthesis('(  )', 3), 0)
        self.assertEqual(find_matching_parenthesis(' ()', 2), 1)
        self.assertEqual(find_matching_parenthesis('(()(()))  )', 7), 0)
        self.assertEqual(find_matching_parenthesis('(()(()))  )', 2), 1)

    def test_find_negative_index(self):
        # Verify that matching parenthesis index is identified correctly
        # when providing a negative `begin` index
        self.assertEqual(find_matching_parenthesis('(  )', -1), 0)
        self.assertEqual(find_matching_parenthesis(' ()', -2), 2)
        self.assertEqual(find_matching_parenthesis('(()(()))  )', -5), 3)

    def test_find_no_match(self):
        # Verify that -1 is returned if there is no matching parenthesis
        self.assertEqual(find_matching_parenthesis('( ( ) ', 0), -1)
        self.assertEqual(find_matching_parenthesis('( ( ) ', -6), -1)
        self.assertEqual(find_matching_parenthesis('( ) ) ', 4), -1)
        self.assertEqual(find_matching_parenthesis('( ) ) ', -2), -1)

    def test_no_begin_parenthesis(self):
        # Verify that an error is thrown if the character at index
        # `begin` is not a parenthesis
        with self.assertRaises(ValueError):
            find_matching_parenthesis('( ( ) ', 1)

        with self.assertRaises(ValueError):
            find_matching_parenthesis('( ( ) ', -1)


class Test_StripParentheses(unittest.TestCase):
    def test_remove_parentheses(self):
        # Tests general cases of removing parentheses
        self.assertEqual(
            strip_parentheses('text with no parentheses'),
            'text with no parentheses'
        )
        self.assertEqual(
            strip_parentheses('text()'),
            'text()'
        )
        self.assertEqual(
            strip_parentheses('( text)  )'),
            'text)'
        )
        self.assertEqual(
            strip_parentheses('( (text)  )'),
            'text'
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))'),
            ') text'
        )
        self.assertEqual(
            strip_parentheses('( ((() text)  ))) ( )) '),
            '(() text)  ))) ('
        )

    def test_no_strip(self):
        # Tests removal of parentheses without stripping
        # leading/trailing whitespace
        self.assertEqual(
            strip_parentheses('text with no parentheses', strip=False),
            'text with no parentheses'
        )
        self.assertEqual(
            strip_parentheses('text()', strip=False),
            'text()'
        )
        self.assertEqual(
            strip_parentheses('( text)  )', strip=False),
            ' text)  '
        )
        self.assertEqual(
            strip_parentheses('( (text)  )', strip=False),
            ' (text)  '
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))', strip=False),
            ' (((() text)  )))'
        )
        self.assertEqual(
            strip_parentheses('( ((() text)  ))) ( )) ', strip=False),
            '( ((() text)  ))) ( )) '
        )

    def test_max_pairs(self):
        # Verifies that a given maximum number of pairs of parentheses
        # are removed
        self.assertEqual(
            strip_parentheses('text with no parentheses', max_pairs=2),
            'text with no parentheses'
        )
        self.assertEqual(
            strip_parentheses('text()', max_pairs=5),
            'text()'
        )
        self.assertEqual(
            strip_parentheses('( text)  )', max_pairs=1),
            'text)'
        )
        self.assertEqual(
            strip_parentheses('( (text)  )', max_pairs=1),
            '(text)'
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))', max_pairs=3),
            '(() text)  )'
        )
        self.assertEqual(
            strip_parentheses('( ((() text)  ))) ( )) ', max_pairs=1),
            '((() text)  ))) ( )'
        )

    def test_return_pairs(self):
        # Verifies that the number of parentheses removed is returned correctly
        self.assertTupleEqual(
            strip_parentheses('text with no parentheses', return_num_pairs_removed=True),
            ('text with no parentheses', 0)
        )
        self.assertTupleEqual(
            strip_parentheses('text()', return_num_pairs_removed=True),
            ('text()', 0)
        )
        self.assertTupleEqual(
            strip_parentheses('( text)  )', return_num_pairs_removed=True),
            ('text)', 1)
        )
        self.assertTupleEqual(
            strip_parentheses('( (text)  )', return_num_pairs_removed=True),
            ('text', 2)
        )
        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ))))', return_num_pairs_removed=True),
            (') text', 5)
        )
        self.assertTupleEqual(
            strip_parentheses('( ((() text)  ))) ( )) ', return_num_pairs_removed=True),
            ('(() text)  ))) (', 2)
        )

        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ))))', max_pairs=3, return_num_pairs_removed=True),
            ('(() text)  )', 3)
        )
