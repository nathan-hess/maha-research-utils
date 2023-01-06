.. spelling:word-list::

    txt


Lookup Table File Format
========================

Lookup tables are common in numerical simulations, allowing discrete points of
empirical data or data calculated offline to be interpolated or extrapolated
and used during a simulation.

The Maha Multics software is capable of reading, storing, and retrieving data
from lookup tables of arbitrary dimensions.  This page discusses the format of
files that store data which can be used to populate such lookup tables.


Definitions
-----------

.. dropdown:: Independent and Dependent Variables
    :animate: fade-in

    In general, an **dependent variable** refers to a quantity whose value is
    determined by one or more **independent variables**.  Put a different way,
    the independent variables can be thought of as a "cause" or an "input" to
    a system, and the dependent variables would then be the "effect" or
    "output" that results from the values of the independent variables.

    In Maha Multics lookup tables, the independent variables are the values that
    the user knows, and the dependent variable is the quantity that is looked
    up *as a function of* the independent variables' values.

.. dropdown:: Dimension
    :animate: fade-in

    The dimension of a lookup table refers to the number of independent
    variables that need to be specified to retrieve a unique value (the
    dependent variable) from the lookup table.


Sample Application: Pump Efficiency
-----------------------------------

One potential application where Maha Multics lookup table files could be
used is to store efficiency data for a pump.  In fluid power models, it is
common to require hydromechanical and volumetric efficiencies as functions
of pump pressure and speed.  Several formats of lookup tables could be relevant
in this situation.

One option is to store the data in a **3D lookup table**.  In this case, both
efficiencies could be stored in the same table, with the following
dimensions: (1) pressure, (2) speed, and (3) which efficiency metric is of
interest (hydromechanical or volumetric).

Another option would be to store the data in two **2D lookup tables**.  One lookup
table could store the hydromechanical efficiency, and the other could store the
volumetric efficiency.  In both tables, the dimensions would be: (1) pressure
and (2) speed.

Notice that *there are multiple ways to store and retrieve data in lookup tables
that accomplish identical results*.  This page will not discuss how to choose
the *optimal* way, but will instead simply explain the file format that allows
such data to be stored and retrieved.


File Format
-----------

Suppose that we want to store a lookup table with ``N`` dimensions.  In general,
a lookup table file has the following format:

.. code-block:: text

    [DIM_SIZE_1] [DIM_SIZE_2] ... [DIM_SIZE_N]
    [DIM_1_UNIT]: [DIM_1_MIN] [DIM_1_STEP] [DIM_1_APPROX_METHOD]
    [DIM_2_UNIT]: [DIM_2_MIN] [DIM_2_STEP] [DIM_2_APPROX_METHOD]
    ...
    [DIM_N_UNIT]: [DIM_N_MIN] [DIM_N_STEP] [DIM_N_APPROX_METHOD]
    [DEPENDENT_VAR_UNIT_1]: [DEPENDENT_VAR_DATA_1] ...
    ...
    [DEPENDENT_VAR_UNIT_M]: [DEPENDENT_VAR_DATA_M] ...


A lookup table can be divided into three primary sections, each of which will be
discussed in detail below.

Section 1: Lookup Table Dimensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

    [DIM_SIZE_1] [DIM_SIZE_2] ... [DIM_SIZE_N]

The first section of the lookup table file defines the number ``N`` of dimensions
(independent variables) in the lookup table, as well as the number of points
in each dimension.

The "size" of each dimension refers to the number of values of the independent
variable at which the dependent variable is explicitly defined.

The sizes ``DIM_SIZE_1``, ``DIM_SIZE_2``, ..., ``DIM_SIZE_N`` of each of the ``N``
dimensions should be listed as **whitespace-separated** integers on a single line.


Section 2: Independent Variable Spacing and Approximation Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

    [DIM_1_UNIT]: [DIM_1_MIN] [DIM_1_STEP] [DIM_1_APPROX_METHOD]
    [DIM_2_UNIT]: [DIM_2_MIN] [DIM_2_STEP] [DIM_2_APPROX_METHOD]
    ...
    [DIM_N_UNIT]: [DIM_N_MIN] [DIM_N_STEP] [DIM_N_APPROX_METHOD]

The next section of the lookup table file provides the points (values of each
independent variable) at which the dependent variable is explicitly defined,
as well as the method for interpolating and/or extrapolating values along each
dimension of the lookup table.

