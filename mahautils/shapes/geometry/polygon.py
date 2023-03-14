"""Classes for representing a polygon

The classes in this module are intended to represent a polygon in the 2D
Cartesian coordinate system.
"""

import copy
from typing import List, Tuple, Union

import matplotlib.path
import numpy as np

from .point import Array_Float2, CartesianPoint2D, Point
from .shape import ClosedShape2D

ListOfPoints2D = Union[
    List[Array_Float2], Tuple[Array_Float2, ...], np.ndarray,
    List[Point], Tuple[Point, ...],
]


class Polygon(ClosedShape2D):
    """An object representing a closed polygon in the 2D Cartesian plane

    This class is intended to represent a polygon, comprised of the closed
    region inside a series of vertices connected by straight lines.  The
    locations of the vertices are arbitrary and edges of the polygon can
    self-intersect.

    Examples
    --------
    Create a triangle:

    >>> vertices = [[0, 0], [1, 0], [1, 2]]
    >>> triangle = mahautils.shapes.Polygon(vertices)

    View the points on the boundary of the polygon, optionally repeating the
    start/end point of the polygon:

    >>> triangle.points()
    (array([0., 0.]), array([1., 0.]), array([1., 2.]))
    >>> triangle.points(repeat_end=True)
    (array([0., 0.]), array([1., 0.]), array([1., 2.]), array([0., 0.]))

    Check whether a point is inside the polygon:

    >>> triangle.is_inside((0.5, 0.5))
    True
    >>> triangle.is_inside((0.5, 10))
    False
    """

    def __init__(self, vertices: ListOfPoints2D,
                 construction: bool = False) -> None:
        """Creates an object representing a polygon

        Parameters
        ----------
        vertices : list or tuple or np.ndarray
            A 2D array containing a set of 2D points representing the vertices
            of the polygon, in order
        construction : bool, optional
            Whether the shape is a "construction shape" meant for visual
            display but not functional geometry (default is ``False``)
        """
        # Mypy disabled as a workaround for python/mypy#3004
        self.vertices = vertices  # type: ignore

        super().__init__(
            default_num_coordinates=None,
            construction=construction,
        )

    @property
    def vertices(self) -> np.ndarray:
        """Returns a copy of a NumPy array containing the vertices of the
        polygon

        Even though polygons are a closed shape, points are stored in the
        :py:attr:`vertices` attribute such that the first and last point are
        **not** repeated.
        """
        return copy.deepcopy(self._vertices)

    @vertices.setter
    def vertices(self, vertices: ListOfPoints2D) -> None:
        try:
            # Convert "points" argument to NumPy array
            vertices_array = np.array([list(x) for x in vertices],
                                      dtype=np.float64)

            # Verify expected shape
            if (vertices_array.ndim != 2) or (vertices_array.shape[1] != 2):
                raise ValueError('Polygon vertices are not a 2D array')

        except (TypeError, ValueError) as exception:
            raise ValueError(
                'Invalid polygon vertex format. Polygon vertices must be a '
                'list of 2D points') from exception

        # If user repeated the first/last vertex, remove it before storing
        # internally
        if np.array_equal(vertices_array[0], vertices_array[-1]):
            vertices_array = vertices_array[:-1]

        self._vertices = vertices_array

        # Store Matplotlib Path object representing polygon
        self._matplotlib_path = matplotlib.path.Path(self._vertices)

    def is_inside(self, point: Union[Array_Float2, CartesianPoint2D],
                  perimeter_is_inside: bool = True) -> bool:
        if perimeter_is_inside:
            # Python stores floating-point numbers as doubles, so the decimal
            # precision is ~15 decimal places
            tolerance = 1e-15

            # Check whether point is within limits of floating-point precision
            # from border
            return any([
                self._matplotlib_path.contains_point(
                    point=list(point), radius=tolerance),
                self._matplotlib_path.contains_point(
                    point=list(point), radius=-tolerance),
            ])

        return self._matplotlib_path.contains_point(point=list(point), radius=0)

    def points(self, repeat_end: bool = False) -> Tuple[np.ndarray, ...]:
        return self._convert_xy_coordinates_to_points(repeat_end=repeat_end)

    def xy_coordinates(self, repeat_end: bool = False
                       ) -> Tuple[np.ndarray, np.ndarray]:
        points = self.vertices

        if repeat_end:
            points = np.concatenate([points, [points[0]]], axis=0)

        return (points[:, 0], points[:, 1])