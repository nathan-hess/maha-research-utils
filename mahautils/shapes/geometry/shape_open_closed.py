"""Classes for representing 2D shapes

The classes in this module are subclasses of the
:py:class:`mahautils.shapes.Shape2D` class and intended to represent
open and closed arbitrary 2D shapes.
"""

from typing import Optional, Tuple, Union

import numpy as np

from .point import Array_Float2
from .point2D import CartesianPoint2D
from .shape import Shape2D


class ClosedShape2D(Shape2D):
    """A class that represents a closed, two-dimensional shape

    This class is intended to represent closed shapes (i.e., shapes for which
    any given point in space is either inside or outside the shape, or on the
    perimeter).
    """

    def __init__(self, default_num_coordinates: Optional[int] = None,
                 construction: bool = False,
                 polygon_file_enclosed_conv: int = 1,
                 units: Optional[str] = None) -> None:
        """Creates an object representing a closed, 2D geometric shape

        Defines an object which represents a closed shape in the 2D Cartesian
        coordinate system.

        Parameters
        ----------
        default_num_coordinates : int, optional
            The default number of coordinates to use when representing the
            shape (default is ``None``)
        construction : bool, optional
            Whether the shape is a "construction shape" meant for visual
            display but not functional geometry (default is ``False``)
        polygon_file_enclosed_conv : int, optional
            Convention for considering enclosed area when generating a polygon
            file from :py:class:`ClosedShape2D` objects (default is ``1``)
        units : str, optional
            The units in which the geometry is defined, or ``None`` to
            indicate dimensionless geometry or that units are to be ignored
            (default is ``None``)
        """
        super().__init__(
            is_closed=True,
            default_num_coordinates=default_num_coordinates,
            construction=construction,
            units=units,
        )

        self.polygon_file_enclosed_conv = polygon_file_enclosed_conv

    @property
    def area(self) -> float:
        """Returns the area enclosed by the shape"""
        raise NotImplementedError  # pragma: no cover

    @property
    def polygon_file_enclosed_conv(self) -> int:
        """Convention for considering enclosed area when generating a polygon
        file from :py:class:`ClosedShape2D` objects

        **This property is exclusively intended for use when generating Maha
        Multics polygon files.**  As discussed on the :ref:`fileref-polygon_file`
        page, when generating Maha Multics polygon files, the ``ENCLOSED_CONV``
        option can be set for any given closed shape to indicate whether the
        area inside the shape (as determined by the winding number algorithm) is
        considered by the polygon file to to be "enclosed" area.  This property
        is designed to store the value of this ``ENCLOSED_CONV`` option for any
        :py:class:`ClosedShape2D` objects that are to be incorporated into a
        polygon file.

        .. note::

            For more information about the interpretation of this option, refer
            to the :ref:`Polygon File Format <fileref-polygon_file-enclosed_conv>`
            page.
        """
        return self._polygon_file_enclosed_conv

    @polygon_file_enclosed_conv.setter
    def polygon_file_enclosed_conv(self, polygon_file_enclosed_conv: int) -> None:
        if polygon_file_enclosed_conv not in (0, 1):
            raise ValueError('Polygon file enclosed area convention must be '
                             'equal to 1 or 0')

        self._polygon_file_enclosed_conv = polygon_file_enclosed_conv

    def is_inside(self, point: Union[Array_Float2, CartesianPoint2D],
                  perimeter_is_inside: bool = True) -> bool:
        """Returns whether a point is inside the shape

        Parameters
        ----------
        point : list or tuple or CartesianPoint2D
            The point whose location is to be checked.  Must be either a
            :py:class:`CartesianPoint2D` instance, or a list or tuple
            containing two elements of type ``float``
        perimeter_is_inside : bool, optional
            Whether to consider points on the perimeter of the shape to be
            inside the shape (default is ``True``)

        Returns
        -------
        bool
            If ``perimeter_is_inside`` is ``True``, returns ``True`` if
            ``point`` is inside the shape or on the perimeter, and ``False``
            otherwise.  If ``perimeter_is_inside`` is ``False``, returns ``True``
            if ``point`` is inside the shape but NOT on the perimeter, and
            ``False`` otherwise
        """
        raise NotImplementedError  # pragma: no cover

    def points(self, repeat_end: bool = False) -> Tuple[np.ndarray, ...]:
        """Returns a list containing discretized points around the perimeter
        of the shape

        This method returns a tuple, of which each element is a point along
        the perimeter of the shape.

        Parameters
        ----------
        repeat_end : bool, optional
            Whether the first and last coordinate returned should be the same
            point (default is ``False``).  This is useful, for instance, when
            plotting the shape with Matplotlib: if ``repeat_end`` is set to
            ``False``, there may be a slight gap visible between the end points
            of the shape

        See Also
        --------
        xy_coordinates :
            Returns the same coordinates as :py:meth:`xy_coordinates` except
            that points are returned as a list, where each entry is a point on
            the perimeter of the shape (essentially the transpose of
            :py:meth:`xy_coordinates`)
        """
        raise NotImplementedError  # pragma: no cover

    def xy_coordinates(self, repeat_end: bool = False
                       ) -> Tuple[np.ndarray, np.ndarray]:
        """Generates Cartesian coordinates of the shape

        This method generates a set of discretized points around the perimeter
        of the shape.  Points are returned as a tuple of two NumPy arrays: the
        first NumPy array contains the x-coordinates of the points, and the
        second NumPy array contains the y-coordinates.  This format makes it
        relatively easy to plot the shape using packages like Matplotlib.

        Parameters
        ----------
        repeat_end : bool, optional
            Whether the first and last coordinate returned should be the same
            point (default is ``False``).  This is useful, for instance, when
            plotting the shape with Matplotlib: if ``repeat_end`` is set to
            ``False``, there may be a slight gap visible between the end points
            of the shape

        See Also
        --------
        points :
            Returns the same coordinates as :py:meth:`xy_coordinates` except
            that points are returned with the x- and y-coordinates grouped for
            each point (essentially the transpose of :py:meth:`xy_coordinates`)
        """
        raise NotImplementedError  # pragma: no cover


class OpenShape2D(Shape2D):
    """A class that represents an open, two-dimensional shape

    This class is intended to represent open shapes (i.e., shapes for which
    the boundary does not form a single closed path, so there is no clear
    definition as to whether a point in space is inside or outside the shape).
    """

    def __init__(self, default_num_coordinates: Optional[int] = None,
                 construction: bool = False, units: Optional[str] = None,
                 ) -> None:
        """Creates an object representing an open, 2D geometric shape

        Defines an object which represents an open shape in the 2D Cartesian
        coordinate system.

        Parameters
        ----------
        default_num_coordinates : int, optional
            The default number of coordinates to use when representing the
            shape (default is ``None``)
        construction : bool, optional
            Whether the shape is a "construction shape" meant for visual
            display but not functional geometry (default is ``False``)
        """
        super().__init__(
            is_closed=False,
            default_num_coordinates=default_num_coordinates,
            construction=construction,
            units=units,
        )

    def xy_coordinates(self, *args, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError  # pragma: no cover
