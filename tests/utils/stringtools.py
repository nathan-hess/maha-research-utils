import unittest

from mahautils.utils.stringtools import (
    split_at_index,
    str_excludes_chars,
)


class Test_SplitAtIndex(unittest.TestCase):
    def test_split_no_return_index(self):
        # Checks that format of returned tuple is correct when not returning
        # the character at position "index"
        self.assertTupleEqual(split_at_index('abcd', 0), ('', 'bcd'))
        self.assertTupleEqual(split_at_index('abcd', 1), ('a', 'cd'))
        self.assertTupleEqual(split_at_index('abcd', 2), ('ab', 'd'))
        self.assertTupleEqual(split_at_index('abcd', 3), ('abc', ''))

        self.assertTupleEqual(split_at_index('abcd', -4), ('', 'bcd'))
        self.assertTupleEqual(split_at_index('abcd', -3), ('a', 'cd'))
        self.assertTupleEqual(split_at_index('abcd', -2), ('ab', 'd'))
        self.assertTupleEqual(split_at_index('abcd', -1), ('abc', ''))

    def test_split_return_index(self):
        # Checks that format of returned tuple is correct when returning
        # the character at position "index"
        self.assertTupleEqual(split_at_index('abcd', 0, True), ('', 'a', 'bcd'))
        self.assertTupleEqual(split_at_index('abcd', 1, True), ('a', 'b', 'cd'))
        self.assertTupleEqual(split_at_index('abcd', 2, True), ('ab', 'c', 'd'))
        self.assertTupleEqual(split_at_index('abcd', 3, True), ('abc', 'd', ''))

        self.assertTupleEqual(split_at_index('abcd', -4, True), ('', 'a', 'bcd'))
        self.assertTupleEqual(split_at_index('abcd', -3, True), ('a', 'b', 'cd'))
        self.assertTupleEqual(split_at_index('abcd', -2, True), ('ab', 'c', 'd'))
        self.assertTupleEqual(split_at_index('abcd', -1, True), ('abc', 'd', ''))


class Test_StrExcludesChars(unittest.TestCase):
    def test_no_prohibited_chars(self):
        # Verifies that `True` is returned when no "prohibited" characters
        # are present
        self.assertTrue(str_excludes_chars('abcd12345*()', 'efg6'))
        self.assertTrue(str_excludes_chars('abcd12345*()', 'e'))

    def test_prohibited_chars(self):
        # Verifies that `False` is returned when "prohibited" characters
        # are present
        self.assertFalse(str_excludes_chars('abcd12345*()', 'def'))
        self.assertFalse(str_excludes_chars('abcd12345*()', '('))
