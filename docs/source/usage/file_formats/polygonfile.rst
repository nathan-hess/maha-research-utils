.. _fileref-polygon_file:

Polygon File
============

Maha Multics "polygon files" are used to store data about a set of polygons
whose vertices may change position over time.


Applications
------------

One of the most common use cases for polygon files is when defining boundary
conditions in lubricating films.  Often, there are known pressures in certain
geometric regions of the film (for instance, in the inlet and outlet ports),
and it is necessary to communicate these geometric conditions to the solver.
A polygon file can be a convenient way to provide this boundary condition.

.. dropdown:: Sample Application: Axial Piston Pump
    :animate: fade-in

    Suppose that you are simulating an `axial piston pump <https://en.wikipedia.org
    /wiki/Axial_piston_pump>`__, and you want to model the cylinder block-valve plate
    interface.

    In this interface, three boundary conditions are of interest, illustrated by
    the figure below.  Note that the geometry in the figure is not representative of
    any real pump; it is for illustration purposes only.  Additionally, while axial
    piston pumps typically have multiple displacement chambers, for simplicity only
    a single displacement chamber is shown in the figure.

    .. figure:: ./images/polygon_file_axial_piston_pump.png

    As seen in the figure above, three boundary conditions must be specified by
    defining polygon-shaped regions:

    - **Low-pressure port (shown in orange)**: This port can have **arbitrary
      shape**, so its location must be specified using a polygon with an
      arbitrary number of vertices.
    - **High-pressure ports (shown in yellow)**: These ports can have arbitrary
      shape, and since the high-pressure side of the valve plate in axial piston
      pumps typically has multiple ports separated by ribs for structural support,
      a **union of disjoint polygons** must be computed to accurately represent
      this boundary condition.
    - **Displacement chamber port (shown in purple)**: The displacement chamber
      port pressure is typically calculated separately from solving the partial
      differential equations (PDEs) governing the film; thus, this port pressure
      can be considered a boundary condition, like the high- and low-pressure
      ports.  An additional challenge is that this is a **moving boundary
      condition**, as the displacement chambers move following the rotation of
      the pump shaft (indicated by the purple arrow in the figure).

    Of course, boundary conditions must also be defined on the inner and outer
    radii of the lubricating film, but these don't need to be specified as
    arbitrary polygons, so they will not be discussed here.

    Once we have defined the shapes of each of these three ports as polygons at
    each time step of the simulation, we can apply a constant-pressure boundary
    condition to each polygon region and use this as a boundary condition to
    solve the governing PDEs in the film.  The polygon file discussed on this
    page addresses provides a data format that supports these needs.


Definitions
-----------

.. dropdown:: Polygon
    :animate: fade-in

    As discussed by `Wolfram MathWorld <https://mathworld.wolfram.com/Polygon.html>`__,
    there is no universally-accepted definition of a polygon.  The definition
    that the Maha Multics software uses a combination of elements of different
    definitions of a polygon from multiple sources.

    In general terms, the Maha Multics software defines a polygon as a closed,
    two-dimensional (2D) region bounded by a series of connected line segments
    that may or may not not intersect themselves.

    Put another way, a polygon can be considered the closed 2D region bounded
    by line segments connecting a cyclical series of points in order, where
    the boundary never intersects itself.


.. dropdown:: Point-in-Polygon Problem
    :animate: fade-in

    A `point-in-polygon problem <https://en.wikipedia.org/wiki/Point_in_polygon>`__
    is a geometric problem attempting to determine whether a given point is
    inside or outside a (possibly self-intersection) polygon.

    There are a number of algorithms that have been proposed for solving the
    point-in-polygon problem.  The Maha Multics software uses the `winding
    number algorithm <https://en.wikipedia.org/wiki/Point_in_polygon#Winding_number_algorithm>`__.

    For more detail on the point-in-polygon and winding number algorithm, refer to
    `this paper <https://www.engr.colostate.edu/~dga/documents/papers/point_in_polygon.pdf>`__.


File Format
-----------

A polygon file stores the :math:`x`- and :math:`y`-coordinates of one or more
polygons, at one or more instants in time.

The standard format of a polygon file is shown below.  Note that *the numbers
on the left-hand side are line numbers, and they are not part of the file*.

.. code-block:: text
    :linenos:

    [NUM_TIME_STEPS] [NUM_POLYGONS] [POLYGON_MERGE_METHOD]
    [TIME_UNIT]: [TIME_BEGIN] [TIME_STEP] [APPROX_METHOD]   <-- (omit if [NUM_TIME_STEPS] == 1)
    [NUM_COORDINATES] [IS_INSIDE]
    [X_COORDINATE_UNIT]: [X_1] [X_2] ... [X_M]  <-- (polygon 1)
    [Y_COORDINATE_UNIT]: [Y_1] [Y_2] ... [Y_M]
    ...
    [NUM_COORDINATES] [IS_INSIDE]
    [X_COORDINATE_UNIT]: [X_1] [X_2] ... [X_N]  <-- (polygon [NUM_POLYGONS])
    [Y_COORDINATE_UNIT]: [Y_1] [Y_2] ... [Y_N]
    ... (repeat highlighted lines 3-9 [NUM_TIME_STEPS] times)

Each parameter in the polygon file is explained in detail below.

.. dropdown:: ``[NUM_TIME_STEPS]``
    :animate: fade-in

    - **Type:** Integer
    - **Restrictions:** Must be greater than or equal to 1
    - **Required**: Yes

    Number of time steps stored in the polygon file.

    As explained, polygon files store data about polygon coordinates at one or
    more instants in time.  This parameter describes the number of time steps
    included in the file.

