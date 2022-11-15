.. spelling:word-list::

   args
   backend
   kwargs


mahautils.shape_designer
========================

.. automodule:: mahautils.shape_designer

.. currentmodule:: mahautils.shape_designer


Shapes
------

The classes below can be used to specify and generate geometric shapes.  These
objects provide the "backend" of the :py:mod:`mahautils.shape_designer` module,
and they are used by other tools in this module when generating geometry.

Points
^^^^^^

.. inheritance-diagram:: shapes.Point shapes.CartesianPoint2D
    :parts: 1

|

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    shapes.Point
    shapes.CartesianPoint2D


2D Shapes
^^^^^^^^^

.. inheritance-diagram:: shapes.Shape2D shapes.ClosedShape2D shapes.OpenShape2D shapes.Circle
    :parts: 1

|

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    shapes.Shape2D
    shapes.ClosedShape2D
    shapes.OpenShape2D
    shapes.Circle


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
