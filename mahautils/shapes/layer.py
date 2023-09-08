"""The classes in this module are intended to store a group of related 2D
shapes.
"""

import itertools
from typing import List, Optional, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import plotly.express as px        # type: ignore
import plotly.graph_objects as go  # type: ignore
import pyxx

from mahautils.shapes.geometry.shape_open_closed import ClosedShape2D, Shape2D
from mahautils.shapes.geometry.point import Array_Float2
from mahautils.shapes.geometry.point2D import CartesianPoint2D
from .plotting import _figure_config, _create_blank_plotly_figure


class Layer(pyxx.arrays.TypedListWithID[Shape2D]):
    """An object for storing a set of 2D shapes

    A :py:class:`Layer` is intended to store a set of related shapes, allowing
    more complex, multi-shape geometries to be constructed.  For instance, one
    potential application would be to use a :py:class:`Layer` to store the
    disjoint polygons that constitute the high-pressure ports in an axial
    piston pump.

    The :py:class:`Layer` inherits from Python's ``MutableSequence`` type, so
    most operations that can be performed for a Python ``list`` (append, pop,
    insert, etc.) are valid operations for a :py:class:`Layer`.
    """

    _id = itertools.count(0)

    def __init__(self, *shapes: Shape2D, name: Optional[str] = None,
                 color: str = 'default', print_multiline: bool = True,
                 ) -> None:
        """Creates a new layer to store shapes

        Creates a new :py:class:`Layer` object in which a set of 2D shapes (of
        type :py:class:`Shape2D`) can be stored.

        Parameters
        ----------
        *shapes : Shape2D, optional
            Shapes to add to the layer after the layer is created (default is
            no shapes)
        name : str, optional
            A descriptive name to identify the layer.  If not provided, the
            layer name is generated automatically
        color : str, optional
            The color with which to display the layer in plots.  If not
            provided or set to ``'default'``, the colors from Plotly's
            default color order are used
        print_multiline : bool, optional
            Whether to return a printable string representation of the list in
            multiline format (default is ``True``).  Multiline format places
            each item in the list on its own line

        Notes
        -----
        Any valid color accepted by Plotly can be specified, either as a named
        color (``'blue'``, ``'green'``, etc.) or a hex code.  Valid options are
        described on `this page <https://plotly.com/python/discrete-color/>`__.
        """
        super().__init__(*shapes, list_type=Shape2D,
                         print_multiline=print_multiline, multiline_padding=1)

        self.color = color
        self.name = f'layer{self.id}' if name is None else name

    @property
    def color(self) -> str:
        """The color with which to display the layer in plots

        Notes
        -----
        Any valid color accepted by Plotly can be specified, either as a named
        color (``'blue'``, ``'green'``, etc.) or a hex code.  Valid options are
        described on `this page <https://plotly.com/python/discrete-color/>`__.
        """
        return self._color

    @color.setter
    def color(self, color: str):
        # Get default Plotly color sequence
        plotly_colors: List[str] = px.colors.qualitative.Plotly

        # Set layer color
        if color == 'default':
            self._color = plotly_colors[self.id % len(plotly_colors)]
        else:
            self._color = str(color)

    @property
    def name(self) -> str:
        """A descriptive name to identify the layer"""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = str(name)

    @property
    def num_shapes(self) -> int:
        """The number of shapes in the layer"""
        return len(self)

    def plot(self, units: Optional[str] = None,
             figure: Optional[go.Figure] = None,
             show: bool = True, return_fig: bool = False,
             ) -> Union[go.Figure, None]:
        """Plots the shapes in the layer

        Creates a Plotly figure illustrating the shapes in the layer, or
        optionally appends traces for each shape to an existing figure.  The
        figure can be opened in a browser (default behavior) and/or returned
        (to allow subsequent user-specific customizations).

        Parameters
        ----------
        units : str, optional
            If units are provided, it will be verified that all plotted shapes
            have these units in their :py:attr:`Shape2D.units` attribute
            (default is ``None``, which performs no unit checks).  Additionally,
            if the ``figure`` argument was not provided, the specified units
            will be included in the axis titles
        figure : go.Figure, optional
            A Plotly figure.  If provided, rather than creating a new figure
            from scratch, the layer's shapes will be added as new traces in
            the provided figure (default is ``None``, which creates a new
            figure from scratch)
        show : bool, optional
            Whether to open the figure in a browser (default is ``True``)
        return_fig : bool, optional
            Whether to return the figure (default is ``False``)

        Returns
        -------
        go.Figure
            A Plotly figure depicting the layer.  Returned if and only if
            ``return_fig`` is ``True``
        """
        if not isinstance(figure, go.Figure):
            figure = _create_blank_plotly_figure(units)

        for shape in self:
            if (units is not None) and (units != shape.units):
                raise ValueError(
                    f'Expected all shapes to have units "{units}" but found '
                    f'a shape with units "{shape.units}"')

            if isinstance(shape, ClosedShape2D):
                x, y = shape.xy_coordinates(repeat_end=True)

                if not shape.construction:
                    figure.add_trace(go.Scatter(
                        x=x, y=y, fill='toself',
                        fillcolor=self.color, line=None, opacity=0.2,
                        hoverinfo='skip',
                    ))
            else:
                x, y = shape.xy_coordinates()

            figure.add_trace(go.Scatter(
                x=x, y=y, fill=None, opacity=1, fillcolor=None,
                mode='lines' if shape.construction else 'lines+markers',
                line={
                    'color': self.color,
                    'dash': 'dash' if shape.construction else 'solid',
                },
                marker={'size': 4},
                hovertemplate='(%{x}, %{y})<extra></extra>',
            ))

        if show:
            figure.show(config=_figure_config)

        if return_fig:
            return figure

        return None

    def reflect(self, pntA: Union[Array_Float2, 'CartesianPoint2D'],
                pntB: Union[Array_Float2, 'CartesianPoint2D']) -> None:
        """Reflects all shapes in the layer about a line specified by two points

        Parameters
        ----------
        pntA : list or tuple or CartesianPoint2D
            One point on the line across which the shape is to be reflected
        pntB : list or tuple or CartesianPoint2D
            Another point on the line across which the shape is to be reflected
        """
        for shape in self:
            shape.reflect(pntA=pntA, pntB=pntB)

    def reflect_x(self) -> None:
        """Reflects all shapes in the layer about the :math:`x`-axis
        """
        for shape in self:
            shape.reflect_x()

    def reflect_y(self) -> None:
        """Reflects all shapes in the layer about the :math:`y`-axis
        """
        for shape in self:
            shape.reflect_y()

    def rotate(self, center: Union[Array_Float2, CartesianPoint2D],
               angle: float, angle_units: str = 'rad') -> None:
        """Rotates all shapes in the layer a given angle in the :math:`xy`-plane
        about a user-specified point

        Parameters
        ----------
        center : list or tuple or CartesianPoint2D
            The center of rotation about which to rotate the shapes
        angle : float
            The angle by which to rotate the shapes about ``center``
        angle_units : str, optional
            The units (radians or degrees) of the ``angle`` argument.  Must be
            either ``'rad'`` or ``'deg'`` (default is ``'rad'``)
        """
        for shape in self:
            shape.rotate(center=center, angle=angle, angle_units=angle_units)

    def translate(self, x: float = 0, y: float = 0) -> None:
        """Translates all shapes in the layer a user-specified distance in
        the :math:`x`- and/or :math:`y`-directions

        Parameters
        ----------
        x : float, optional
            The distance to translate the shapes in the :math:`x`-direction
            (default is ``0``)
        y : float, optional
            The distance to translate the shapes in the :math:`y`-direction
            (default is ``0``)
        """
        for shape in self:
            shape.translate(x=x, y=y)
