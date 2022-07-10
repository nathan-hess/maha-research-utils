import unittest

from mahautils.utils.parentheses import (
    check_matched_parentheses,
    find_matching_parenthesis,
    find_skip_parentheses,
    strip_parentheses,
)


class Test_CheckMatchedParentheses(unittest.TestCase):
    def test_matched(self):
        # Verifies that strings with matching parentheses are correctly
        # identified
        self.assertTrue(check_matched_parentheses('(())() variables ((())())'))
        self.assertTrue(check_matched_parentheses(''))
        self.assertTrue(check_matched_parentheses('()'))
        self.assertTrue(check_matched_parentheses('(      )'))

    def test_unmatched_count(self):
        # Verifies that strings with differing numbers of opening and closing
        # parentheses are identified as not having matching parentheses
        self.assertFalse(check_matched_parentheses('((  )()'))
        self.assertFalse(check_matched_parentheses('((  (()'))

    def test_unmatched_order(self):
        # Verifies that strings with equal numbers of opening and closing
        # parentheses but in which each opening parenthesis does not correspond
        # to a closing parenthesis *later in the string* are identified as
        # not having matching parentheses
        self.assertFalse(check_matched_parentheses('()(()))(()'))
        self.assertFalse(check_matched_parentheses(')(()'))
        self.assertFalse(check_matched_parentheses(')('))


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


class Test_FindSkipParentheses(unittest.TestCase):
    def test_invalid_direction(self):
        # Verifies that an error is thrown if "direction" argument is not valid
        with self.assertRaises(ValueError):
            find_skip_parentheses('abcd', 'd', 0, 'invalid_direction')

    def test_invalid_search_string(self):
        # Verifies that an error is thrown if "value" argument is not a string
        with self.assertRaises(TypeError):
            find_skip_parentheses(100, 'd', 0, 'invalid_direction')

    def test_invalid_begin_index(self):
        # Verifies that an error is thrown if "begin" argument is not a valid
        # index within the length of the string
        with self.assertRaises(IndexError):
            find_skip_parentheses('abcd', 'd', -5)

        with self.assertRaises(IndexError):
            find_skip_parentheses('abcd', 'd', 4)

    def test_no_parentheses(self):
        # Verifies that correct index is found in strings with no parentheses
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'a', 0), 0)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'a', 1), 7)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'acf', 1), 2)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'g', 0), -1)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'f', 7), -1)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('a',), 0), 0)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('a', 'c'), 1), 2)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('g', 'h'), 1), -1)

        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'a', 4, 'reverse'), 0)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'a', -2, 'reverse'), 11)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'acf', 6, 'reverse'), 5)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'g', -1, 'reverse'), -1)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', 'f', 4, 'reverse'), -1)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('a',), 4, 'reverse'), 0)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('a', 'c'), 5, 'reverse'), 2)
        self.assertEqual(find_skip_parentheses('abcdef1a234a5', ('g', 'h'), 5, 'reverse'), -1)

    def test_begin_outside_parentheses(self):
        # Verifies that correct index is found in strings with parentheses, beginning
        # the search outside the parentheses
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'a', 0), 0)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'a', 1), 19)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'a1', 1), 18)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'c', 16), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'a5', -3), 21)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('a',), 1), 19)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('a', '1'), 1), 18)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('c',), 16), -1)

        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'b', 1, 'reverse'), 1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'b', 19, 'reverse'), 1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', 'bc', 19, 'reverse'), 2)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', '5', 19, 'reverse'), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('b',), 19, 'reverse'), 1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('b', 'c'), 19, 'reverse'), 2)
        self.assertEqual(find_skip_parentheses('abc (deabfef(e)f) 1a2a5', ('5',), 19, 'reverse'), -1)

    def test_begin_inside_parentheses(self):
        # Verifies that correct index is found in strings with parentheses, beginning
        # the search inside the parentheses
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'a', 5), 7)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'b', 9), 17)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'e', 11), 18)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'be', 11), 17)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'q', 6), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'qv', 12), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'qv', 13), 14)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'bqv', -16), 17)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('e',), 11), 18)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('b', 'e'), 11), 17)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('q',), 6), -1)

        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'b', 18, 'reverse'), 17)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'b', 16, 'reverse'), 8)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'e', 17, 'reverse'), 10)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'cd', 17, 'reverse'), 5)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'q', 17, 'reverse'), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'qv', 17, 'reverse'), -1)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'ev', 14, 'reverse'), 13)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', 'ade', -9, 'reverse'), 10)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('e',), 17, 'reverse'), 10)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('c', 'd'), 17, 'reverse'), 5)
        self.assertEqual(find_skip_parentheses('abc (deabfef(eq)fbe) 1a2a5', ('q',), 17, 'reverse'), -1)


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
            '( text)  )'
        )
        self.assertEqual(
            strip_parentheses('( (text)  )'),
            'text'
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))'),
            '( (((() text)  ))))'
        )
        self.assertEqual(
            strip_parentheses('( ((() text)  ))) ( )) '),
            '( ((() text)  ))) ( ))'
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
            '( text)  )'
        )
        self.assertEqual(
            strip_parentheses('( (text)  )', strip=False),
            ' (text)  '
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))', strip=False),
            '( (((() text)  ))))'
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
            '( text)  )'
        )
        self.assertEqual(
            strip_parentheses('( (text)  )', max_pairs=1),
            '(text)'
        )
        self.assertEqual(
            strip_parentheses('( (((() text)  ))))', max_pairs=3),
            '( (((() text)  ))))'
        )
        self.assertEqual(
            strip_parentheses('( ((() text)  ))) ( )) ', max_pairs=1),
            '( ((() text)  ))) ( ))'
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
            ('( text)  )', 0)
        )
        self.assertTupleEqual(
            strip_parentheses('( (text)  )', return_num_pairs_removed=True),
            ('text', 2)
        )
        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ))))', return_num_pairs_removed=True),
            ('( (((() text)  ))))', 0)
        )
        self.assertTupleEqual(
            strip_parentheses('( ((() text)  ))) ( )) ', return_num_pairs_removed=True),
            ('( ((() text)  ))) ( ))', 0)
        )

        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ()() )))', return_num_pairs_removed=True),
            ('(() text)  ()()', 3)
        )

        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ))))', max_pairs=3, return_num_pairs_removed=True),
            ('( (((() text)  ))))', 0)
        )
        self.assertTupleEqual(
            strip_parentheses('( (((() text)  ()() )))', max_pairs=2, return_num_pairs_removed=True),
            ('((() text)  ()() )', 2)
        )
