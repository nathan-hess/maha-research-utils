"""**Shapes that can be used when constructing geometry with MahaUtils**

This module provides geometric shapes that can be used when creating more
complex geometry (for instance, to write Maha Multics polygon files).  The
specification of the shapes in this module is intended to be as generic and
flexible as possible to allow greater freedom in building complex geometry.
"""

from .circle import Circle
from .geometry import Geometry
from .point import Point
from .point2D import CartesianPoint2D
from .point3D import CartesianPoint3D
from .polygon import Polygon
from .shape import Shape2D
from .shape_open_closed import ClosedShape2D, OpenShape2D
