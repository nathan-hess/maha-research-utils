"""Classes for representing a point in space

The classes in this module can be used to store the location of a point in
space.  Although these data could simply be stored in a tuple or list, the
custom classes in this module are advantageous in that they avoid mistakenly
mixing coordinate systems (such as Cartesian and polar) and they provide
added error-checking functionality, such as verifying that coordinates are
floating-point numbers.
"""

import math
from typing import List, Tuple, Union

# Type alias for a list or tuple containing two floating-point numbers
Array_Float2 = Union[List[float], Tuple[float, float]]


class Point:
    """Base class representing an arbitrary point in space

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

    def __init__(self):
        """Creates an instance of a :py:class:`Point` class and sets the point
        coordinates to an empty tuple"""
        self._coordinates = ()

    def __eq__(self, value) -> bool:
        # Verify that `value` is of the same type of point
        if not isinstance(value, self.__class__):
            return False

        # If points don't have the same number of coordinates, they aren't equal
        if len(self.coordinates) != len(value.coordinates):
            return False

        # If coordinate values differ, the points aren't equal
        for i, item in enumerate(self.coordinates):
            if item != value.coordinates[i]:
                return False

        return True

    def __len__(self):
        return len(self._coordinates)

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


class CartesianPoint2D(Point):
    """Class representing a point in 2D Cartesian coordinates

    This class can be used to represent a point in the 2D Cartesian coordinate
    system.  Note that although the axes for such a coordinate system can be
    arbitrary (:math:`xy`-coordinates, :math:`xz`-coordinates, etc.) in this
    documentation the axes are always referred to as :math:`x` and :math:`y`
    for simplicity and clarity.

    Notes
    -----
    The equality operator (``==``) is defined for points.  Points are
    considered equal if they are of the same type (:py:class:`Point`,
    :py:class:`CartesianPoint2D`, etc.) and if the points' have
    :py:attr:`coordinates` attributes of the same shape and values.

    Examples
    --------
    Create a :py:class:`CartesianPoint2D` with no location initialized:

    >>> print(mahautils.shape_designer.shapes.CartesianPoint2D())
    ()

    Create a :py:class:`CartesianPoint2D` with location specified by
    positional arguments:

    >>> print(mahautils.shape_designer.shapes.CartesianPoint2D(1, 2.3))
    (1.0, 2.3)
    >>> print(mahautils.shape_designer.shapes.CartesianPoint2D([4, 5]))
    (4.0, 5.0)
    >>> pnt = mahautils.shape_designer.shapes.CartesianPoint2D([6, 7])
    >>> print(mahautils.shape_designer.shapes.CartesianPoint2D(pnt))
    (6.0, 7.0)

    Create a :py:class:`CartesianPoint2D` with location specified by
    keyword arguments:

    >>> print(mahautils.shape_designer.shapes.CartesianPoint2D(x=1, y=2))
    (1.0, 2.0)
    """

    def __init__(self, *args: Union[Array_Float2, 'CartesianPoint2D', float],
                 **kwargs):
        """Defines a point in the 2D Cartesian coordinate system

        Creates a :py:class:`CartesianPoint2D` instance and optionally allows
        the user to define the location of the point.

        Parameters
        ----------
        args : list or tuple or CartesianPoint2D or float, optional
            Positional arguments provided when creating the point object.  See
            the "Notes" section for information on how to use positional
            arguments to specify the point location
        kwargs : Any, optional
            Keyword arguments provided when creating the point object.  See
            the "Notes" section for information on how to use keyword arguments
            to specify the point location

        Notes
        -----
        When creating a :py:class:`CartesianPoint2D` instance, it is possible
        to provide the point location using the constructor arguments.  This
        location can be provided using *either positional or keyword arguments,
        but not both*.

        If providing the location using positional arguments, then any of the
        following may be specified: (1) two floating-point numbers; (2) a list,
        tuple, NumPy array, or any other array-like object containing two
        floating-point numbers; or (3) another :py:class:`CartesianPoint2D`
        instance.

        If providing the location using keyword arguments, then *two* keyword
        arguments *must* be specified: ``x`` and ``y``.  Both arguments must
        be numeric types (integer or floating-point values).
        """
        super().__init__()

        # Variable that indicates whether the point coordinates have already
        # been stored
        stored_point = False

        # Store point location passed as positional arguments
        if len(args) > 0:
            # If user passed a list, tuple, or `CartesianPoint2D` instance,
            # directly store the point coordinates
            if len(args) == 1:
                self.coordinates = args[0]

            # If user passed individual point values, store them
            else:
                self.coordinates = args

            # Record that point location was stored
            stored_point = True

        # Store point location passed as keyword arguments
        if ('x' in kwargs) or ('y' in kwargs):
            # Check that the user didn't try to provide the point coordinates
            # using both positional and keyword arguments
            if stored_point:
                raise TypeError(
                    'Invalid input. Point location can be specified using '
                    'either positional or keyword arguments, but not both')

            # Verify that both x- and y-coordinates were provided
            if not (('x' in kwargs) and ('y' in kwargs)):
                raise TypeError(
                    'Invalid keyword arguments. If providing point location '
                    'using keyword arguments, both arguments "x" and "y" '
                    'must be provided')

            # Store point coordinates
            self.coordinates = (kwargs['x'], kwargs['y'])

            # Record that point location was stored
            stored_point = True

    @property
    def coordinates(self):
        """The coordinates of the point, represented as a tuple ``(x, y)``"""
        return super().coordinates

    @coordinates.setter
    def coordinates(self, coordinates: Union[Array_Float2, 'CartesianPoint2D']):
        if isinstance(coordinates, CartesianPoint2D):
            self._coordinates = coordinates.coordinates

        else:
            # Verify that two coordinates were provided
            try:
                # This does not use `assert` because `assert` statements can in
                # some cases be removed when compiling to optimized byte code
                if len(coordinates) != 2:
                    raise AssertionError(
                        'Length of provided coordinates must be 2, '
                        f'but {len(coordinates)} coordinate(s) were provided')
            except (AssertionError, TypeError) as exception:
                raise ValueError('Point coordinates must be a list or tuple '
                                 'of length 2') from exception

            # Convert coordinates to floating-point numbers and store values
            try:
                self._coordinates \
                    = (float(coordinates[0]), float(coordinates[1]))
            except (TypeError, ValueError) as exception:
                raise ValueError(
                    'All point coordinates must be of a numeric type '
                    '(float, int, etc.)') from exception

    def distance_to(self, point: Union[Array_Float2, 'CartesianPoint2D']):
        """Computes the distance to another point

        Calculates and returns the distance to another point in the same 2D
        Cartesian coordinate system.

        Parameters
        ----------
        point : list or tuple or CartesianPoint2D
            The point to which to calculate distance

        Returns
        -------
        float
            The distance to another location ``point`` in the 2D Cartesian
            plane
        """
        pnt = CartesianPoint2D(point)
        return math.sqrt((self.x - pnt.x)**2 + (self.y - pnt.y)**2)

    @property
    def x(self):
        """The x-coordinate of the point"""
        return self.coordinates[0]

    @property
    def y(self):
        """The y-coordinate of the point"""
        return self.coordinates[1]
