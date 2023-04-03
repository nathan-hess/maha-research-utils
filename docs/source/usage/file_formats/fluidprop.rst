.. spelling:word-list::

    txt


.. _fileref-fluid_property_file:

Fluid Property File Format
==========================

Maha Multics fluid property files store discrete points of information about
fluid property files so that fluids can be simulated accurately.  This page
discusses the format of such files.


File Format
-----------

For the Maha Multics software, fluid properties are stored as a function of
pressure :math:`p` and temperature :math:`T`.

Seven fluid properties must be defined for each pressure and temperature:

- Density
- Bulk modulus
- Kinematic viscosity
- Specific heat capacity
- Thermal conductivity
- Volumetric expansion coefficient
- Specific enthalpy

The file format used to specify these properties is as follows:

.. code-block:: shell
    :caption: General Fluid Property File Format
    :linenos:

    [N_T]
    [T_step]
    [N_p]
    [p_step]
    [T_1] [T_2] ... [T_i] ... [T_{N_T}]
    [p_1] [p_2] ... [p_j] ... [p_{N_p}]
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_1
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_2
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_{N_p}
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_2, p = p_1
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_i, p = p_j
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_{N_T}, p = p_{N_p}

.. note::

    The "comments" (such as ``# T = T_1, p = p_1``) should NOT be included in
    actual fluid property files -- these are not permitted.  However, they are
    included in this documentation to aid in explaining the format.

As seen above, there are two main sections of the fluid property file: (1) a
header and (2) the fluid property data.  The following sections will explain
each of these in greater detail.


Section 1: Header
^^^^^^^^^^^^^^^^^

.. code-block:: shell
    :caption: Header
    :linenos:

    [N_T]
    [T_step]
    [N_p]
    [p_step]
    [T_1] [T_2] ... [T_i] ... [T_{N_T}]
    [p_1] [p_2] ... [p_j] ... [p_{N_p}]

All fluid property files must begin with a header.  The purpose of the header
is to specify the pressure and temperature values at which fluid properties in
the file will be defined.

The temperatures and pressures are specified by the following metadata in the
fluid property file:

- ``[N_T]``: The total number of temperature values for which fluid properties
  are defined in the file.
- ``[T_step]``: The (constant) increment between successive temperature values
  in the file.
- ``[N_p]``: The total number of pressure values for which fluid properties
  are defined in the file.
- ``[p_step]``: The (constant) increment between successive pressure values
  in the file.

After the metadata, two **whitespace-separated** lists must be included containing
all the temperature and pressure values, respectively, for which fluid properties
in the file will be defined.

- In the code snippets above, these are represented by ``[T_1] [T_2] ... [T_i] ... [T_{N_T}]``
  and ``[p_1] [p_2] ... [p_j] ... [p_{N_p}]``, respectively.
- The list of temperature and pressure values must have lengths ``N_T`` and ``N_p``,
  respectively.
- The difference between subsequent values in the temperature and pressure lists
  must be ``T_step`` and ``p_step``, respectively.

.. important::

    There are several important assumptions to be aware of in fluid property files:

    - The increments between successive pressure and temperature values must be
      equal (i.e., ``T_step`` and ``p_step`` must be constant).
    - The units of all temperature quantities must be **Kelvin** and the units of
      all pressure quantities must be **bar** (absolute pressure).

    These are limitations hard-coded into the Maha Multics software and are
    documented here for compatibility.

Note that it is *absolutely* redundant to include metadata about, for instance,
the number of temperature values as well as a list of all temperature values
in the header.  However, this is hard-coded into the Maha Multics software,
so for compatibility the file must contain this redundant information.


Section 2: Fluid Property Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell
    :caption: Fluid Property Data
    :linenos:

    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_1
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_2
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_1, p = p_{N_p}
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_2, p = p_1
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_i, p = p_j
    ...
    [rho] [k] [nu] [cp] [lambda] [alpha] [h]  # T = T_{N_T}, p = p_{N_p}

The second section of the fluid property file defines the values of fluid properties
for each combination of pressure and temperature specified in the header.

All of the following properties must be defined in the file and **must have the
units shown below**.  Note that the first column corresponds to the variables
used to represent each property in the code snippets above.

.. list-table::
    :align: left
    :header-rows: 1
    :widths: auto

    * -
      - Description
      - Required Units
    * - ``[rho]``
      - Density
      - :math:`kg/m^3`
    * - ``[k]``
      - Bulk modulus
      - :math:`Pa` (absolute pressure)
    * - ``[nu]``
      - Kinematic viscosity
      - :math:`m^2/s`
    * - ``[cp]``
      - Specific heat capacity
      - :math:`J/kg/K`
    * - ``[lambda]``
      - Thermal conductivity
      - :math:`W/m/K`
    * - ``[alpha]``
      - Volumetric expansion coefficient
      - :math:`K^{-1}`
    * - ``[h]``
      - Specific enthalpy
      - :math:`J/kg`

For each possible combination of pressure and temperature, the fluid properties
in the table above must be specified, in order, with a **whitespace-separated**
list.  The order of pressures and temperatures should be such that pressure
is the "inner loop."  Put differently, if writing a fluid property file, you
might use code similar to:

.. code-block:: text

    for T in (T_1, T_2, ..., T_{N_T}):
        for p in (p_1, p_2, ..., p_{N_p}):
            write(rho, k, nu, cp, lambda, alpha, h)


Comments, Whitespace, and Line Endings
--------------------------------------

Comments should not be used in fluid property files.

Items denoted "whitespace-separated" may be separated by either spaces
or tab (``\t``) characters.

Blank lines should not be included.

On Linux and MacOS, LF line endings (``\n``) must be used.  On Windows,
either LF (``\n``) or CRLF (``\r\n``) line endings may be used.


Example File
------------

Suppose we have the following fluid property data.  Note that the numbers are very
unrealistic but were chosen to make it easy to see how the tables translate into
the fluid property file format.

**T = 273 K**

+---------------------------------------------------+-----------------------------+
| Fluid Property                                    | Pressure                    |
|                                                   +---------+---------+---------+
|                                                   | 100 Pa  | 150 Pa  | 200 Pa  |
+===================================================+=========+=========+=========+
| Density (:math:`kg/m^3`)                          | 0.1     | 0.2     | 0.3     |
+---------------------------------------------------+---------+---------+---------+
| Bulk modulus (:math:`Pa`)                         | 1.1     | 1.2     | 1.3     |
+---------------------------------------------------+---------+---------+---------+
| Kinematic viscosity (:math:`m^2/s`)               | 2.1     | 2.2     | 2.3     |
+---------------------------------------------------+---------+---------+---------+
| Specific heat capacity (:math:`J/kg/K`)           | 3.1     | 3.2     | 3.3     |
+---------------------------------------------------+---------+---------+---------+
| Thermal conductivity (:math:`W/m/K`)              | 4.1     | 4.2     | 4.3     |
+---------------------------------------------------+---------+---------+---------+
| Volumetric expansion coefficient (:math:`K^{-1}`) | 5.1     | 5.2     | 5.3     |
+---------------------------------------------------+---------+---------+---------+
| Specific enthalpy (:math:`J/kg`)                  | 6.1     | 6.2     | 6.3     |
+---------------------------------------------------+---------+---------+---------+

**T = 303 K**

+---------------------------------------------------+-----------------------------+
| Fluid Property                                    | Pressure                    |
|                                                   +---------+---------+---------+
|                                                   | 100 Pa  | 150 Pa  | 200 Pa  |
+===================================================+=========+=========+=========+
| Density (:math:`kg/m^3`)                          | 10.1    | 10.2    | 10.3    |
+---------------------------------------------------+---------+---------+---------+
| Bulk modulus (:math:`Pa`)                         | 11.1    | 11.2    | 11.3    |
+---------------------------------------------------+---------+---------+---------+
| Kinematic viscosity (:math:`m^2/s`)               | 12.1    | 12.2    | 12.3    |
+---------------------------------------------------+---------+---------+---------+
| Specific heat capacity (:math:`J/kg/K`)           | 13.1    | 13.2    | 13.3    |
+---------------------------------------------------+---------+---------+---------+
| Thermal conductivity (:math:`W/m/K`)              | 14.1    | 14.2    | 14.3    |
+---------------------------------------------------+---------+---------+---------+
| Volumetric expansion coefficient (:math:`K^{-1}`) | 15.1    | 15.2    | 15.3    |
+---------------------------------------------------+---------+---------+---------+
| Specific enthalpy (:math:`J/kg`)                  | 16.1    | 16.2    | 16.3    |
+---------------------------------------------------+---------+---------+---------+

In this example, there are ``N_T = 2`` temperature values (273 K and 303 K) and
``N_p = 3`` pressure values (100, 150, and 200 Pa).  The fluid property file that
stores these data would be:

.. code-block:: text
    :caption: fluid_properties.txt

    2
    30
    3
    50
    273  303
    100  150  200
    0.1  1.1  2.1  3.1  4.1  5.1  6.1
    0.2  1.2  2.2  3.2  4.2  5.2  6.2
    0.3  1.3  2.3  3.3  4.3  5.3  6.3
    10.1  11.1  12.1  13.1  14.1  15.1  16.1
    10.2  11.2  12.2  13.2  14.2  15.2  16.2
    10.3  11.3  12.3  13.3  14.3  15.3  16.3
