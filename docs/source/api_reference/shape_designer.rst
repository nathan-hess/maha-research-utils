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

.. inheritance-diagram:: shapes.Shape2D shapes.ClosedShape2D shapes.OpenShape2D
    :parts: 1

|

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    shapes.Shape2D
    shapes.ClosedShape2D
    shapes.OpenShape2D
