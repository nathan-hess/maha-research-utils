import copy
import unittest

from mahautils.utils import Dictionary


class Test_Dictionary(unittest.TestCase):
    pass


class Test_Dictionary_General(Test_Dictionary):
    def test_dict_methods(self):
        # Verify that methods for built-in Python dictionaries work
        # for MahaUtils `Dictionary` objects
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

    def test_getitem(self):
        # Verify that custom exceptions are thrown if specified
        with self.subTest(exception='default'):
            with self.assertRaises(KeyError):
                Dictionary()['nonexistent_key']

        with self.subTest(exception='custom'):
            with self.assertRaises(ValueError):
                Dictionary(custom_except_class=ValueError)['nonexistent_key']

    def test_initialize_content(self):
        # Verify that dictionary content is initialized correctly
        dictionary = Dictionary({'key1': 'value1', 'key2': 6.28})
        self.assertDictEqual(dictionary, {'key1': 'value1', 'key2': 6.28})


class Test_Dictionary_Print(Test_Dictionary):
    def test_dictionary_str(self):
        # Verify that dictionary can be converted to a string
        # representation correctly
        dictionary = Dictionary({'key1': 'value1', 'key24': 6.28})

        with self.subTest(format='str'):
            self.assertEqual(
                str(dictionary),
                "Dictionary([('key1', 'value1'), ('key24', 6.28)])"
            )

        with self.subTest(format='__repr__'):
            self.assertEqual(
                dictionary.__repr__(),
                "Dictionary([('key1', 'value1'), ('key24', 6.28)])"
            )

    def test_dictionary_multiline(self):
        # Verifies tha the "multiline_print" attribute can be set correctly
        with self.subTest(method='constructor'):
            self.assertTrue(Dictionary(multiline_print=True).multiline_print)
            self.assertFalse(Dictionary(multiline_print=False).multiline_print)

        with self.subTest(method='property'):
            dictionary = Dictionary()

            dictionary.multiline_print = True
            self.assertTrue(dictionary.multiline_print)

            dictionary.multiline_print = False
            self.assertFalse(dictionary.multiline_print)

        with self.subTest(method='default'):
            self.assertFalse(Dictionary().multiline_print)

    def test_dictionary_multiline_str(self):
        # Verify that dictionary can be converted to a string
        # representation correctly
        dictionary = Dictionary({'key1': 'value1', 'key24': 6.28}, multiline_print=True)

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

    def test_dictionary_multiline_str_empty(self):
        # Verify that dictionary can be converted to a string
        # representation correctly when dictionary contains no content
        dictionary = Dictionary(multiline_print=True)

        with self.subTest(format='str'):
            self.assertEqual(str(dictionary), '')

        with self.subTest(format='__repr__'):
            self.assertEqual(dictionary.__repr__(), '')

    def test_dictionary_multiline_indent(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default indentation
        with self.subTest(indent=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_indent=3,
                multiline_print=True,
            )

            self.assertEqual(
                str(dictionary1),
                ('   key1  :  value1\n'
                 '   key24 :  6.28')
            )

        with self.subTest(indent=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28}, multiline_print=True)
            dictionary2.str_indent = 9

            self.assertEqual(
                str(dictionary2),
                ('         key1  :  value1\n'
                 '         key24 :  6.28')
            )

    def test_dictionary_multiline_pad_left(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default left padding
        with self.subTest(str_pad_left=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_pad_left=3,
                multiline_print=True,
            )

            self.assertEqual(
                str(dictionary1),
                ('key1    :  value1\n'
                 'key24   :  6.28')
            )

        with self.subTest(str_pad_left=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28}, multiline_print=True)
            dictionary2.str_pad_left = 9

            self.assertEqual(
                str(dictionary2),
                ('key1          :  value1\n'
                 'key24         :  6.28')
            )

    def test_dictionary_multiline_pad_right(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default right padding
        with self.subTest(str_pad_right=3, method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_pad_right=3,
                multiline_print=True,
            )

            self.assertEqual(
                str(dictionary1),
                ('key1  :   value1\n'
                 'key24 :   6.28')
            )

        with self.subTest(str_pad_right=9, method='properties'):
            dictionary2 = Dictionary({'key1': 'value1', 'key24': 6.28}, multiline_print=True)
            dictionary2.str_pad_right = 9

            self.assertEqual(
                str(dictionary2),
                ('key1  :         value1\n'
                 'key24 :         6.28')
            )

    def test_dictionary_multiline_custom_format(self):
        # Verify that dictionary can be converted to a string
        # representation correctly with non-default formatting
        with self.subTest(method='arguments'):
            dictionary1 = Dictionary(
                {'key1': 'value1', 'key24': 6.28},
                str_indent=3, str_pad_left=0, str_pad_right=4,
                multiline_print=True,
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
            dictionary2.multiline_print = True

            self.assertEqual(
                str(dictionary2),
                ('   key1 :    value1\n'
                 '   key24:    6.28')
            )


class Test_Dictionary_Exceptions(Test_Dictionary):
    def test_set_custom_except_class_invalid(self):
        # Verifies that custom exception classes have to be subclasses of
        # `Exception`
        with self.assertRaises(TypeError):
            Dictionary(custom_except_class=str)

    def test_set_custom_except_message(self):
        # Verifies that custom exception messages have to be formatted
        # correctly
        for message in ('key "%s" error', '%skey error', 'key error%s'):
            with self.subTest(message=message):
                Dictionary(custom_except_msg=message)

        for message in ('message', 'key "%s" not found %s'):
            with self.subTest(message=message):
                with self.assertRaises(ValueError):
                    Dictionary(custom_except_msg=message)


class Test_Dictionary_Index(Test_Dictionary):
    def setUp(self) -> None:
        super().setUp()

        self.items = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5}
        self.dictionary = Dictionary(self.items)

    def test_index(self):
        # Verifies that dictionary item indices can be retrieved correctly
        for key, index in self.items.items():
            with self.subTest(key=key):
                self.assertEqual(self.dictionary.index(key), index)

    def test_index_invalid(self):
        # Verifies that an appropriate error is thrown if attempting to find
        # the index of a key not present in the dictionary
        with self.assertRaises(KeyError):
            self.dictionary.index('nonexistent_key')


class Test_Dictionary_Delete(Test_Dictionary):
    def setUp(self) -> None:
        super().setUp()

        self.dictionary = Dictionary({'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

    def test_delete_key(self):
        # Verifies that items can be removed from the dictionary by key
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        del self.dictionary['b']
        del self.dictionary['f']

        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'c': 3, 'd': 4, 'e': 5})

    def test_delete_index(self):
        # Verifies that items can be removed from the dictionary by index
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        self.dictionary.delete_index(3)
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'c': 3, 'e': 5, 'f': 6})

        self.dictionary.delete_index(4)
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'c': 3, 'e': 5})

        self.dictionary.delete_index(-2)
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'e': 5})


