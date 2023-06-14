"""Classes for representing a point in 3D space

The classes in this module can be used to store the location of a point in
a three-dimensional space.
"""

import math
from typing import Optional, Union

from .point import Array_Float3, Point


class CartesianPoint3D(Point):
    """Class representing a point in 3D Cartesian coordinates

    This class can be used to represent a point in the 3D Cartesian coordinate
    system.  Note that although the axes for such a coordinate system can be
    arbitrary (:math:`xyz`-coordinates, :math:`a_1 a_2 a_3`-coordinates, etc.),
    in this class the axes are always referred to as :math:`x`, :math:`y`, and
    :math:`z` for simplicity and clarity.

    Notes
    -----
    The equality operator (``==``) is defined for points.  Points are
    considered equal if they are of the same type (:py:class:`Point`,
    :py:class:`CartesianPoint3D`, etc.), have :py:attr:`coordinates`
    attributes of the same shape and values, and have the same value of
    :py:attr:`units`.

    Examples
    --------
    Create a :py:class:`CartesianPoint3D` with no location initialized:

    >>> print(mahautils.shapes.CartesianPoint3D())
    ()

    Create a :py:class:`CartesianPoint3D` with location specified by
    positional arguments:

    >>> print(mahautils.shapes.CartesianPoint3D(1, 2.3, 4))
    (1.0, 2.3, 4.0)
    >>> print(mahautils.shapes.CartesianPoint3D([4, 5, 6]))
    (4.0, 5.0, 6.0)
    >>> pnt = mahautils.shapes.CartesianPoint3D([6, 7, 8])
    >>> print(mahautils.shapes.CartesianPoint3D(pnt))
    (6.0, 7.0, 8.0)

    Create a :py:class:`CartesianPoint3D` with location specified by
    keyword arguments:

    >>> print(mahautils.shapes.CartesianPoint3D(x=1, y=2, z=3))
    (1.0, 2.0, 3.0)
    """

    def __init__(self, *args: Union[Array_Float3, 'CartesianPoint3D', float],
                 units: Optional[str] = None, **kwargs):
        """Defines a point in the 3D Cartesian coordinate system

        Creates a :py:class:`CartesianPoint3D` instance and optionally allows
        the user to define the location of the point.

        Parameters
        ----------
        args : list or tuple or CartesianPoint3D or float, optional
            Positional arguments provided when creating the point object.  See
            the "Notes" section for information on how to use positional
            arguments to specify the point location
        units : str, optional
            The units in which the geometry is defined, or ``None`` to
            indicate dimensionless geometry or that units are to be ignored
            (default is ``None``)
        kwargs : Any, optional
            Keyword arguments provided when creating the point object.  See
            the "Notes" section for information on how to use keyword arguments
            to specify the point location

        Notes
        -----
        When creating a :py:class:`CartesianPoint3D` instance, it is possible
        to provide the point location using the constructor arguments.  This
        location can be provided using *either positional or keyword arguments,
        but not both*.

        If providing the location using positional arguments, then any of the
        following may be specified: (1) three floating-point numbers; (2) a list,
        tuple, NumPy array, or any other array-like object containing two
        floating-point numbers; or (3) another :py:class:`CartesianPoint3D`
        instance.

        If providing the location using keyword arguments, then *three* keyword
        arguments *must* be specified: ``x``, ``y``, and ``z``.  Both arguments
        must be numeric types (integer or floating-point values).
        """
        super().__init__(units=units)

        # Variable that indicates whether the point coordinates have already
        # been stored
        stored_point = False

        # Store point location passed as positional arguments
        if len(args) > 0:
            # If user passed a list, tuple, or `CartesianPoint3D` instance,
            # directly store the point coordinates
            if len(args) == 1:
                self.coordinates = args[0]

            # If user passed individual point values, store them
            else:
                self.coordinates = args

            # Record that point location was stored
            stored_point = True

        # Store point location passed as keyword arguments
        if ('x' in kwargs) or ('y' in kwargs) or ('z' in kwargs):
            # Check that the user didn't try to provide the point coordinates
            # using both positional and keyword arguments
            if stored_point:
                raise TypeError(
                    'Invalid input. Point location can be specified using '
                    'either positional or keyword arguments, but not both')

            # Verify that both x-, y-, and z-coordinates were provided
            if not (('x' in kwargs) and ('y' in kwargs) and ('z' in kwargs)):
                raise TypeError(
                    'Invalid keyword arguments. If providing point location '
                    'using keyword arguments, both arguments "x," "y," and '
                    '"z" must be provided')

            # Store point coordinates
            self.coordinates = (kwargs['x'], kwargs['y'], kwargs['z'])

            # Record that point location was stored
            stored_point = True

    @property
    def coordinates(self):
        """The coordinates of the point, represented as a tuple ``(x, y, z)``"""
        return super().coordinates

    @coordinates.setter
    def coordinates(self, coordinates: Union[Array_Float3, 'CartesianPoint3D']):
        if isinstance(coordinates, CartesianPoint3D):
            self._coordinates = coordinates.coordinates

        else:
            # Verify that three coordinates were provided
            try:
                # This does not use `assert` because `assert` statements can in
                # some cases be removed when compiling to optimized byte code
                if len(coordinates) != 3:
                    raise AssertionError(
                        'Length of provided coordinates must be 3, '
                        f'but {len(coordinates)} coordinate(s) were provided')
            except (AssertionError, TypeError) as exception:
                raise ValueError('Point coordinates must be a list or tuple '
                                 'of length 3') from exception

            # Convert coordinates to floating-point numbers and store values
            try:
                self._coordinates \
                    = (float(coordinates[0]), float(coordinates[1]),
                       float(coordinates[2]))
            except (TypeError, ValueError) as exception:
                raise ValueError(
                    'All point coordinates must be of a numeric type '
                    '(float, int, etc.)') from exception

    @property
    def x(self):
        """The x-coordinate of the point"""
        return self.coordinates[0]

    @x.setter
    def x(self, x: float) -> None:
        self.coordinates = (x, self.y, self.z)

    @property
    def y(self):
        """The y-coordinate of the point"""
        return self.coordinates[1]

    @y.setter
    def y(self, y: float) -> None:
        self.coordinates = (self.x, y, self.z)

    @property
    def z(self):
        """The z-coordinate of the point"""
        return self.coordinates[2]

    @z.setter
    def z(self, z: float) -> None:
        self.coordinates = (self.x, self.y, z)

    def distance_to(self, point: Union[Array_Float3, 'CartesianPoint3D']):
        """Computes the distance to another point

        Calculates and returns the distance to another point in the same 3D
        Cartesian coordinate system.

        Parameters
        ----------
        point : list or tuple or CartesianPoint3D
            The point to which to calculate distance

        Returns
        -------
        float
            The distance to another location ``point`` in 3D Cartesian space
        """
        pnt = CartesianPoint3D(point)
        return math.sqrt((self.x - pnt.x)**2 + (self.y - pnt.y)**2
                         + (self.z - pnt.z)**2)
