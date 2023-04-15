"""The classes in this module are intended to store a group of related 2D
shapes.
"""

import itertools
from typing import List, Optional, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import plotly.express as px        # type: ignore
import pyxx

from mahautils.shapes.geometry.shape import Shape2D


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
