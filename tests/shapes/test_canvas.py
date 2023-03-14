import unittest

from mahautils.shapes import Canvas, Layer
from mahautils.shapes.geometry import Shape2D


class Test_Canvas(unittest.TestCase):
    def setUp(self):
        self.idx0 = Canvas().id + 1

    def test_name_user(self):
        # Verifies that user-defined "name" attribute is set
        # and retrieved correctly
        with self.subTest(type='str'):
            self.assertEqual(Canvas(name='myCanvas').name, 'myCanvas')

        with self.subTest(type='int'):
            self.assertEqual(Canvas(name=1234).name, '1234')

    def test_name_automatic(self):
        # Verifies that automatically-selected "name" attribute
        # is set and retrieved correctly
        canvas1 = Canvas()
        self.assertEqual(canvas1.name, f'canvas{self.idx0}')
        self.assertEqual(canvas1.name, f'canvas{canvas1.id}')

        canvas2 = Canvas()
        self.assertEqual(canvas2.name, f'canvas{self.idx0 + 1}')
        self.assertEqual(canvas2.name, f'canvas{canvas2.id}')

    def test_add_layers(self):
        # Verifies that layers can be added to a canvas as expected
        with self.subTest(comment='same_class'):
            with self.subTest(method='constructor'):
                canvas1 = Canvas(
                    Layer(name='testLayer1'),
                    Layer(name='testLayer2'),
                    Layer(name='testLayer3')
                )
                self.assertEqual(len(canvas1), 3)

                for i in range(3):
                    self.assertEqual(canvas1[i].name, f'testLayer{i+1}')

            with self.subTest(method='append'):
                canvas2 = Canvas()
                canvas2.append(Layer(name='test_layer_2'))
                canvas2.append(Layer(name='test_layer_3'))
                canvas2.insert(0, Layer(name='test_layer_1'))
                canvas2.extend([Layer(name='test_layer_4')])

                self.assertEqual(len(canvas2), 4)

                for i in range(4):
                    self.assertEqual(canvas2[i].name, f'test_layer_{i+1}')

    def test_add_layers_invalid(self):
        # Verifies that canvas restricts layer type appropriately
        with self.assertRaises(TypeError):
            canvas = Canvas(Layer())
            canvas.append([Shape2D(), Shape2D()])

    def test_num_layers(self):
        # Verifies that number of layers in a canvas is computed accurately
        with self.subTest(num_shapes=0):
            self.assertEqual(Canvas().num_layers, 0)

        with self.subTest(num_shapes=1):
            self.assertEqual(Canvas(Layer()).num_layers, 1)

        with self.subTest(num_shapes=2):
            self.assertEqual(Canvas(Layer(), Layer()).num_layers, 2)