class Test_Dictionary_Insert(Test_Dictionary):
    def setUp(self) -> None:
        super().setUp()

        self.dictionary = Dictionary({'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

    def test_insert(self):
        # Verifies that an item can be inserted at a given point in the dictionary
        with self.subTest(index=-2):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(-2, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'z': 3.14, 'f': 6})

        with self.subTest(index=-1):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(-1, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'z': 3.14})

        with self.subTest(index=0):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(0, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'z': 3.14, 'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        with self.subTest(index=1):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(1, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'z': 3.14, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        with self.subTest(index=2):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(2, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'z': 3.14, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        with self.subTest(index=3):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(3, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'z': 3.14, 'd': 4, 'e': 5, 'f': 6})

        with self.subTest(index=4):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(4, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'z': 3.14, 'e': 5, 'f': 6})

        with self.subTest(index=5):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(5, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'z': 3.14, 'f': 6})

        with self.subTest(index=6):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(6, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'z': 3.14})

        with self.subTest(index=7):
            dictionary = copy.deepcopy(self.dictionary)
            dictionary.insert(7, 'z', 3.14)
            self.assertDictEqual(
                dictionary,
                {'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'z': 3.14})

    def test_insert_after(self):
        # Verifies that an item can be inserted at a given point in the dictionary
        self.dictionary.insert_after('c', 'z', 3.14)
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'c': 3, 'z': 3.14, 'd': 4, 'e': 5, 'f': 6})

    def test_insert_before(self):
        # Verifies that an item can be inserted at a given point in the dictionary
        self.dictionary.insert_before('c', 'z', 3.14)
        self.assertDictEqual(
            self.dictionary,
            {'a': 0, 'b': 1, 'z': 3.14, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

    def test_invalid_overwrite(self):
        # Verifies that an error is thrown if attempting to overwrite an item
        # in the dictionary
        for method in ('insert', 'insert_after', 'insert_before'):
            with self.subTest(method=method):
                with self.assertRaises(KeyError):
                    getattr(self.dictionary, method)(0, 'c', 3.14)
