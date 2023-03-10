"""Classes for representing 2D shapes

The classes in this module are intended to represent arbitrary 2D shapes and
to be used in "drawing" utilities in which complex 2D geometry is assembed
from a variety of simpler shapes.
"""

from typing import Optional, Tuple, Union

import numpy as np

from .point import Array_Float2, CartesianPoint2D


class Shape2D:
    """Represents an arbitrary, two-dimensional shape

    This class is intended to represent an arbitrary 2D shape.  Note that
    the intended application for this class is to be used in a drawing utility,
    which is why attributes such as "construction" shapes are defined (these
    are a common feature of computer-aided design tools).
    """

    def __init__(self, is_closed: bool,
                 default_num_coordinates: Optional[int] = None,
                 construction: bool = False):
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
        """
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
        points :
            Returns the same coordinates as :py:meth:`points` except
            that points are returned with all the x-coordinates aggregated and
            all the y-coordinates aggregated (essentially the transpose of
            :py:meth:`points`)
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
                 construction: bool = False):
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
        """
        super().__init__(
            is_closed=True,
            default_num_coordinates=default_num_coordinates,
            construction=construction
        )

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


class OpenShape2D(Shape2D):
    """A class that represents an open, two-dimensional shape

    This class is intended to represent open shapes (i.e., shapes for which
    the boundary does not form a single closed path, so there is no clear
    definition as to whether a point in space is inside or outside the shape).
    """

    def __init__(self, default_num_coordinates: Optional[int] = None,
                 construction: bool = False):
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
            construction=construction
        )

    def xy_coordinates(self, *args, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError  # pragma: no cover
