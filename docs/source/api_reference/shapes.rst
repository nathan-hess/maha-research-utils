.. spelling:word-list::

   args
   backend
   kwargs
   num


mahautils.shapes
================

.. automodule:: mahautils.shapes

.. currentmodule:: mahautils.shapes


Shapes
------

The classes below can be used to specify and generate geometric shapes.  These
objects provide the "backend" of the :py:mod:`mahautils.shapes` module,
and they are used by other tools in this module when generating geometry.

.. inheritance-diagram:: Geometry Point Shape2D ClosedShape2D OpenShape2D CartesianPoint2D Circle Polygon CartesianPoint3D
    :parts: 1

|


Abstract Geometry
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    Geometry
    Point

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    Shape2D
    ClosedShape2D
    OpenShape2D


2D Geometry
^^^^^^^^^^^

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    CartesianPoint2D
    Circle
    Polygon


3D Geometry
^^^^^^^^^^^

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    CartesianPoint3D


Layers and Canvases
-------------------

Layers and canvases are "collections" that store shapes and allow more complex,
multi-shape geometries to be constructed.  A layer is a group of shapes, and a
canvas is a group of layers.

For instance, in an axial piston pump, all of the high-pressure ports might be
grouped in a layer, all the low-pressure ports might be grouped in another
layer, and these two layers might be grouped into a single canvas (and different
canvases could be created for different simulation time steps).

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    Layer
    Canvas
