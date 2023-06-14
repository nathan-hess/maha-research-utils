"""**Tools for creating patterns of geometric shapes**

The :py:mod:`mahautils.shapes` module is intended to facilitate building
complex patterns of geometric shapes.  This can be useful when preparing
input files for simulations, such as files that specify port shapes and
locations for pumps and motors.
"""

from .canvas import Canvas
from .geometry import (
    CartesianPoint2D,
    CartesianPoint3D,
    Circle,
    ClosedShape2D,
    Geometry,
    OpenShape2D,
    Point,
    Polygon,
    Shape2D,
)
from .layer import Layer
