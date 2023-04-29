import unittest
from unittest.mock import Mock

import plotly.express as px
import plotly.graph_objects as go
import pyxx

from mahautils.shapes import Layer
from mahautils.shapes.geometry import (
    Circle,
    ClosedShape2D,
    OpenShape2D,
    Shape2D,
)


class Test_Layer(unittest.TestCase):
    def setUp(self):
        self.idx0 = Layer().id + 1

        self.circle1 = Circle((0, 0), radius=2)
        self.circle2 = Circle((2, 4), radius=6)
        self.closed_shape = ClosedShape2D()


class Test_Layer_Properties(Test_Layer):
    def setUp(self):
        super().setUp()

    def test_color_user(self):
        # Verifies that user-defined "color" attribute is set
        # and retrieved correctly
        self.assertEqual(Layer(color='red').color, 'red')

    def test_color_automatic(self):
        # Verifies that automatically-selected "color" attribute
        # is set and retrieved correctly
        plotly_colors = px.colors.qualitative.Plotly

        for _ in range(len(plotly_colors) + 2):
            # Check that layer colors follow Plotly's default color order
            layer1_color_index = plotly_colors.index(Layer().color)
            layer2_color_index = plotly_colors.index(Layer().color)

            if layer2_color_index < layer1_color_index:
                layer2_color_index += len(plotly_colors)

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

    def test_num_shapes(self):
        # Verifies that number of shapes in layer is computed accurately
        with self.subTest(num_shapes=0):
            self.assertEqual(Layer().num_shapes, 0)

        with self.subTest(num_shapes=1):
            self.assertEqual(Layer(self.circle1).num_shapes, 1)

        with self.subTest(num_shapes=2):
            self.assertEqual(Layer(self.circle1, self.circle2).num_shapes, 2)


class Test_Layer_Add(Test_Layer):
    def setUp(self):
        super().setUp()

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


