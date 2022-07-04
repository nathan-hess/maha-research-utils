import unittest

from mahautils.utils.stringtools import strip_parentheses


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
