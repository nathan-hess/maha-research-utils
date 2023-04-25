"""**Shapes that can be used when constructing geometry with the MahaUtils
ShapeDesigner**

This module provides geometric shapes that can be used when creating more
complex geometry with the ShapeDesigner module.  The specification of the
shapes in this module is intended to be as generic and flexible as possible
to allow greater freedom in building complex geometry.
"""

from .circle import Circle
from .geometry import Geometry
from .point import Point
from .point2D import CartesianPoint2D
from .polygon import Polygon
from .shape import ClosedShape2D, OpenShape2D, Shape2D