There are several important pieces of information defined for each independent
variable dimension.  First, the independent variable can be assigned a unit,
specified by ``DIM_1_UNIT``, ``DIM_2_UNIT``, ..., ``DIM_N_UNIT`` for each of
the ``N`` independent variables.  Any valid unit defined in the simulation
``inputDict.txt`` can be provided.

Next, the independent variable spacing is defined similar to a combination of NumPy's
`arange <https://numpy.org/doc/stable/reference/generated/numpy.arange.html>`__ and
`linspace <https://numpy.org/doc/stable/reference/generated/numpy.linspace.html>`__
functions.  The minimum value of each independent variable is given by ``DIM_1_MIN``,
``DIM_2_MIN``, ..., ``DIM_N_MIN``, and the corresponding step (the difference between
adjacent values of the independent variable) is given by ``DIM_1_STEP``,
``DIM_2_STEP``, ..., ``DIM_N_STEP``.  **Maha Multics requires a constant "step size"
between values of all independent variables.**  Notice that these parameters,
combined with ``DIM_SIZE_1``, ``DIM_SIZE_2``, ..., ``DIM_SIZE_N`` from Section 1,
allow the independent variable values to be fully specified.

Finally, the last value provided on each line (``DIM_1_APPROX_METHOD``,
``DIM_2_APPROX_METHOD``, ..., ``DIM_N_APPROX_METHOD``) is the approximation
method used to interpolate and extrapolate values along the given dimension in
the lookup table.  That is, along each dimension, the lookup table contains a
discrete approximation of a function :math:`f(x)`.  Discrete values are
provided in the range :math:`x \in [x_{min}, x_{max}]` in the lookup table,
and the objective of the lookup table is to interpolate or extrapolate to
estimate :math:`f(x)` for any other :math:`x`.  The following approximation
methods are valid:

.. list-table::
    :header-rows: 1
    :widths: auto

    - * ``DIM_#_APPROX_METHOD``
        * Description
    - * **0** (nearest neighbor)
        * Nearest neighbor interpolation and extrapolation
    - * **1** (linear)
        * Linear interpolation and extrapolation
    - * **2** (saturation)
        * Linear interpolation; no extrapolation (:math:`f(x) = f(x_{min})` for
        :math:`x \le x_{min}` and :math:`f(x) = f(x_{max})` for :math:`x \ge x_{max}`)
    - * **3** (periodic)
        * Linear interpolation; to extrapolate, it is assumed that the dependent
        variable is periodic with period :math:`x_{max} - x_{min}` such that
        :math:`f(x) = f(((x - x_{min}) \% (x_{max} - x_{min})) + x_{min})`,
        where :math:`\%` denotes the modulo operator

All values should be **whitespace-separated**.


Section 3: Dependent Variable Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

    [DEPENDENT_VAR_UNIT_1]: [DEPENDENT_VAR_DATA_1] ...
    ...
    [DEPENDENT_VAR_UNIT_M]: [DEPENDENT_VAR_DATA_M] ...

The final section of a lookup table file contains the values of the dependent
variable.  The values of the dependent variable for *every possible combination
of the independent variables* must be specified.

Each line must begin with a unit ``DEPENDENT_VAR_UNIT_1``, ..., ``DEPENDENT_VAR_UNIT_M``
specifying the units in which the data *on that line* are stored.

The order in which the dependent variable values are given can be thought of
as resulting from fixing the independent variables "from right to left."  To be
exact:

- Consider the order in which the independent variables are specified on the
    first line of the lookup table file (which is the same order they are listed
    in Section 2 of the file).  First fix all dimensions ``2``, ``3``, ..., ``N``
    at their minimum values.
- On each row (after the unit), provide dependent variable values ``DEPENDENT_VAR_DATA_1``
    for every value of the dimension 1 **as whitespace-separated numbers**; that
    is, each row of this section should have ``DIM_SIZE_1`` values.
- Then, increment dimension 2 and add subsequent rows (``DIM_SIZE_1`` rows
    total) for each value of the second independent variable.
- Then, work "rightward" and increment dimension 3, and add rows for each value
    of dimension 2, and repeat for all ``DIM_SIZE_3`` values of dimension 3.
- Repeat this process until all ``N`` dimensions have been incremented.

For an example of how to implement this order, refer to the
:ref:`paragraph_fileformat_lookuptable_example3D` below.


Comments, Whitespace, and Line Endings
--------------------------------------

Any content on a line following a ``#`` character is ignored.  Full-line comments
(lines with no content other than a comment) are not permitted.

Items denoted "whitespace-separated" may be separated by either spaces
or tab (``\t``) characters.

Blank lines are not permitted.

