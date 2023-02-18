.. spelling:word-list::

   exps


mahautils.multics
=================

.. automodule:: mahautils.multics

.. currentmodule:: mahautils.multics


File Parsers
------------

The classes below can be used to read and/or write input and output files
for the Maha Multics software.

.. inheritance-diagram:: MahaMulticsConfigFile FluidPropertyFile SimResults VTKFile
    :parts: 1

|

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    MahaMulticsConfigFile
    FluidPropertyFile
    SimResults
    VTKFile


Unit Conversions
----------------

The classes below are customized versions of the unit converters found in the
`PyXX <https://github.com/nathan-hess/python-utilities>`__ package.  These
objects can perform any unit conversions allowed by the Maha Multics software,
and they allow users flexibility to define customized units.

.. autosummary::
    :toctree: ./api
    :template: ../_templates/api_reference_class_template.rst

    MahaMulticsUnitSystem
    MahaMulticsUnit
    MahaMulticsUnitConverter
