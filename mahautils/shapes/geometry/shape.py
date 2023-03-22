"""Classes for representing 2D shapes

The classes in this module are intended to represent arbitrary 2D shapes and
to be used in "drawing" utilities in which complex 2D geometry is assembed
from a variety of simpler shapes.
"""

from typing import Optional, Tuple, Union

import numpy as np

from .geometry import Geometry
from .point import Array_Float2, CartesianPoint2D


class Shape2D(Geometry):
    """Represents an arbitrary, two-dimensional shape

    This class is intended to represent an arbitrary 2D shape.  Note that
    the intended application for this class is to be used in a drawing utility,
    which is why attributes such as "construction" shapes are defined (these
    are a common feature of computer-aided design tools).
    """

    def __init__(self, is_closed: bool,
                 default_num_coordinates: Optional[int] = None,
                 construction: bool = False,
                 units: Optional[str] = None) -> None:
        """Creates an object representing a 2D geometric shape

        Defines an object which represents a general shape and can return
        shape properties and the Cartesian coordinates of the (discretized)
        shape.

        Parameters
        ----------
        is_closed : bool
            Whether the shape is bounded by a closed perimeter
        default_num_coordinates : int, optional
            The default number of coordinates to use when representing the
            shape (default is ``None``)
        construction : bool, optional
            Whether the shape is a "construction shape" meant for visual
            display but not functional geometry (default is ``False``)
        units : str, optional
            The units in which the geometry is defined, or ``None`` to
            indicate dimensionless geometry or that units are to be ignored
            (default is ``None``)
        """
        super().__init__(units=units)

        self._is_closed = bool(is_closed)
        self.construction = construction
        self.default_num_coordinates = default_num_coordinates

    @property
    def construction(self):
        """Whether the shape is a "construction shape" meant for visual
        display but not functional geometry"""
        return self._construction

    @construction.setter
    def construction(self, construction: bool):
        if not isinstance(construction, bool):
            raise TypeError('Argument "construction" must be of type "bool"')

        self._construction = construction

    @property
    def is_closed(self):
        """Whether the shape is bounded by a closed perimeter"""
        return self._is_closed

    @property
    def default_num_coordinates(self):
        """The number of coordinates to use when representing a discretized
        form of the shape"""
        return self._default_num_coordinates

    @default_num_coordinates.setter
    def default_num_coordinates(self, default_num_coordinates: Optional[int]):
        if default_num_coordinates is None:
            self._default_num_coordinates = None
        else:
            try:
                if not float(default_num_coordinates).is_integer():
                    raise ValueError(
                        'Argument "default_num_coordinates" must be an '
                        'integer, not a floating-point number')
            except (TypeError, ValueError) as exception:
                raise ValueError('Unable to convert "default_num_coordinates" '
                                 'to an integer') from exception

            if int(default_num_coordinates) <= 0:
                raise ValueError(
                    'Argument "default_num_coordinates" must be positive')

            self._default_num_coordinates = int(default_num_coordinates)

    def _convert_xy_coordinates_to_points(self, **kwargs
                                          ) -> Tuple[np.ndarray, ...]:
        x_coordinates, y_coordinates = self.xy_coordinates(**kwargs)
        return tuple(np.transpose(np.array([x_coordinates, y_coordinates])))

    def _get_num_coordinates(self, num_coordinates: Optional[int] = None):
        if num_coordinates is not None:
            return num_coordinates

        if self.default_num_coordinates is not None:
            return self.default_num_coordinates

        raise ValueError('Cannot generate coordinates.  Neither the '
                         '"num_coordinates" argument was be provided nor '
                         'was the "default_num_coordinates" attribute set')

    def points(self) -> Tuple[np.ndarray, ...]:
        """Returns a list containing discretized points around the perimeter
        of the shape

        This method returns a tuple, of which each element is a point along
        the perimeter of the shape.

        See Also
        --------
        xy_coordinates :
            Returns the same coordinates as :py:meth:`xy_coordinates` except
            that points are returned as a list, where each entry is a point on
            the perimeter of the shape (essentially the transpose of
            :py:meth:`xy_coordinates`)
        """
        raise NotImplementedError  # pragma: no cover

    def xy_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generates Cartesian coordinates of the shape

        This method generates a set of discretized points around the perimeter
        of the shape.  Points are returned as a tuple of two NumPy arrays: the
        first NumPy array contains the x-coordinates of the points, and the
        second NumPy array contains the y-coordinates.  This format makes it
        relatively easy to plot the shape using packages like Matplotlib.

        See Also
        --------
        points :
            Returns the same coordinates as :py:meth:`xy_coordinates` except
            that points are returned with the x- and y-coordinates grouped for
            each point (essentially the transpose of :py:meth:`xy_coordinates`)
        """
        raise NotImplementedError  # pragma: no cover


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