On Linux and MacOS, LF line endings (``\n``) must be used.  On Windows,
either LF (``\n``) or CRLF (``\r\n``) line endings may be used.


Examples
--------

1D Lookup Table
^^^^^^^^^^^^^^^

One potential application of a 1D lookup table is to approximate a function of one
variable.  For instance, suppose we want to create a Maha Multics lookup table that
approximates :math:`f(x) = x^2` at :math:`x = 4, 5, 6, 7, 8, 9`.  For this example,
we'll assume that :math:`x` has units of ``mm`` and :math:`f(x)` has units of ``kg``.

In this case, we have one dimension, and the independent variable is defined at 6
values.  Therefore, ``DIM_SIZE_1 = 6``, ``DIM_1_MIN = 4``, and ``DIM_1_STEP = 1``.
Assuming that we want to use linear interpolation and "saturate" the dependent
variable at the boundary values, ``DIM_1_APPROX_METHOD = 2``.  Finally, the values
of :math:`f(x)` for :math:`x = 4, 5, 6, 7, 8, 9` are :math:`16, 25, 36, 49, 64, 81`,
respectively.

Combining all these results, the final lookup table file would be (the numbers at
the beginning of each line are line numbers, not part of the file):

.. code-block:: text
    :caption: lookup_table_1D.txt
    :linenos:

    6
    mm:  4  1  2
    kg:  16  25  36  49  64  81


2D Lookup Table
^^^^^^^^^^^^^^^

Next, consider a fluid power application: a hydraulic pump efficiency map.  For
this example, we'll assume that the efficiency is based on two parameters: the
pump speed and pressure.  A hypothetical (and very unrealistic) sample efficiency
map is shown below.

.. list-table::
    :header-rows: 1
    :stub-columns: 1

    * -
      - 200 rpm
      - 300 rpm
      - 400 rpm
      - 500 rpm
    * - 50 bar
      - 0.85
      - 0.86
      - 0.87
      - 0.88
    * - 75 bar
      - 0.89
      - 0.90
      - 0.91
      - 0.92
    * - 100 bar
      - 0.93
      - 0.94
      - 0.95
      - 0.96

To construct the Maha Multics lookup table file, first notice that there are two
independent variables: speed and pressure.

There are four speeds defined, each spaced at :math:`100\ rpm` intervals beginning at
:math:`200\ rpm`.  Thus, ``DIM_SIZE_1 = 4``, ``DIM_1_MIN = 200``, and ``DIM_1_STEP = 100``.
Assuming that we want to use linear interpolation and "saturate" the efficiency at
the maximum and minimum values defined in the lookup table, we would set
``DIM_1_APPROX_METHOD = 2``.

The second independent variable is pressure.  There are three pressure levels defined,
beginning at :math:`50\ bar` and spaced at :math:`25\ bar` intervals.  Thus,
``DIM_SIZE_2 = 3``, ``DIM_2_MIN = 50``, and ``DIM_2_STEP = 25``.  To use the same
methods for interpolation/extrapolation as speed, we could set ``DIM_2_APPROX_METHOD = 2``.

The complete lookup table file would be (the numbers at the beginning of each line
are line numbers, not part of the file):

.. code-block:: text
    :caption: lookup_table_2D.txt
    :linenos:

    4  3
    rpm:  200  100  2
    bar:  50   25   2
    -:  0.85  0.86  0.87  0.88
    -:  0.89  0.90  0.91  0.92
    -:  0.93  0.94  0.95  0.96


.. _paragraph_fileformat_lookuptable_example3D:

3D Lookup Table
^^^^^^^^^^^^^^^

Next, consider an extension of the 2D lookup table: suppose we now want to store
hydraulic pump efficiency maps at multiple points in time in the same file.  For
this example, we'll assume that the efficiency is based on three parameters: the
pump speed, pump pressure, and time :math:`t` that the pump has been operating.
A set of hypothetical (and very unrealistic) sample efficiency maps is shown below.

**Efficiency at t = 0**

.. list-table::
    :header-rows: 1
    :stub-columns: 1

    * -
      - 200 rpm
      - 300 rpm
      - 400 rpm
      - 500 rpm
    * - 50 bar
      - 0.85
      - 0.86
      - 0.87
      - 0.88
    * - 75 bar
      - 0.89
      - 0.90
      - 0.91
      - 0.92
    * - 100 bar
      - 0.93
      - 0.94
      - 0.95
      - 0.96

**Efficiency at t = 10 hours**

