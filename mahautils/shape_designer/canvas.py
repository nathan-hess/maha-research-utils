"""The classes in this module are intended to store a group of related
:py:class:`Layer` objects.
"""

import itertools
from typing import Optional

import pyxx

from .layer import Layer


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

    def __init__(self, *layers: Layer, name: Optional[str] = None) -> None:
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
        """
        super().__init__(
            *layers,
            list_type=Layer,
            print_multiline=True,
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
