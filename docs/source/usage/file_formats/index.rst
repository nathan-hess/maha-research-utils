.. include:: ../../constants.rst


.. _section-file_formats:

Maha Multics File Formats
=========================

One of the main tools included in |PackageNameStylized| are a series of file
parsers for various input and output files used by the Maha Multics software.
This section provides details of the required format of each file and the
terminology used in describing the file formats, which may be used elsewhere
in the documentation.

.. important::

    While reading through these reference pages, you may notice that there
    are certain aspects of the Maha Multics-formatted files that are not
    optimal (i.e., there's a better way to store the data).  This is
    frequently the case; however, these are limitations of the Maha Multics
    software.

    This package merely seeks to describe how to parse and write files in a
    format compatible with the Maha Multics software, so these reference
    pages do not discuss the optimal way to store data, but rather how data
    are currently stored in files used by the Maha Multics software.

|

.. toctree::
    :caption: File Format Specifications
    :maxdepth: 1

    lookuptable
    polygonfile