.. list-table::
    :header-rows: 1
    :stub-columns: 1

    * -
      - 200 rpm
      - 300 rpm
      - 400 rpm
      - 500 rpm
    * - 50 bar
      - 0.35
      - 0.36
      - 0.37
      - 0.38
    * - 75 bar
      - 0.39
      - 0.40
      - 0.41
      - 0.42
    * - 100 bar
      - 0.43
      - 0.44
      - 0.45
      - 0.46

To construct the Maha Multics lookup table file, first notice that there are three
independent variables: speed, pressure, and time.

The first two dimensions, speed and pressure, can be handled in exactly the same
way as the 2D lookup table example:

- There are four speeds defined, each spaced at :math:`100\ rpm` intervals beginning at
  :math:`200\ rpm`.  Thus, ``DIM_SIZE_1 = 4``, ``DIM_1_MIN = 200``, and ``DIM_1_STEP = 100``.
  Assuming that we want to use linear interpolation and "saturate" the efficiency at
  the maximum and minimum values defined in the lookup table, we would set
  ``DIM_1_APPROX_METHOD = 2``.
- The second independent variable is pressure.  There are three pressure levels defined,
  beginning at :math:`50\ bar` and spaced at :math:`25\ bar` intervals.  Thus,
  ``DIM_SIZE_2 = 3``, ``DIM_2_MIN = 50``, and ``DIM_2_STEP = 25``.  To use the same
  methods for interpolation/extrapolation as speed, we could set ``DIM_2_APPROX_METHOD = 2``.

The third independent variable, time, can be handled in nearly the same way as speed
and pressure.  There are two times defined, :math:`t = 0` and :math:`t = 10`, so
``DIM_SIZE_3 = 2``, ``DIM_3_MIN = 0``, and ``DIM_3_STEP = 10``.  Assuming we want to
use linear interpolation and extrapolation, we could set ``DIM_2_APPROX_METHOD = 1``.

The complete lookup table file would be (the numbers at the beginning of each line
are line numbers, not part of the file):

.. code-block:: text
    :caption: lookup_table_3D.txt
    :linenos:

    4  3  2
    rpm:  200  100  2
    bar:  50   25   2
    hr:   0    10   1
    -:  0.85  0.86  0.87  0.88
    -:  0.89  0.90  0.91  0.92
    -:  0.93  0.94  0.95  0.96
    -:  0.35  0.36  0.37  0.38
    -:  0.39  0.40  0.41  0.42
    -:  0.43  0.44  0.45  0.46

Notice how the data are grouped:

1. The lookup table file contains data for every possible combination of the
   independent variable values.
2. In Line 1, the independent variables are listed in the following order:
   speed (dimension 1), pressure (dimension 2), and time (dimension 3).
3. To add data to the table, we fix values from "right to left."  That is, first, we
   fix dimensions 2 and 3; we set pressure and time to their minimum values of
   :math:`50\ bar` and :math:`0\ hr`, respectively.  Then, the first line of
   data (Line 5) contains the (four) dependent variable values, one for each speed.
4. Next, we work "rightward," keeping dimension 3 (time) fixed at :math:`0\ hr`,
   but incrementing dimension 2 (pressure) to :math:`75\ bar`.  Then, Line 6 in the
   lookup table file contains data for this combination (:math:`0\ hr`, :math:`75\ bar`)
   for each of the four speeds.
5. Then, we repeat Step 4: increment pressure once again to :math:`100\ bar`, and
   Line 7 of the lookup table file contains the pump efficiency for each speed
   for :math:`0\ hr` and :math:`100\ bar`.
6. Now, we have added data for all possible combinations of pressure and speed
   for :math:`t = 0` in Lines 5-7.  Therefore, we work "rightward" once again, this
   time incrementing time to :math:`t = 10\ hr`.  We can then repeat Steps 3-5 to
   add three new lines to the lookup table file (Lines 8-10), containing the pump
   efficiencies for all combinations of speed and pressure for :math:`t = 10\ hr`.
7. This completes the 3D lookup table, but notice that had there been more than
   two time steps, we would simply have needed to repeat Steps 3-5 for each time
   step to add efficiencies for all combinations of speed and pressure.

Notice that although a 3D lookup table example was discussed, this methodology can
be extended to an arbitrary number of dimensions.  For a higher number of
dimensions, the pattern for the order in which data are stored is the same: fix
the independent variables "from right to left."  Each line contains dependent
variable values for each value of the first independent variable.  Successive lines
correspond to incrementing the second independent variable, followed by incrementing
the third, and so on.
