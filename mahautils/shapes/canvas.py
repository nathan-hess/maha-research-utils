"""The classes in this module are intended to store a group of related
:py:class:`Layer` objects.
"""

import itertools
from typing import Optional, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import plotly.graph_objects as go  # type: ignore
import pyxx

from mahautils.shapes.geometry.point import Array_Float2
from mahautils.shapes.geometry.point2D import CartesianPoint2D
from .layer import Layer
from .plotting import _figure_config, _create_blank_plotly_figure


class Canvas(pyxx.arrays.TypedListWithID[Layer]):
    """An object for storing a set of layers

    A :py:class:`Canvas` is intended to store a set of related layers, allowing
    more complex, multi-shape geometries to be constructed.  For instance, one
    potential application would be to use two :py:class:`Layer` objects to
    store the disjoint polygons corresponding to the high-pressure ports and
    the low-pressure ports in an axial piston pump, and then to group these
    layers at each instant in time in a :py:class:`Canvas`.  Then, multiple
    :py:class:`Canvas` objects could be used to store layers for every time
    step in the simulation.

    The :py:class:`Canvas` inherits from Python's ``MutableSequence`` type, so
    most operations that can be performed for a Python ``list`` (append, pop,
    insert, etc.) are valid operations for a :py:class:`Canvas`.
    """

    _id = itertools.count(0)

    def __init__(self, *layers: Layer, name: Optional[str] = None,
                 print_multiline: bool = True) -> None:
        """Creates a new canvas to store layers

        Creates a new :py:class:`Canvas` object in which a set of
        :py:class:`Layer` objects can be stored.

        Parameters
        ----------
        *layers : Layer, optional
            Layers to add to the canvas after the canvas is created (default
            is to add no layers)
        name : str, optional
            A descriptive name to identify the canvas.  If not provided, the
            canvas name is generated automatically
        print_multiline : bool, optional
            Whether to return a printable string representation of the list in
            multiline format (default is ``True``).  Multiline format places
            each item in the list on its own line
        """
        super().__init__(
            *layers,
            list_type=Layer,
            print_multiline=print_multiline,
            multiline_padding=1
        )

        # Set canvas name
        self.name = f'canvas{self.id}' if name is None else name

    @property
    def name(self) -> str:
        """A descriptive name to identify the canvas"""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = str(name)

    @property
    def num_layers(self) -> int:
        """The number of layers in the canvas"""
        return len(self)

    def plot(self, units: Optional[str] = None,
             figure: Optional[go.Figure] = None,
             show: bool = True, return_fig: bool = False,
             ) -> Union[go.Figure, None]:
        """Plots the shapes in the canvas

        Creates a Plotly figure illustrating the shapes in all layers of the
        canvas, or optionally appends traces for each shape to an existing
        figure.  The figure can be opened in a browser (default behavior)
        and/or returned (to allow subsequent user-specific customizations).

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
            A Plotly figure depicting the canvas.  Returned if and only if
            ``return_fig`` is ``True``
        """
        if not isinstance(figure, go.Figure):
            figure = _create_blank_plotly_figure(units)

        for layer in self:
            figure = layer.plot(units=units, figure=figure,
                                show=False, return_fig=True)

        if show:
            figure.show(config=_figure_config)

        if return_fig:
            return figure

        return None

    def reflect(self, pntA: Union[Array_Float2, 'CartesianPoint2D'],
                pntB: Union[Array_Float2, 'CartesianPoint2D']) -> None:
        """Reflects all shapes in all layers of the canvas about a line
        specified by two points

        Parameters
        ----------
        pntA : list or tuple or CartesianPoint2D
            One point on the line across which the shape is to be reflected
        pntB : list or tuple or CartesianPoint2D
            Another point on the line across which the shape is to be reflected
        """
        for layer in self:
            layer.reflect(pntA=pntA, pntB=pntB)

    def reflect_x(self) -> None:
        """Reflects all shapes in all layers of the canvas about
        the :math:`x`-axis
        """
        for layer in self:
            layer.reflect_x()

    def reflect_y(self) -> None:
        """Reflects all shapes in all layers of the canvas about
        the :math:`y`-axis
        """
        for layer in self:
            layer.reflect_y()

    def rotate(self, center: Union[Array_Float2, CartesianPoint2D],
               angle: float, angle_units: str = 'rad') -> None:
        """Rotates all shapes in all layers of the canvas a given angle in
        the :math:`xy`-plane about a user-specified point

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
        for layer in self:
            layer.rotate(center=center, angle=angle, angle_units=angle_units)

    def translate(self, x: float = 0, y: float = 0) -> None:
        """Translates all shapes in all layers of the canvas a user-specified
        distance in the :math:`x`- and/or :math:`y`-directions

        Parameters
        ----------
        x : float, optional
            The distance to translate the shapes in the :math:`x`-direction
            (default is ``0``)
        y : float, optional
            The distance to translate the shapes in the :math:`y`-direction
            (default is ``0``)
        """
        for layer in self:
            layer.translate(x=x, y=y)
