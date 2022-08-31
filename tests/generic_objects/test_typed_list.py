import copy
import unittest

from mahautils.generic_objects import TypedList


class Test_TypedList(unittest.TestCase):
    def setUp(self):
        # Define a set of data types to test
        self.test_types = (int, float, str, type, list)

        # Provide sample data for each data type
        self.test_lists_data = {
            int: (2, 5, -25, 94, 0, 1, 5, -4),
            float: (4.2, 1.0, 0.0, -4.2, -2e5, 3e-4, 0.0, 3000.0),
            str: ('ab', 'cde', '323.4', '3', '', '\n', '   ', '#@'),
            type: (int, float, dict, dict, type, str, tuple, list),
            list: ([2, 4, 3.4], ['a', 'b', 'c'], [], [(1,)], ['ab', list],
                   [[]], [3.44, 2.1], [4, 'abc']),
        }

        self.test_type_samples = {
            int: 5,
            float: 5.2504923,
            str: 'zyxw',
            type: list,
            list: [5, list],
        }

        self.test_type_slices = {
            int: [0, -5],
            float: [-4.3, 0.0001],
            str: ['', 'qrst'],
            type: [tuple, list],
            list: [[545.2, type], []],
        }

        # Set up and populate items in `TypedList` objects
        self.test_lists = {
            dtype: TypedList(list_type=dtype) for dtype in self.test_types
        }

        for dtype in self.test_types:
            self.test_lists[dtype]._data \
                = list(copy.deepcopy(self.test_lists_data[dtype]))

    def test_list_type_property(self):
        # Verifies that `list_type` attribute is set correctly
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):

                # Check that list type is set correctly and can be accessed
                # with the `list_type` property
                typed_list = TypedList(list_type=dtype)
                self.assertIs(typed_list.list_type, dtype)

                # Check that the list type can't be modified
                with self.assertRaises(AttributeError):
                    typed_list.list_type = dict

                with self.assertRaises(AttributeError):
                    typed_list.list_type = dtype

    def test_delitem_single(self):
        # Verifies that a single item can be deleted from the list
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):

                del self.test_lists[dtype][1]
                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [self.test_lists_data[dtype][0], *self.test_lists_data[dtype][2:]]
                )

    def test_delitem_multiple(self):
        # Verifies that a slice of items can be deleted from the list
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):

                del self.test_lists[dtype][1:4]
                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [self.test_lists_data[dtype][0], *self.test_lists_data[dtype][4:]]
                )

    def test_equality(self):
        # Checks equality between two `TypedList` objects
        with self.subTest(type='int'):
            list1 = TypedList(list_type=int)
            list1._data = [1, 92, 3, 4, 5, -30]

            list2 = TypedList(list_type=int)
            list2._data = [1, 92, 3, 4, 5, -30]

            self.assertEqual(list1, list2)

        with self.subTest(type='float'):
            list3 = TypedList(list_type=float)
            list3._data = [1.23, -0.4, 0.00, 1e-14, 2e9]

            list4 = TypedList(list_type=float)
            list4._data = [1.23, -0.4, 0.00, 1e-14, 2e9]

            self.assertEqual(list3, list4)

        with self.subTest(type='str'):
            list5 = TypedList(list_type=str)
            list5._data = ['abc', 'de', '12']

            list6 = TypedList(list_type=str)
            list6._data = ['abc', 'de', '12']

            self.assertEqual(list5, list6)

        with self.subTest(type='empty'):
            list7 = TypedList(list_type=float)
            list8 = TypedList(list_type=float)

            self.assertEqual(list7, list8)

    def test_inequality(self):
        # Checks inequality between two `TypedList` objects
        with self.subTest(type='different_type'):
            list1 = TypedList(list_type=int)
            list2 = TypedList(list_type=float)

            self.assertNotEqual(list1, list2)

        with self.subTest(type='different_length'):
            list3 = TypedList(list_type=int)
            list3._data = [1, 92, 3, 4, 5, -30]

            list4 = TypedList(list_type=int)
            list4._data = [1, 92, 3, 4, 5]

            self.assertNotEqual(list3, list4)

        
        with self.subTest(type='different_values'):
            list5 = TypedList(list_type=int)
            list5._data = [1, 92, 3, 4, 5, -30]

            list6 = TypedList(list_type=int)
            list6._data = [1, 92, 2, 4, 5, -30]

            self.assertNotEqual(list5, list6)

    def test_getitem_single(self):
        # Verifies that individual items can be retrieved correctly
        for dtype in self.test_types:
            for i in range(8):
                with self.subTest(type=str(dtype), index=i):
                    self.assertEqual(
                        self.test_lists[dtype][i],
                        self.test_lists_data[dtype][i])

    def test_getitem_multiple(self):
        # Verifies that multiple items can be retrieved correctly
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.assertListEqual(
                    self.test_lists[dtype][3:7],
                    list(self.test_lists_data[dtype][3:7]))

    def test_len(self):
        # Verifies that `TypedList` length is determined correctly
        with self.subTest(length=0):
            self.assertEqual(len(TypedList(list_type=int)), 0)

        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.assertEqual(len(self.test_lists[dtype]), 8)

    def test_setitem_single_index0(self):
        # Verifies that a single item can set at index 0
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.test_lists[dtype][0] = self.test_type_samples[dtype]

                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [
                        self.test_type_samples[dtype],
                        *self.test_lists_data[dtype][1:],
                    ]
                )

    def test_setitem_single_index2(self):
        # Verifies that a single item can set at index 2
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.test_lists[dtype][2] = self.test_type_samples[dtype]

                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [
                        self.test_lists_data[dtype][0],
                        self.test_lists_data[dtype][1],
                        self.test_type_samples[dtype],
                        *self.test_lists_data[dtype][3:],
                    ]
                )

    def test_setitem_single_index_n1(self):
        # Verifies that a single item can set at index -1
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.test_lists[dtype][-1] = self.test_type_samples[dtype]

                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [
                        *self.test_lists_data[dtype][0:7],
                        self.test_type_samples[dtype],
                    ]
                )

    def test_setitem_slice(self):
        # Verifies that a multiple items can set at a given slice
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.test_lists[dtype][2:5] = self.test_type_slices[dtype]

                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [
                        self.test_lists_data[dtype][0],
                        self.test_lists_data[dtype][1],
                        *self.test_type_slices[dtype],
                        *self.test_lists_data[dtype][5:],
                    ]
                )

    def test_setitem_invalid_type(self):
        # Verifies that an error is thrown if attempting to assign an item
        # that doesn't have expected type
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                with self.assertRaises(TypeError):
                    self.test_lists[dtype][0] = {'key': 1234}

    def test_setitem_invalid_index_value(self):
        # Verifies that an error is thrown if attempting to assign a
        # non-iterable item with slice notation
        test_list = TypedList(list_type=float)

        with self.subTest(type='invalid_index_type'):
            with self.assertRaises(TypeError):
                test_list[float] = 4.3

        with self.subTest(type='non_iterable'):
            with self.assertRaises(TypeError):
                test_list[2:4] = 4.3

    def test_str_repr(self):
        # Verifies that printable string representation of object is
        # constructed correctly
        str_rep = {
            int: '\n'.join(('[ 2,',
                            '  5,',
                            '  -25,',
                            '  94,',
                            '  0,',
                            '  1,',
                            '  5,',
                            '  -4,  ]')),
            float: '\n'.join(('[ 4.2,',
                              '  1.0,',
                              '  0.0,',
                              '  -4.2,',
                              '  -200000.0,',
                              '  0.0003,',
                              '  0.0,',
                              '  3000.0,    ]')),
            str: '\n'.join(('[ ab,',
                            '  cde,',
                            '  323.4,',
                            '  3,',
                            '  ,',
                            '  \n  ,',
                            '     ,',
                            '  #@,    ]')),
            type:'\n'.join(("[ <class 'int'>,",
                            "  <class 'float'>,",
                            "  <class 'dict'>,",
                            "  <class 'dict'>,",
                            "  <class 'type'>,",
                            "  <class 'str'>,",
                            "  <class 'tuple'>,",
                            "  <class 'list'>,  ]")),
            list: '\n'.join(("[ [2, 4, 3.4],",
                             "  ['a', 'b', 'c'],",
                             "  [],",
                             "  [(1,)],",
                             "  ['ab', <class 'list'>],",
                             "  [[]],",
                             "  [3.44, 2.1],",
                             "  [4, 'abc'],             ]")),
        }

        for dtype in self.test_types:
            with self.subTest(type=str(dtype), output='str'):
                self.assertEqual(str(self.test_lists[dtype]), str_rep[dtype])

            with self.subTest(type=str(dtype), output='repr'):
                self.assertEqual(self.test_lists[dtype].__repr__(), str_rep[dtype])

    def test_property_multiline(self):
        # Verifies that `print_multiline` property of `TypedList` objects
        # functions as expected
        typed_list = TypedList(list_type=float)
        typed_list._data = [3.445, 6, 'string', -0.5343]

        with self.subTest(print_multiline='True'):
            typed_list.print_multiline = True

            # Check that property is stored correctly
            self.assertTrue(typed_list.print_multiline)

            # Check that string representation is correct
            self.assertEqual(
                str(typed_list), '[ 3.445,\n  6,\n  string,\n  -0.5343, ]')
            self.assertEqual(
                typed_list.__repr__(), '[ 3.445,\n  6,\n  string,\n  -0.5343, ]')

        with self.subTest(print_multiline='False'):
            typed_list.print_multiline = False

            # Check that property is stored correctly
            self.assertFalse(typed_list.print_multiline)

            # Check that string representation is correct
            self.assertEqual(
                str(typed_list), "[3.445, 6, 'string', -0.5343]")
            self.assertEqual(
                typed_list.__repr__(), "[3.445, 6, 'string', -0.5343]")

    def test_multiline_pad(self):
        # Verifies that padding of multiline string representation is
        # displayed correctly
        typed_list = TypedList(list_type=float)
        typed_list._data = [3.445, 6, 'string', -0.5343]

        with self.subTest(padding=0):
            typed_list.multiline_padding = 0

            # Check that property is stored correctly
            self.assertEqual(typed_list.multiline_padding, 0)

            # Check that string representation is correct
            self.assertEqual(
                str(typed_list), '[3.445,\n 6,\n string,\n -0.5343,]')
            self.assertEqual(
                typed_list.__repr__(), '[3.445,\n 6,\n string,\n -0.5343,]')

        with self.subTest(padding=5):
            typed_list.multiline_padding = 5

            # Check that property is stored correctly
            self.assertEqual(typed_list.multiline_padding, 5)

            # Check that string representation is correct
            self.assertEqual(
                str(typed_list),
                '[     3.445,\n      6,\n      string,\n      -0.5343,     ]'
            )
            self.assertEqual(
                typed_list.__repr__(),
                '[     3.445,\n      6,\n      string,\n      -0.5343,     ]'
            )

    def test_invalid_multiline_property(self):
        # Verifies that an error is thrown if attempting to assign an
        # invalid value to the `print_multiline` property
        typed_list = TypedList(list_type=float)

        with self.assertRaises(TypeError):
            typed_list.print_multiline = 'true'

        with self.assertRaises(TypeError):
            typed_list.print_multiline = 0

    def test_invalid_multiline_padding(self):
        # Verifies that an error is thrown if attempting to assign an
        # invalid value to the `multiline_padding` property
        typed_list = TypedList(list_type=float)

        with self.assertRaises(TypeError):
            typed_list.multiline_padding = True

        with self.assertRaises(TypeError):
            typed_list.multiline_padding = 5.0

    def test_insert(self):
        # Verifies that an item can be inserted at a desired index
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                self.test_lists[dtype].insert(2, self.test_type_samples[dtype])

                self.assertListEqual(
                    self.test_lists[dtype]._data,
                    [
                        self.test_lists_data[dtype][0],
                        self.test_lists_data[dtype][1],
                        self.test_type_samples[dtype],
                        *self.test_lists_data[dtype][2:],
                    ]
                )

    def test_insert_invalid_type(self):
        # Verifies that an error is thrown if attempting to insert an item
        # that is not of the expected type
        for dtype in self.test_types:
            with self.subTest(type=str(dtype)):
                with self.assertRaises(TypeError):
                    self.test_lists[dtype].insert(0, {'key': 1234})
