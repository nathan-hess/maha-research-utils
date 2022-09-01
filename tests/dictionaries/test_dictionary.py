import unittest

from mahautils.dictionaries import Dictionary


class Test_Dictionary(unittest.TestCase):
    def test_dict_methods(self):
        # Verify that methods for built-in Python dictionaries work
        # for `mahautils.dictionaries.Dictionary` object
        dictionary = Dictionary()
        self.assertDictEqual(dictionary, {})

        with self.subTest(action='setitem'):
            dictionary['key'] = 2.72
            dictionary['string'] = 'str'
            self.assertDictEqual(dictionary, {'key': 2.72, 'string': 'str'})

        with self.subTest(action='keys'):
            self.assertListEqual(list(dictionary.keys()), ['key', 'string'])

        with self.subTest(action='pop'):
            self.assertEqual(dictionary.pop('string'), 'str')
            self.assertDictEqual(dictionary, {'key': 2.72})

    def test_initialize_content(self):
        # Verify that dictionary content is initialized correctly
        dictionary = Dictionary({'key1': 'value1', 'key2': 6.28})
        self.assertDictEqual(dictionary, {'key1': 'value1', 'key2': 6.28})

    def test_dictionary_str(self):
        # Verify that dictionary can be converted to a string
        # representation correctly
        dictionary = Dictionary({'key1': 'value1', 'key24': 6.28})

        with self.subTest(format='str'):
            self.assertEqual(
                str(dictionary),
                ('key1  :  value1\n'
                 'key24 :  6.28')
            )

        with self.subTest(format='__repr__'):
            self.assertEqual(
                dictionary.__repr__(),
                ('key1  :  value1\n'
                 'key24 :  6.28')
            )

    def test_dictionary_indent(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default indentation
        with self.subTest(indent=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_indent=3
            )

            self.assertEqual(
                str(dictionary1),
                ('   key1  :  value1\n'
                 '   key24 :  6.28')
            )

        with self.subTest(indent=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28})
            dictionary2.str_indent = 9

            self.assertEqual(
                str(dictionary2),
                ('         key1  :  value1\n'
                 '         key24 :  6.28')
            )

    def test_dictionary_pad_left(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default left padding
        with self.subTest(str_pad_left=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_pad_left=3
            )

            self.assertEqual(
                str(dictionary1),
                ('key1    :  value1\n'
                 'key24   :  6.28')
            )

        with self.subTest(str_pad_left=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28})
            dictionary2.str_pad_left = 9

            self.assertEqual(
                str(dictionary2),
                ('key1          :  value1\n'
                 'key24         :  6.28')
            )

    def test_dictionary_pad_right(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default right padding
        with self.subTest(str_pad_right=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_pad_right=3
            )

            self.assertEqual(
                str(dictionary1),
                ('key1  :   value1\n'
                 'key24 :   6.28')
            )

        with self.subTest(str_pad_right=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28})
            dictionary2.str_pad_right = 9

            self.assertEqual(
                str(dictionary2),
                ('key1  :         value1\n'
                 'key24 :         6.28')
            )

    def test_dictionary_custom_format(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default formatting
        with self.subTest(method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_indent=3, str_pad_left=0, str_pad_right=4
            )

            self.assertEqual(
                str(dictionary1),
                ('   key1 :    value1\n'
                 '   key24:    6.28')
            )

        with self.subTest(method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28})
            dictionary2.str_indent = 3
            dictionary2.str_pad_left = 0
            dictionary2.str_pad_right = 4

            self.assertEqual(
                str(dictionary2),
                ('   key1 :    value1\n'
                 '   key24:    6.28')
            )
