"""Classes for representing 2D shapes

The classes in this module are intended to represent arbitrary 2D shapes and
to be used in "drawing" utilities in which complex 2D geometry is assembed
from a variety of simpler shapes.
"""

import math
from typing import Optional, Tuple, TYPE_CHECKING, Union

import numpy as np

from .geometry import Geometry
from .point import Array_Float2

if TYPE_CHECKING:
    from .point2D import CartesianPoint2D  # pragma: no cover


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

    def _convert_rotate_angle(self, angle: float, angle_units: str) -> float:
        if angle_units == 'rad':
            return angle

        if angle_units == 'deg':
            return math.radians(angle)

        raise ValueError('Argument "angle_units" must be either "rad" or "deg"')

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

    def reflect(self, pntA: Union[Array_Float2, 'CartesianPoint2D'],
                pntB: Union[Array_Float2, 'CartesianPoint2D']) -> None:
        """Reflects the shape across a line defined by two points

        Parameters
        ----------
        pntA : list or tuple or CartesianPoint2D
            One point on the line across which the shape is to be reflected
        pntB : list or tuple or CartesianPoint2D
            Another point on the line across which the shape is to be reflected
        """
        raise NotImplementedError  # pragma: no cover

    def reflect_x(self):
        """Reflects the shape over the :math:`x`-axis"""
        self.reflect((0.0, 0.0), (1.0, 0.0))

    def reflect_y(self):
        """Reflects the shape over the :math:`y`-axis"""
        self.reflect((0.0, 0.0), (0.0, 1.0))

    def rotate(self, center: Union[Array_Float2, 'CartesianPoint2D'],
               angle: float, angle_units: str = 'rad') -> None:
        """Rotates the shape in the :math:`xy`-plane

        Rotates the shape the shape a given angle in the :math:`xy`-plane
        about a user-specified point.

        Parameters
        ----------
        center : list or tuple or CartesianPoint2D
            The center of rotation about which to rotate the shape
        angle : float
            The angle by which to rotate the shape about ``center``
        angle_units : str, optional
            The units (radians or degrees) of the ``angle`` argument.  Must be
            either ``'rad'`` or ``'deg'`` (default is ``'rad'``)
        """
        raise NotImplementedError  # pragma: no cover

    def translate(self, x: float = 0, y: float = 0) -> None:
        """Translates the shape in the :math:`xy`-plane

        Translates the shape a user-specified distance in the :math:`x`- and/or
        :math:`y`-directions.

        Parameters
        ----------
        x : float, optional
            The distance to translate the shape in the :math:`x`-direction
            (default is ``0``)
        y : float, optional
            The distance to translate the shape in the :math:`y`-direction
            (default is ``0``)
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