class Test_Layer_Plot(Test_Layer):
    def setUp(self):
        super().setUp()

        self.units = 'myUnits'

        self.circle_construction = Circle(
            center=(8, 0), radius=6, construction=True, units=self.units)

        self.circle1.xy_coordinates = Mock(
            return_value=([2, 0, -2, 0, 2], [0, 2, 0, -2, 0]))
        self.circle2.xy_coordinates = Mock(
            return_value=([8, 2, -4, 2, 8], [4, 10, 4, -2, 4]))
        self.circle_construction.xy_coordinates = Mock(
            return_value=([14, 8, 2, 8, 14], [0, 6, 0, -6, 0]))

        self.circle1.units = self.units
        self.circle2.units = self.units

        self.circle_no_units = Circle(
            center=(2, 4), radius=6, default_num_coordinates=4)

        self.circle_invalid_units = Circle(
            center=(2, 4), radius=6, default_num_coordinates=4, units='mm')

        self.layer = Layer(self.circle1, self.circle2, self.circle_construction,
                           color='red')
        self.layer_data = [
            {'fill': 'toself', 'fillcolor': 'red', 'hoverinfo': 'skip',
             'opacity': 0.2, 'type': 'scatter',
             'x': [2, 0, -2, 0, 2], 'y': [0, 2, 0, -2, 0]},
            {'hovertemplate': '(%{x}, %{y})<extra></extra>',
             'line': {'color': 'red', 'dash': 'solid'},
             'marker': {'size': 4}, 'mode': 'lines+markers',
             'opacity': 1, 'type': 'scatter',
             'x': [2, 0, -2, 0, 2], 'y': [0, 2, 0, -2, 0]},
            {'fill': 'toself', 'fillcolor': 'red', 'hoverinfo': 'skip',
             'opacity': 0.2, 'type': 'scatter',
             'x': [8, 2, -4, 2, 8], 'y': [4, 10, 4, -2, 4]},
            {'hovertemplate': '(%{x}, %{y})<extra></extra>',
             'line': {'color': 'red', 'dash': 'solid'}, 'marker': {'size': 4},
             'mode': 'lines+markers', 'opacity': 1, 'type': 'scatter',
             'x': [8, 2, -4, 2, 8], 'y': [4, 10, 4, -2, 4]},
            {'hovertemplate': '(%{x}, %{y})<extra></extra>',
             'line': {'color': 'red', 'dash': 'dash'},
             'marker': {'size': 4}, 'mode': 'lines', 'opacity': 1, 'type': 'scatter',
             'x': [14, 8, 2, 8, 14], 'y': [0, 6, 0, -6, 0]},
        ]

    def test_plot_new_figure(self):
        # Verifies that a layer plot is generated correctly when creating a
        # new figure from scratch
        figure = self.layer.plot(show=False, return_fig=True)
        figure_dict = figure.to_dict()

        with self.subTest(key='data'):
            self.assertListEqual(figure_dict['data'], self.layer_data)

        with self.subTest(key='layout'):
            del figure_dict['layout']['template']

            self.assertDictEqual(
                figure_dict['layout'],
                {
                    'margin': {'r': 20, 't': 30}, 'plot_bgcolor': 'white', 'showlegend': False,
                    'xaxis': {
                        'gridcolor': '#d2d2d2', 'gridwidth': 1, 'linecolor': 'black', 'linewidth': 1,
                        'mirror': True, 'showgrid': True, 'showline': True, 'title': {'text': 'x'},
                        'zeroline': True, 'zerolinecolor': '#7b7b7b', 'zerolinewidth': 1
                    },
                    'yaxis': {
                        'gridcolor': '#d2d2d2', 'gridwidth': 1, 'linecolor': 'black', 'linewidth': 1,
                        'mirror': True, 'scaleanchor': 'x', 'scaleratio': 1, 'showgrid': True, 'showline': True,
                        'title': {'text': 'y'}, 'zeroline': True, 'zerolinecolor': '#7b7b7b', 'zerolinewidth': 1}
                }
            )

    def test_plot_new_figure_units(self):
        # Verifies that units are added to axis titles if requested by user
        figure = self.layer.plot(units=self.units, show=False, return_fig=True)
        figure_dict = figure.to_dict()

        self.assertEqual(figure_dict['layout']['xaxis']['title']['text'], f'x [{self.units}]')
        self.assertEqual(figure_dict['layout']['yaxis']['title']['text'], f'y [{self.units}]')

    def test_plot_custom_figure(self):
        # Verifies that a layer plot is generated correctly when appending to
        # an existing figure
        existing_figure = go.Figure()
        figure = self.layer.plot(figure=existing_figure, show=False, return_fig=True)
        figure_dict = figure.to_dict()

        with self.subTest(key='data'):
            self.assertListEqual(figure_dict['data'], self.layer_data)

        with self.subTest(key='layout'):
            del figure_dict['layout']['template']
            self.assertDictEqual(figure_dict['layout'], {})

    def test_show(self):
        # Verifies that figures can be displayed if requested by user
        existing_figure = go.Figure()
        existing_figure.show = Mock()

        # Ensure plotting doesn't return any output (prevents printing
        # unnecessary text to the terminal)
        self.assertIsNone(
            self.layer.plot(figure=existing_figure, show=True, return_fig=False)
        )

        # Verify that figure was displayed
        existing_figure.show.assert_called_once()

    def test_plot_open_shape(self):
        # Verifies that shapes that are not closed can be plotted
        open_shape = OpenShape2D()
        open_shape.xy_coordinates = Mock(return_value=([1, 2, 3], [4, 5, 6]))

        layer = Layer(open_shape, color='blue')
        figure = layer.plot(show=False, return_fig=True)
        figure_dict = figure.to_dict()

        self.assertDictEqual(
            figure_dict['data'][0],
            {'hovertemplate': '(%{x}, %{y})<extra></extra>',
             'line': {'color': 'blue', 'dash': 'solid'},
             'marker': {'size': 4}, 'mode': 'lines+markers',
             'opacity': 1, 'type': 'scatter',
             'x': [1, 2, 3], 'y': [4, 5, 6]}
        )

        # Ensure that the "repeat_end" argument was not provided for
        # open shapes
        open_shape.xy_coordinates.assert_called_once_with()

    def test_invalid_units(self):
        # Verifies that an error is thrown if the user requested to generate
        # a figure with units but units aren't identical
        with self.assertRaises(ValueError):
            self.layer.append(self.circle_invalid_units)
            self.layer.plot(units=self.units, show=False)

    def test_missing_units(self):
        # Verifies that an error is thrown if the user requested to generate
        # a figure with units but one or more shapes are missing units
        with self.assertRaises(ValueError):
            self.layer.append(self.circle_no_units)
            self.layer.plot(units=self.units, show=False)


class Test_Layer_Transform(Test_Layer):
    def setUp(self):
        super().setUp()

        self.layer = Layer(self.circle1, self.circle2, self.closed_shape)

        self.circle1.rotate = Mock()
        self.circle2.rotate = Mock()
        self.closed_shape.rotate = Mock()

        self.circle1.translate = Mock()
        self.circle2.translate = Mock()
        self.closed_shape.translate = Mock()

    def test_rotate(self):
        # Verifies that rotating a layer rotates all shapes in the layer
        self.layer.rotate(center=(5, 6), angle=700, angle_units='mm')

        self.circle1.rotate.assert_called_once_with(
            center=(5, 6), angle=700, angle_units='mm')
        self.circle2.rotate.assert_called_once_with(
            center=(5, 6), angle=700, angle_units='mm')
        self.closed_shape.rotate.assert_called_once_with(
            center=(5, 6), angle=700, angle_units='mm')

    def test_translate(self):
        # Verifies that translating a layer translates all shapes in the layer
        self.layer.translate(x=4627, y=510)

        self.circle1.translate.assert_called_once_with(x=4627, y=510)
        self.circle2.translate.assert_called_once_with(x=4627, y=510)
        self.closed_shape.translate.assert_called_once_with(x=4627, y=510)
