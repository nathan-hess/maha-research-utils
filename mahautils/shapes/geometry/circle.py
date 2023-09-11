"""Classes for representing a circle

The classes in this module are intended to represent a circle in the 2D
Cartesian coordinate system.
"""

import math
from typing import Optional, Tuple, Union

import numpy as np

from .point import Array_Float2
from .point2D import CartesianPoint2D
from .shape_open_closed import ClosedShape2D


class Circle(ClosedShape2D):
    """An object representing a circle in the 2D Cartesian plane

    This class is intended to represent a circle in 2D Cartesian coordinates.
    Users are required to define the circle's center and radius (or diameter)
    when creating :py:class:`Circle` objects, and the objects can then perform
    actions such as returning discretized points on the circumference of the
    circle and determining whether a point is inside the circle.

    Examples
    --------
    Create a circle centered at :math:`(0,0)` with radius :math:`2`:

    >>> circle = mahautils.shapes.Circle((0,0), radius=2)

    Generate points around the circle's circumference (output is rounded here
    for more easily understandable display):

    >>> import numpy as np
    >>> np.round(circle.points(num_coordinates=4, repeat_end=False))
    array([[ 2.,  0.],
           [ 0.,  2.],
           [-2.,  0.],
           [-0., -2.]])

    Check whether a point is inside the circle:

    >>> circle.is_inside((0, 0))
    True
    >>> circle.is_inside((2.01, 0))
    False
    """

    def __init__(self, center: Union[Array_Float2, CartesianPoint2D],
                 radius: Optional[float] = None, diameter: Optional[float] = None,
                 default_num_coordinates: Optional[int] = None,
                 construction: bool = False,
                 polygon_file_enclosed_conv: int = 1,
                 units: Optional[str] = None) -> None:
        """Creates an object representing a circle

        Defines a circle in the 2D Cartesian plane, locating it based on the
        center of the circle and the radius (or diameter).

        Parameters
        ----------
        center : list or tuple or CartesianPoint2D
            The center of the circle
        radius : float, optional
            The radius of the circle (default is ``None``)
        diameter : float, optional
            The diameter of the circle (default is ``None``)
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

        Notes
        -----
        It is required that either ``radius`` or ``diameter`` is provided, but
        not both.  If neither or both are provided, a :py:class:`TypeError`
        will be thrown.
        """
        super().__init__(
            default_num_coordinates=default_num_coordinates,
            construction=construction,
            polygon_file_enclosed_conv=polygon_file_enclosed_conv,
            units=units,
        )

        # Store circle center.  Mypy is disabled for this line because it
        # incorrectly identified the types of the argument and the attribute
        # as incompatible (even though they should be since the argument and
        # the setter function accept the same types)
        self.center = center  # type: ignore

        # Store circle radius or diameter
        if sum([radius is None, diameter is None]) != 1:
            raise TypeError(
                'Exactly one of the following arguments must be provided: '
                '["radius", "diameter"]')

        if radius is not None:
            self.radius = radius
        else:
            # Mypy is disabled on this line -- from previous check, "diameter"
            # cannot be "None" since it was already confirmed that either
            # "radius" or "diameter" is not "None", and this "else" statement
            # is only entered if "radius" is "None"
            self.diameter = diameter  # type: ignore

    def __eq__(self, value: object) -> bool:
        # Check that operand is of type "Circle"
        if not isinstance(value, Circle):
            return False

        # Check that units are the same
        if not self._has_identical_units(value):
            return False

        # If circles have the same center and radius, they are considered equal
        if (self.center == value.center) and (self.radius == value.radius):
            return True

        return False

    def __repr__(self):
        return f'{__class__} center={self.center}, radius={self.radius}'

    def __str__(self):
        return self.__repr__()

    @property
    def area(self) -> float:
        """The area of the circle"""
        return math.pi * (self.radius**2)

    @property
    def center(self) -> CartesianPoint2D:
        """The center of the circle"""
        return self._center

    @center.setter
    def center(self, center: Union[Array_Float2, CartesianPoint2D]):
        self._center = CartesianPoint2D(center)

    @property
    def circumference(self) -> float:
        """The circumference of the circle"""
        return 2.0 * math.pi * self.radius

    @property
    def diameter(self) -> float:
        """The diameter of the circle"""
        return 2.0 * self.radius

    @diameter.setter
    def diameter(self, diameter: float):
        self.radius = 0.5 * diameter

    @property
    def radius(self) -> float:
        """The radius of the circle"""
        return self._radius

    @radius.setter
    def radius(self, radius: float):
        if float(radius) < 0:
            raise ValueError('Circle radius cannot be negative')

        self._radius = float(radius)

    def intersection_area(self, circle: 'Circle'):
        """Calculates the area of intersection with another circle

        Calculates the overlapping area of intersection between this circle and
        another :py:class:`Circle` instance.  Mathematical formulas based on
        https://mathworld.wolfram.com/Circle-CircleIntersection.html.

        Parameters
        ----------
        circle : Circle
            The circle with which area of intersection is to be calculated

        Returns
        -------
        float
            The area of intersection between this circle and ``circle``
        """
        if not isinstance(circle, Circle):
            raise TypeError(
                'Intersection area can only be calculated with another circle')

        if not self._has_identical_units(circle):
            raise ValueError(
                'Circles have different units. Cannot compute intersection area')

        # Distance between circle centers
        d = self.center.distance_to(circle.center)

        # Maximum and minimum circle radius
        R = max(self.radius, circle.radius)
        r = min(self.radius, circle.radius)

        if d >= R + r:
            # Circles don't overlap
            return 0.0

        if d <= R - r:
            # The smaller circle is completely enclosed by the larger circle
            return math.pi*(r**2)

        return (
            r**2 * math.acos((d**2 + r**2 - R**2) / (2*d*r))
            + R**2 * math.acos((d**2 + R**2 - r**2) / (2*d*R))
            - 0.5 * math.sqrt((-d + r + R) * (d + r - R)
                              * (d - r + R) * (d + r + R))
        )

    def is_inside(self, point: Union[Array_Float2, CartesianPoint2D],
                  perimeter_is_inside: bool = True) -> bool:
        distance = self.center.distance_to(point)

        if perimeter_is_inside:
            return distance <= self.radius
        return distance < self.radius

    def points(self, repeat_end: bool = False,
               num_coordinates: Optional[int] = None,
               ) -> Tuple[np.ndarray, ...]:
        """Returns a list containing discretized points around the
        circumference of the circle

        This method returns a tuple, of which each element is a point along
        the circumference of the circle.  Points are ordered in a
        counterclockwise direction around the circle.

        Parameters
        ----------
        repeat_end : bool, optional
            Whether the first and last coordinate returned should be the same
            point (default is ``False``).  This is useful, for instance, when
            plotting the circle with Matplotlib: if ``repeat_end`` is set to
            ``False``, there may be a slight gap visible between the end points
            of the circle
        num_coordinates : int, optional
            The number of points to use when discretizing the circle's shape
            (default is ``None``).  If this argument is ``None`` or omitted,
            the number of points is set to :py:attr:`default_num_coordinates`,
            if provided (otherwise an error is thrown)

        See Also
        --------
        points :
            Returns the same coordinates as :py:meth:`points` except
            that points are returned with all the x-coordinates aggregated and
            all the y-coordinates aggregated (essentially the transpose of
            :py:meth:`points`)
        """
        return self._convert_xy_coordinates_to_points(
            num_coordinates=num_coordinates,
            repeat_end=repeat_end,
        )

    def reflect(self, pntA: Union[Array_Float2, 'CartesianPoint2D'],
                pntB: Union[Array_Float2, 'CartesianPoint2D']) -> None:
        self.center.reflect(pntA=pntA, pntB=pntB)

    def rotate(self, center: Union[Array_Float2, CartesianPoint2D],
               angle: float, angle_units: str = 'rad') -> None:
        self.center.rotate(center=center, angle=angle, angle_units=angle_units)

    def translate(self, x: float = 0, y: float = 0) -> None:
        self.center.translate(x=x, y=y)

    def xy_coordinates(self, repeat_end: bool = False,
                       num_coordinates: Optional[int] = None,
                       ) -> Tuple[np.ndarray, np.ndarray]:
        """Generates Cartesian coordinates of the circle

        This method generates a set of discretized points around the
        circumference of the circle, in counterclockwise order.  Points are
        returned as a tuple of two NumPy arrays: the first NumPy array
        contains the x-coordinates of the points, and the second NumPy array
        contains the y-coordinates.  This format makes it relatively easy to
        plot the shape using packages like Matplotlib.

        Parameters
        ----------
        repeat_end : bool, optional
            Whether the first and last coordinate returned should be the same
            point (default is ``False``).  This is useful, for instance, when
            plotting the circle with Matplotlib: if ``repeat_end`` is set to
            ``False``, there may be a slight gap visible between the end points
            of the circle
        num_coordinates : int, optional
            The number of points to use when discretizing the circle's shape
            (default is ``None``).  If this argument is ``None`` or omitted,
            the number of points is set to :py:attr:`default_num_coordinates`,
            if provided (otherwise an error is thrown)

        See Also
        --------
        points :
            Returns the same coordinates as :py:meth:`xy_coordinates` except
            that points are returned with the x- and y-coordinates grouped for
            each point (essentially the transpose of :py:meth:`xy_coordinates`)

        Examples
        --------
        Create a :py:class:`Circle` object and plot it with Matplotlib:

        >>> import matplotlib.pyplot as plt
        >>> circle = mahautils.shapes.Circle((0,0), radius=2)
        >>> fig = plt.plot(*circle.xy_coordinates(num_coordinates=1000))
        """
        # Determine the number of coordinates to output
        n = self._get_num_coordinates(num_coordinates)

        # Set the angles for which to output circle coordinates
        if repeat_end:
            end = 2 * math.pi
        else:
            end = 2 * math.pi * ((n - 1) / n)
        theta = np.linspace(0, end, n)

        # Calculate and return circle coordinates
        x_coordinates = self.radius * np.cos(theta) + self.center.x
        y_coordinates = self.radius * np.sin(theta) + self.center.y

        return (x_coordinates, y_coordinates)
