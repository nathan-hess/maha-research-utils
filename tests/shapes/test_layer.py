import unittest

import matplotlib.pyplot as plt
import pyxx

from mahautils.shapes import Layer
from mahautils.shapes.geometry import Circle, ClosedShape2D, Shape2D


class Test_Layer(unittest.TestCase):
    def setUp(self):
        self.idx0 = Layer().id + 1

        self.circle1 = Circle((0, 0), radius=2)
        self.circle2 = Circle((2, 4), radius=6)
        self.closed_shape = ClosedShape2D()

    def test_color_user(self):
        # Verifies that user-defined "color" attribute is set
        # and retrieved correctly
        with self.subTest(type='str'):
            self.assertEqual(Layer(color='red').color, 'red')

        with self.subTest(type='tuple'):
            self.assertTupleEqual(
                Layer(color=(1.0, 2.0, 3.0)).color,
                (1.0, 2.0, 3.0))

    def test_color_automatic(self):
        # Verifies that automatically-selected "color" attribute
        # is set and retrieved correctly
        matplotlib_colors: list = plt.rcParams['axes.prop_cycle'].by_key()['color']

        layer1_color_index = matplotlib_colors.index(Layer().color)
        layer2_color_index = matplotlib_colors.index(Layer().color)

        if layer2_color_index < layer1_color_index:
            layer2_color_index += len(matplotlib_colors)

        self.assertEqual(layer1_color_index + 1, layer2_color_index)

    def test_name_user(self):
        # Verifies that user-defined "name" attribute is set
        # and retrieved correctly
        with self.subTest(type='str'):
            self.assertEqual(Layer(name='myLayer').name, 'myLayer')

        with self.subTest(type='int'):
            self.assertEqual(Layer(name=1234).name, '1234')

    def test_name_automatic(self):
        # Verifies that automatically-selected "name" attribute
        # is set and retrieved correctly
        layer1 = Layer()
        self.assertEqual(layer1.name, f'layer{self.idx0}')
        self.assertEqual(layer1.name, f'layer{layer1.id}')

        layer2 = Layer()
        self.assertEqual(layer2.name, f'layer{self.idx0 + 1}')
        self.assertEqual(layer2.name, f'layer{layer2.id}')

    def test_add_shapes(self):
        # Verifies that shapes can be added to layer as expected
        with self.subTest(comment='different_classes'):
            with self.subTest(method='constructor'):
                layer1 = Layer(self.circle1, self.closed_shape)
                self.assertEqual(len(layer1), 2)

            with self.subTest(method='append'):
                layer2 = Layer()
                self.assertEqual(len(layer2), 0)

                layer2.append(self.circle1)
                self.assertEqual(len(layer2), 1)

                layer2.append(self.closed_shape)
                self.assertEqual(len(layer2), 2)

        circle_list = pyxx.arrays.TypedList(
            self.circle1, self.circle2, self.circle1,
            list_type=Shape2D
        )

        with self.subTest(comment='same_class'):
            with self.subTest(method='constructor'):
                layer3 = Layer(self.circle1, self.circle2, self.circle1)
                self.assertEqual(layer3, circle_list)

            with self.subTest(method='append'):
                layer4 = Layer()
                layer4.append(self.circle2)
                layer4.append(self.circle1)
                layer4.insert(0, self.circle1)

                self.assertEqual(layer4, circle_list)

    def test_add_shapes_invalid(self):
        # Verifies that layer restricts shape type appropriately
        with self.assertRaises(TypeError):
            layer = Layer(self.circle1, self.closed_shape)
            layer.append((0, 0))

    def test_num_shapes(self):
        # Verifies that number of shapes in layer is computed accurately
        with self.subTest(num_shapes=0):
            self.assertEqual(Layer().num_shapes, 0)

        with self.subTest(num_shapes=1):
            self.assertEqual(Layer(self.circle1).num_shapes, 1)

        with self.subTest(num_shapes=2):
            self.assertEqual(Layer(self.circle1, self.circle2).num_shapes, 2)
