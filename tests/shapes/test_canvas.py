import copy
import unittest
from unittest.mock import Mock

import plotly.graph_objects as go

from mahautils.shapes import Canvas, Layer
from mahautils.shapes.geometry import ClosedShape2D, Shape2D


class Test_Canvas(unittest.TestCase):
    def setUp(self):
        self.idx0 = Canvas().id + 1


class Test_Canvas_Properties(Test_Canvas):
    def setUp(self):
        super().setUp()

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


class Test_Canvas_Add(Test_Canvas):
    def setUp(self):
        super().setUp()

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


class Test_Canvas_Plot(Test_Canvas):
    def setUp(self):
        super().setUp()

        self.shape1 = ClosedShape2D(default_num_coordinates=100)
        self.shape1.xy_coordinates = Mock(return_value=([0, 1, 2], [3, 4, 5]))

        self.shape2 = copy.deepcopy(self.shape1)
        self.shape3 = copy.deepcopy(self.shape1)
        self.shape3.construction = True

        self.layer1 = Layer(self.shape1, self.shape2)
        self.layer2 = Layer(self.shape3)

        self.canvas = Canvas(self.layer1, self.layer2)

    def test_plot_new_figure(self):
        # Verifies that a canvas plot is generated correctly when creating a
        # new figure from scratch
        figure: go.Figure = self.canvas.plot(show=False, return_fig=True)

        with self.subTest(check='num_data_series'):
            # There should be 5 data series (outline + fill for each of the
            # non-construction shapes; outline only for construction shapes)
            expected_num_traces = 5

            self.assertEqual(len(figure.data), expected_num_traces)

        with self.subTest(check='layout'):
            layout_dict = figure.to_dict()['layout']
            del layout_dict['template']

            self.assertDictEqual(
                layout_dict,
                {'margin': {'r': 20, 't': 30}, 'plot_bgcolor': 'white', 'showlegend': False,
                 'xaxis': {'gridcolor': '#d2d2d2', 'gridwidth': 1, 'linecolor': 'black',
                           'linewidth': 1, 'mirror': True, 'showgrid': True, 'showline': True,
                           'title': {'text': 'x'}, 'zeroline': True, 'zerolinecolor': '#7b7b7b',
                           'zerolinewidth': 1},
                 'yaxis': {'gridcolor': '#d2d2d2', 'gridwidth': 1, 'linecolor': 'black',
                           'linewidth': 1, 'mirror': True, 'scaleanchor': 'x', 'scaleratio': 1,
                           'showgrid': True, 'showline': True, 'title': {'text': 'y'},
                           'zeroline': True, 'zerolinecolor': '#7b7b7b', 'zerolinewidth': 1},
                }
            )

        with self.subTest(check='shapes'):
            # Verifies that each shape's coordinates were requested
            self.shape1.xy_coordinates.assert_called_once()
            self.shape2.xy_coordinates.assert_called_once()
            self.shape3.xy_coordinates.assert_called_once()

    def test_plot_custom_figure(self):
        # Verifies that a canvas plot is generated correctly when appending to
        # an existing figure
        existing_figure = go.Figure()
        figure = self.canvas.plot(figure=existing_figure, show=False, return_fig=True)

        with self.subTest(check='num_data_series'):
            # There should be 5 data series (outline + fill for each of the
            # non-construction shapes; outline only for construction shapes)
            expected_num_traces = 5

            self.assertEqual(len(figure.data), expected_num_traces)

        with self.subTest(check='layout'):
            layout_dict = figure.to_dict()['layout']
            del layout_dict['template']

            self.assertDictEqual(layout_dict, {})

        with self.subTest(check='shapes'):
            # Verifies that each shape's coordinates were requested
            self.shape1.xy_coordinates.assert_called_once()
            self.shape2.xy_coordinates.assert_called_once()
            self.shape3.xy_coordinates.assert_called_once()

    def test_show(self):
        # Verifies that figures can be displayed if requested by user
        existing_figure = go.Figure()
        existing_figure.show = Mock()

        # Ensure plotting doesn't return any output (prevents printing
        # unnecessary text to the terminal)
        self.assertIsNone(
            self.canvas.plot(figure=existing_figure, show=True, return_fig=False)
        )

        # Verify that figure was displayed
        existing_figure.show.assert_called_once()


class Test_Canvas_Transform(Test_Canvas):
    def setUp(self):
        super().setUp()

        self.layer1 = Layer()
        self.layer2 = Layer()
        self.canvas = Canvas(self.layer1, self.layer2)

        self.layer1.reflect = Mock()
        self.layer2.reflect = Mock()

        self.layer1.reflect_x = Mock()
        self.layer2.reflect_x = Mock()

        self.layer1.reflect_y = Mock()
        self.layer2.reflect_y = Mock()

        self.layer1.rotate = Mock()
        self.layer2.rotate = Mock()

        self.layer1.translate = Mock()
        self.layer2.translate = Mock()

    def test_reflect(self):
        # Verifies that reflecting a canvas reflects all layers in the canvas
        self.canvas.reflect(pntA=(1, 2), pntB=(3, 4))

        self.layer1.reflect.assert_called_once_with(pntA=(1, 2), pntB=(3, 4))
        self.layer2.reflect.assert_called_once_with(pntA=(1, 2), pntB=(3, 4))

    def test_reflect_x(self):
        # Verifies that reflecting a canvas reflects all layers in the canvas
        self.canvas.reflect_x()

        self.layer1.reflect_x.assert_called_once()
        self.layer2.reflect_x.assert_called_once()

    def test_reflect_y(self):
        # Verifies that reflecting a canvas reflects all layers in the canvas
        self.canvas.reflect_y()

        self.layer1.reflect_y.assert_called_once()
        self.layer2.reflect_y.assert_called_once()

    def test_rotate(self):
        # Verifies that rotating a canvas rotates all layers in the canvas
        self.canvas.rotate(center=(8, 9), angle=1000, angle_units='in')

        self.layer1.rotate.assert_called_once_with(
            center=(8, 9), angle=1000, angle_units='in')
        self.layer1.rotate.assert_called_once_with(
            center=(8, 9), angle=1000, angle_units='in')

    def test_translate(self):
        # Verifies that translating a canvas translates all layers in the canvas
        self.canvas.translate(x=569, y=62)

        self.layer1.translate.assert_called_once_with(x=569, y=62)
        self.layer1.translate.assert_called_once_with(x=569, y=62)
