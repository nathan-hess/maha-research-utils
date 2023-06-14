"""Classes for representing a point in space

The classes in this module can be used to store the location of a point in
space.  Although these data could simply be stored in a tuple or list, the
custom classes in this module are advantageous in that they avoid mistakenly
mixing coordinate systems (such as Cartesian and polar) and they provide
added error-checking functionality, such as verifying that coordinates are
floating-point numbers.
"""

from typing import List, Optional, overload, Tuple, Union

import numpy as np

from .geometry import Geometry

# Type alias for a list or tuple containing two floating-point numbers
Array_Float2 = Union[List[float], Tuple[float, float], np.ndarray]

# Type alias for a list or tuple containing three floating-point numbers
Array_Float3 = Union[List[float], Tuple[float, float, float], np.ndarray]


class Point(Geometry):
    """Base class representing an arbitrary point in a space of an arbitrary
    number of dimensions

    This is a generic class that represents an arbitrary point in any
    coordinate system.  In general, this class should be inherited by
    other classes and customizations added (for instance, checking that
    the number of point coordinates match the dimension of the coordinate
    system).

    Notes
    -----
    The equality operator (``==``) is defined for points.  Points are
    considered equal if they are of the same type (:py:class:`Point`,
    :py:class:`CartesianPoint2D`, etc.) and if the points' have
    :py:attr:`coordinates` attributes of the same shape and values.
    """

    def __init__(self, units: Optional[str] = None, **kwargs):
        """Creates an instance of a :py:class:`Point` class and sets the point
        coordinates to an empty tuple

        Parameters
        ----------
        units : str, optional
            The units in which the geometry is defined, or ``None`` to
            indicate dimensionless geometry or that units are to be ignored
            (default is ``None``)
        """
        super().__init__(units=units, **kwargs)

        self._coordinates: Tuple[float, ...] = ()

        # Iterable index
        self.__iter_index = 0

    def __eq__(self, value) -> bool:
        # Verify that `value` is of the same type of point
        if not isinstance(value, self.__class__):
            return False

        # Check that units are the same
        if not self._has_identical_units(value):
            return False

        # If points don't have the same number of coordinates, they aren't equal
        if len(self.coordinates) != len(value.coordinates):
            return False

        # If coordinate values differ, the points aren't equal
        for i, item in enumerate(self.coordinates):
            if item != value.coordinates[i]:
                return False

        return True

    @overload
    def __getitem__(self, index: int) -> float:
        ...  # pragma: no cover

    @overload
    def __getitem__(self, index: slice) -> Tuple[float, ...]:
        ...  # pragma: no cover

    def __getitem__(self, idx):
        return self._coordinates[idx]

    def __iter__(self):
        self.__iter_index = 0
        return self

    def __len__(self):
        return len(self._coordinates)

    def __next__(self):
        if self.__iter_index >= len(self._coordinates):
            self.__iter_index = 0
            raise StopIteration

        self.__iter_index += 1
        return self._coordinates[self.__iter_index - 1]

    def __repr__(self):
        return f'{self.__class__} {self.__str__()}'

    def __str__(self) -> str:
        return str(self._coordinates)

    @property
    def coordinates(self) -> Tuple[float, ...]:
        """The coordinates of the point"""
        return self._coordinates

    @coordinates.setter
    def coordinates(self):
        raise NotImplementedError  # pragma: no cover