.. dropdown:: ``[NUM_POLYGONS]``
    :animate: fade-in

    - **Type:** Integer
    - **Restrictions:** Must be greater than or equal to 1
    - **Required**: No (default is 1 if not specified)

    Number of polygons at every time step.

    **The Maha Multics software requires that the same number of polygons are
    present at each time step**.  This parameter describes how many polygons
    are included for each time step.

.. dropdown:: ``[TIME_UNIT]``
    :animate: fade-in

    - **Type:** String
    - **Restrictions:** Must be a unit recognized by the Maha Multics software
    - **Required**: Yes if ``[NUM_TIME_STEPS] = 1``; otherwise omit this line

    Units of time for the polygon file.

    This parameter specifies the units which will be applied to the
    ``[TIME_BEGIN]`` and ``[TIME_STEP]`` parameters.

.. dropdown:: ``[TIME_BEGIN]``
    :animate: fade-in

    - **Type:** Floating-point number
    - **Restrictions:** Must be a real number
    - **Required**: Yes if ``[NUM_TIME_STEPS] = 1``; otherwise omit this line

    Initial time.

    This parameter specifies the time for the first set of polygons stored in
    the file.

.. dropdown:: ``[TIME_STEP]``
    :animate: fade-in

    - **Type:** Floating-point number
    - **Restrictions:** Must be a real number greater than 0

    Time step between each of the ``[NUM_POLYGONS]`` specified polygons.

    **The Maha Multics software assumes that there is a constant time step
    between each time step stored in polygon files.**  This parameter specifies
    this constant time step.

.. dropdown:: ``[APPROX_METHOD]``
    :animate: fade-in

    - **Type:** Integer
    - **Restrictions:** Must be one of: 0, 2, 3

    Describes how interpolation between time steps and extrapolation outside
    the defined time range are performed.

    The parameters ``[NUM_TIME_STEPS]``, ``[TIME_BEGIN]``, and ``[TIME_STEP]``
    specify a range of times over which polygons will be provided; let us
    denote this range :math:`t \in [t_{min}, t_{max}]`.  There are two issues
    that need to be addressed.  First, polygons are specified at a *discrete*
    number of time steps -- how do we *interpolate* between time steps?
    Second, suppose the time :math:`t` falls outside the range
    :math:`[t_{min}, t_{max}]` -- how do we *extrapolate*?

    **The Maha Multics software uses the same option to specify both
    interpolation and extrapolation behavior**.  Users can choose between
    the options in the table below.

    .. list-table::
        :header-rows: 1
        :widths: 5 7 8

        - * ``[APPROX_METHOD]``
          * Interpolation Behavior
          * Extrapolation Behavior
        - * **0** or **2** (nearest neighbor)
          * No interpolation, nearest neighbor
          * No extrapolation, nearest neighbor
        - * **3** (periodic)
          * No interpolation, nearest neighbor
          * Assume data are periodic.  See more detailed explanation below.

    **Periodic Extrapolation:** To perform "periodic" extrapolation, it is
    assumed that the data between :math:`t_{min}` and :math:`t_{max}` form
    a repeating cycle with period :math:`t_{max} - t_{max}`.  Thus, when
    attempting to extrapolate a value for time :math:`t`, the value of
    :math:`t` is modified as follows:

    .. math:: t = ((t - t_{min}) \% (t_{max} - t_{min})) + t_{min}
    
    Where :math:`\%` denotes the modulo operator.

    .. note::

        These options may seem illogical, but the reason is that these options
        are shared with other interpolation/extrapolation Maha Multics code.
        Thus, although values of ``0`` and ``2`` produce identical behavior
        for polygon files, for other applications these produce different
        results.  Similarly, this is why ``1`` is not an option -- it is an
        option for other code that performs interpolation/extrapolation, but
        not polygon files.

.. dropdown:: ``[NUM_COORDINATES]``
    :animate: fade-in

    - **Type:** Integer
    - **Restrictions:** Must be greater than or equal to 3

    The number of x- and y-coordinates that specifies each polygon at the
    given time step.

    This parameter should be provided at the beginning of data for each
    time step.  Polygons can be specified by an arbitrary number of points,
    and this parameter describes the number of x- and y-coordinates that will
    be used to define the boundary of all polygons for the corresponding time
    step.

    **The Maha Multics software requires that all polygons have the same number
    of coordinates at any given time step**.  There are cases when this is not
    advantageous, such as if polygons are of significantly different size;
    however, this is currently a limitation of Maha Multics.  It is possible to
    vary ``[NUM_COORDINATES]`` for different time steps, but it must be the same
    for all polygons at any given time step.

    Note that this information is technically redundant since the coordinates
    themselves are given.  However, this is a limitation of the Maha Multics
    software and must be included for the software to function.

.. warning::

    As explained above, the term "time" is used loosely with polygon files.  The
    measure of time does not necessarily need to be "physical time" (i.e.,
    measured in seconds).  Rather, it could be "time" measured as, for example,
    the rotation angle of a pump shaft (in which case ``[TIME_UNIT]`` might be
    ``degrees``).


Comments, Whitespace, and Line Endings
--------------------------------------

Comments should not be used in polygon files.

Items denoted "whitespace-separated" may be separated by either spaces
or tab (``\t``) characters.

Blank lines may be included but are not recommended.

On Linux and MacOS, LF line endings (``\n``) must be used.  On Windows,
either LF (``\n``) or CRLF (``\r\n``) line endings may be used.


Examples
--------

Single, Stationary Polygon
^^^^^^^^^^^^^^^^^^^^^^^^^^


Single, Moving Polygon
^^^^^^^^^^^^^^^^^^^^^^


Multiple, Stationary Polygons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
