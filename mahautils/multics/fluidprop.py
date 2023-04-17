"""This module provides a class intended for reading and parsing fluid
property files used by the Maha Multics software.
"""

import copy
import pathlib
from typing import List, Optional, Tuple, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import numpy as np
import pyxx
import scipy.interpolate  # type: ignore

from mahautils.utils.arrays import to_np_1D_array
from .configfile import MahaMulticsConfigFile
from .exceptions import (
    FileNotParsedError,
    FluidPropertyFileError,
)

NumberOrNumericList = Union[float, np.ndarray, List[float], Tuple[float, ...]]


class FluidPropertyFile(MahaMulticsConfigFile):
    """An object representing a Maha Multics fluid properties file

    The Maha Multics software requires fluid properties to simulate
    lubrication behavior.  One method of providing fluid properties is with
    formatted fluid property files.  This class allows such files to be read
    so their properties can be viewed.

    Maha Multics fluid property files store the following properties:

    - Density
    - Bulk modulus
    - Kinematic viscosity
    - Specific heat capacity
    - Thermal conductivity
    - Volumetric expansion coefficient
    - Specific enthalpy
    """

    # Order and units of columns of data in fluid property files
    __file_format = (
        # Symbol   Description                         Units     Attribute name
        ('rho',    'density',                          'kg/m^3', '_density'      ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('k',      'bulk modulus',                     'Pa_a'  , '_bulk_modulus' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('nu',     'kinematic viscosity',              'm^2/s' , '_viscosity_k'  ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('cp',     'specific heat capacity',           'J/kg/K', '_specific_heat'),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('lambda', 'thermal conductivity',             'W/m/K' , '_thermal_cond' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('alpha',  'volumetric expansion coefficient', 'K^(-1)', '_expand_coeff' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('h',      'specific enthalpy',                'J/kg'  , '_enthalpy'     ),  # noqa: E202, E203, E501  # pylint: disable=C0301
    )

    # Default units of pressure and temperature in fluid property files
    __pressure_units = 'Pa_a'  # Pascals, absolute pressure
    __temperature_units = 'K'  # Kelvin

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None,
                 unit_converter: Optional[pyxx.units.UnitConverter] = None
                 ) -> None:
        """Creates an object that can read and write Maha Multics fluid
        property files

        Creates an instance of the :py:class:`FluidPropertyFile` class and
        optionally reads and parses a specified Maha Multics fluid property
        file.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename of the fluid property file to read and
            parse (default is ``None``).  If set to ``None``, no file is read
        unit_converter : pyxx.units.UnitConverter, optional
            A :py:class:`pyxx.units.UnitConverter` instance which will be
            used to convert units of quantities stored in the simulation
            results file (default is ``None``).  If set to ``None``, the
            :py:class:`MahaMulticsUnitConverter` unit converter will be used
            to perform unit conversions
        """
        super().__init__(path=path, unit_converter=unit_converter)

        # Initialize variables
        self._num_pressure: Union[int, None] = None
        self._num_temperature: Union[int, None] = None
        self._step_pressure: Union[float, None] = None
        self._step_temperature: Union[float, None] = None
        self._pressure_values: Union[np.ndarray, None] = None
        self._temperature_values: Union[np.ndarray, None] = None

        self._density: Union[np.ndarray, None] = None
        self._bulk_modulus: Union[np.ndarray, None] = None
        self._viscosity_k: Union[np.ndarray, None] = None
        self._specific_heat: Union[np.ndarray, None] = None
        self._thermal_conduct: Union[np.ndarray, None] = None
        self._expand_coeff: Union[np.ndarray, None] = None
        self._enthalpy: Union[np.ndarray, None] = None

        # If path was provided, read file
        if path is not None:
            self.read(path, parse=True)

    @property
    def num_pressure(self) -> int:
        """The number of (discrete) values of pressure for which fluid
        properties are defined in the file"""
        if self._num_pressure is None:
            raise FileNotParsedError('Attribute "num_pressure" is not defined; '
                                     'file has not yet been parsed')

        return self._num_pressure

    @property
    def num_temperature(self) -> int:
        """The number of (discrete) values of temperature for which fluid
        properties are defined in the file"""
        if self._num_temperature is None:
            raise FileNotParsedError('Attribute "num_temperature" is not '
                                     'defined; file has not yet been parsed')

        return self._num_temperature

    def get_pressure_step(self, units: str) -> float:
        """Returns the increments of pressure over which properties in the
        file are stored

        Fluid properties are stored in discrete increments of pressure.  This
        method returns this "step" or increment between pressure values.

        Parameters
        ----------
        units : str
            The units in which the pressure increment should be stored

        Returns
        -------
        float
            The pressure increment over which fluid properties are stored
        """
        if self._step_pressure is None:
            raise FileNotParsedError(
                'Cannot return pressure step; file has not yet been parsed')

        return float(self.unit_converter.convert(
            quantity  = self._step_pressure,
            from_unit = self.__pressure_units,
            to_unit   = units,
        ))

    def get_pressure_values(self, units: str) -> np.ndarray:
        """Returns the (discrete) pressure values over which properties in the
        file are stored

        Fluid properties are stored for discrete values of pressure.  This
        method returns all pressure values for which fluid properties are
        stored.

        Parameters
        ----------
        units : str
            The units in which the pressure values should be stored

        Returns
        -------
        np.ndarray
            The pressure values for which fluid properties are stored
        """
        if self._pressure_values is None:
            raise FileNotParsedError(
                'Cannot return pressure values; file has not yet been parsed')

        return self.unit_converter.convert(
            quantity  = self._pressure_values,
            from_unit = self.__pressure_units,
            to_unit   = units,
        )

    def get_temperature_step(self, units: str) -> float:
        """Returns the increments of temperature over which properties in the
        file are stored

        Fluid properties are stored in discrete increments of temperature.
        This method returns this "step" or increment between temperature
        values.

        Parameters
        ----------
        units : str
            The units in which the temperature increment should be returned

        Returns
        -------
        float
            The temperature increment over which fluid properties are stored
        """
        if self._step_temperature is None:
            raise FileNotParsedError(
                'Cannot return temperature step; file has not yet been parsed')

        return float(self.unit_converter.convert(
            quantity  = self._step_temperature,
            from_unit = self.__temperature_units,
            to_unit   = units,
        ))

    def get_temperature_values(self, units: str) -> np.ndarray:
        """Returns the (discrete) temperature values over which properties in
        the file are stored

        Fluid properties are stored for discrete values of temperature.  This
        method returns all temperature values for which fluid properties are
        stored.

        Parameters
        ----------
        units : str
            The units in which the temperature values should be stored

        Returns
        -------
        np.ndarray
            The temperature values for which fluid properties are stored
        """
        if self._temperature_values is None:
            raise FileNotParsedError(
                'Cannot return temperature values; file has not yet been parsed')

        return self.unit_converter.convert(
            quantity  = self._temperature_values,
            from_unit = self.__temperature_units,
            to_unit   = units,
        )

    def interpolate(self, fluid_property: str, output_units: str,
                    pressures: NumberOrNumericList, pressure_units: str,
                    temperatures: NumberOrNumericList, temperature_units: str,
                    interpolator_type: str, **kwargs,
                    ) -> np.ndarray:
        """Interpolates and/or extrapolates fluid property data for given
        pressures and temperatures

        Retrieves fluid property data from the file for given pressure(s) and
        temperature(s), interpolating and/or extrapolating if necessary.
        Interpolation is performed with the :py:mod:`scipy.interpolate` package
        (https://docs.scipy.org/doc/scipy/reference/interpolate.html).

        Parameters
        ----------
        fluid_property : str
            The name of the fluid property for which data should be returned
        output_units : str
            The units with which to return fluid property data
        pressures : float or np.ndarray or list or tuple
            The pressure(s) at which fluid properties should be returned.  See
            the "Notes" section for more information about required format
        pressure_units : str
            The units in which the ``pressures`` argument is provided
        temperatures : float or np.ndarray or list or tuple
            The temperature(s) at which fluid properties should be returned.
            See the "Notes" section for more information about required format
        temperature_units : str
            The units in which the ``temperatures`` argument is provided
        interpolator_type : str
            The SciPy interpolation function to use to perform interpolation.
            Can be selected from any of the options in the "Notes" section
        **kwargs
            Any keyword arguments to be supplied to the SciPy interpolation
            function specified by ``interpolator_type``.  See the "Notes"
            section for more information

        Returns
        -------
        np.ndarray
            The interpolated value(s) of the fluid properties given by
            ``fluid_property`` for the pressures and temperatures given
            by ``pressures`` and ``temperatures``, respectively.  See the
            "Notes" section for more information about the output data format

        Notes
        -----
        **Valid Fluid Properties**

        The table below summarizes valid inputs for the ``fluid_property``
        argument.

        .. list-table::
            :align: left
            :header-rows: 1
            :widths: auto

            * - Fluid Property
              - Valid ``fluid_property`` Inputs
              - Sample Units
            * - Density
              - ``rho``, ``density``
              - ``kg/m^3``
            * - Bulk modulus
              - ``k``, ``bulk modulus``
              - ``Pa_a``
            * - Kinematic viscosity
              - ``nu``, ``kinematic viscosity``
              - ``m^2/s``
            * - Specific heat capacity
              - ``cp``, ``specific heat capacity``
              - ``J/kg/K``
            * - Thermal conductivity
              - ``lambda``, ``thermal conductivity``
              - ``W/m/K``
            * - Volumetric expansion coefficient
              - ``alpha``, ``volumetric expansion coefficient``
              - ``1/K``
            * - Specific enthalpy
              - ``h``, ``specific enthalpy``
              - ``J/kg``
            * - Dynamic viscosity
              - ``mu``, ``dynamic viscosity``, ``absolute viscosity``
              - ``Pa_a*s``

        **Interpolation Functions**

        The following interpolation functions are available (set the
        ``interpolator_type`` argument to the given string to use each):

        - ``'interpn'``: The :py:class:`scipy.interpolate.interpn` function
          for multidimensional interpolation on rectangular grids (`reference
          <https://docs.scipy.org/doc/scipy/reference/generated
          /scipy.interpolate.interpn.html>`__)
        - ``'griddata'``: The :py:class:`scipy.interpolate.griddata`
          interpolation function for unstructured, multivariate interpolation
          (`reference <https://docs.scipy.org/doc/scipy/reference/generated
          /scipy.interpolate.griddata.html>`__)
        - ``'RBFInterpolator'``: The :py:class:`scipy.interpolate.RBFInterpolator`
          function for unstructured, multivariate interpolation using a radial
          basis function (`reference <https://docs.scipy.org/doc/scipy/reference
          /generated/scipy.interpolate.RBFInterpolator.html>`__)
        - ``'CloughTocher2DInterpolator'``: The
          :py:class:`scipy.interpolate.CloughTocher2DInterpolator`
          function for unstructured, multivariate interpolation using a
          piecewise cubic, :math:`C^1` smooth, curvature-minimizing interpolant
          (`reference <https://docs.scipy.org/doc/scipy/reference/generated
          /scipy.interpolate.CloughTocher2DInterpolator.html>`__)

        Review the SciPy documentation for questions about parameters for the
        interpolation functions.  *Some of these interpolation functions
        require users to set* ``kwargs`` *to meet specific mathematical
        requirements, and errors may be encountered if such requirements are
        not met.*

        **Formatting of Pressure and Temperature Inputs**

        Interpolation can be performed for one or more pressures and/or
        temperatures with a single call of the :py:meth:`interpolate` method.
        The table below specifies the valid format of the ``pressures`` and
        ``temperatures`` arguments, and the corresponding format of data that
        would be returned by each selection of inputs.

        .. list-table::
            :align: left
            :header-rows: 1
            :widths: auto

            * - Input: ``pressures``
              - Input: ``temperatures``
              - Output Shape
              - Notes
            * - ``float``
              - ``float``
              - ``(1,)``
              - Returns the interpolated property at the input pressure and
                temperature
            * - ``list`` (length ``n``)
              - ``float``
              - ``(n,)``
              - Returns the interpolated property at every value of
                ``pressures`` for the specified temperature
            * - ``float``
              - ``list`` (length ``n``)
              - ``(n,)``
              - Returns the interpolated property at every value of
                ``temperatures`` for the specified pressure
            * - ``list`` (length ``n``)
              - ``list`` (length ``n``)
              - ``(n,)``
              - Input lists **must** have equal length.  Component ``i`` of
                the returned array is interpolated for ``pressures[i]`` and
                ``temperatures[i]``

        Note that a length-1 list is considered equivalent to ``float`` in the
        table above.  Also, NumPy arrays or tuples can be used in place of
        ``list`` above.
        """
        fluid_property = str(fluid_property).lower()

        for _, _, _, attr in self.__file_format:
            if getattr(self, attr) is None:
                raise FileNotParsedError(
                    'Unable to interpolate fluid properties; file has not '
                    'been read/parsed')

        if (self._pressure_values is None) or (self._temperature_values is None):
            raise FileNotParsedError(
                'Unable to interpolate fluid properties; file has not '
                'been read/parsed')

        # Convert pressures and temperatures to NumPy arrays
        pressures = to_np_1D_array(pressures, dtype=np.float64)
        temperatures = to_np_1D_array(temperatures, dtype=np.float64)

        num_pressures = len(pressures)
        num_temperatures = len(temperatures)

        # Check that input array sizes are compatible
        if (
            (num_pressures > 1) and (num_temperatures > 1)
            and (num_pressures != num_temperatures)
        ):
            raise ValueError(
                'Pressure and temperature arrays both have lengths greater '
                'than 1, but their lengths are not equal')

        # Ensure pressure and temperature arrays have the same size
        if (num_pressures > 1) and (num_temperatures == 1):
            temperatures = np.repeat(temperatures, num_pressures)

        elif ((num_temperatures > 1) and (num_pressures == 1)):
            pressures = np.repeat(pressures, num_temperatures)

        # Retrieve data to interpolate/extrapolate
        data: np.ndarray = np.array([])
        data_units = ''

        success = False
        for symbol, desc, units, attr in self.__file_format:
            if fluid_property in (symbol, desc):
                data = getattr(self, attr)
                data_units = units

                success = True
                break

        if not success:
            if fluid_property in ('mu', 'absolute viscosity',
                                  'dynamic viscosity'):
                data = np.multiply(self._density, self._viscosity_k)  # type: ignore
                data_units \
                    = f'{self.__file_format[0][2]}*{self.__file_format[2][2]}'

                success = True

        if not success:
            raise ValueError(f'Invalid fluid property "{fluid_property}"')

        # Perform interpolation/extrapolation
        pressures = self.unit_converter.convert(
            quantity  = pressures,
            from_unit = pressure_units,
            to_unit   = self.__pressure_units
        )
        temperatures = self.unit_converter.convert(
            quantity  = temperatures,
            from_unit = temperature_units,
            to_unit   = self.__temperature_units
        )

        if interpolator_type == 'interpn':
            output_data = scipy.interpolate.interpn(
                points = (self._temperature_values, self._pressure_values),
                values = data,
                xi     = np.transpose(np.array([temperatures, pressures])),
                **kwargs
            )

        elif interpolator_type in ('griddata', 'RBFInterpolator',
                                   'CloughTocher2DInterpolator'):
            mesh_p, mesh_t = np.meshgrid(self._pressure_values,
                                         self._temperature_values)
            mesh_points = np.transpose(np.array([mesh_t.flatten(),
                                                 mesh_p.flatten()]))
            data_flat = data.flatten()

            query_points = np.transpose(np.array([temperatures, pressures]))

            if interpolator_type == 'griddata':
                output_data = scipy.interpolate.griddata(
                    points = mesh_points,
                    values = data_flat,
                    xi     = query_points,
                    **kwargs
                )

            elif interpolator_type == 'RBFInterpolator':
                interpolator = scipy.interpolate.RBFInterpolator(
                    y = mesh_points,
                    d = data_flat,
                    **kwargs
                )

                output_data = interpolator(query_points)

            else:
                interpolator = scipy.interpolate.CloughTocher2DInterpolator(
                    points = mesh_points,
                    values = data_flat,
                    **kwargs
                )

                output_data = interpolator(query_points)

        else:
            raise ValueError(
                f'Interpolator "{interpolator_type}" is not supported')

        return self.unit_converter.convert(
            quantity  = output_data,
            from_unit = data_units,
            to_unit   = output_units,
        )

    def parse(self) -> None:
        """Parses the file content in the :py:attr:`contents` list and
        populates attributes (such as :py:attr:`title`) with extracted data

        This method parses the data in :py:attr:`contents`, extracting
        fluid property data and storing it in this object's attributes for
        easier reading and editing.
        """
        super().parse()
        original_contents = copy.deepcopy(self.contents)

        # Settings
        tolerance = 1e-8  # tolerance for equality of floating-point numbers

        # Remove comments from file
        self.clean_contents(
            remove_comments    = True,
            strip              = True,
            remove_blank_lines = True,
        )

        # READ PRESSURE AND TEMPERATURE METADATA
        if len(self.contents) < 6:
            raise FluidPropertyFileError(
                'Fluid property file is missing required lines listing '
                'temperature and pressure ranges')

        try:
            # Get number of temperature values and temperature step
            self._num_temperature = int(float(self.contents.pop(0)))
            self._step_temperature = float(self.contents.pop(0))

            # Get number of pressure values and pressure step
            self._num_pressure = int(float(self.contents.pop(0)))
            self._step_pressure = float(self.contents.pop(0))

            # Get list of all temperature and pressure values
            self._temperature_values = np.array(
                [float(i) for i in self.contents.pop(0).split()],
                dtype=np.float64,
            )
            self._pressure_values = np.array(
                [float(i) for i in self.contents.pop(0).split()],
                dtype=np.float64,
            )
        except ValueError as exception:
            raise FluidPropertyFileError(
                'Fluid property file is missing required temperature and '
                'pressure metadata') from exception

        # VALIDATE FILE FORMAT
        # Check that file has expected number of lines
        expected_len = self.num_pressure * self.num_temperature
        if len(self.contents) != expected_len:
            raise FluidPropertyFileError(
                f'Fluid property file has {len(self.contents)} lines of fluid '
                f'property data, but {expected_len} lines were expected')

        # Check that temperature and pressure steps match listed values
        max_diff = np.max(np.abs(
            (self._temperature_values[1:] - self._temperature_values[:-1])
            - self._step_temperature
        ))
        if max_diff > tolerance:
            raise FluidPropertyFileError(
                'Fluid property file temperature values do not have stated '
                f'temperature step (maximum difference: {max_diff})')

        max_diff = np.max(np.abs(
            (self._pressure_values[1:] - self._pressure_values[:-1])
            - self._step_pressure
        ))
        if max_diff > tolerance:
            raise FluidPropertyFileError(
                'Fluid property file pressure values do not have stated '
                f'pressure step (maximum difference: {max_diff})')

        # READ FLUID PROPERTY DATA
        num_samples = self.num_pressure * self.num_temperature

        # Read data from file
        try:
            raw_file_data = np.transpose(np.array(
                [line.strip().split() for line in self.contents],
                dtype=np.float64,
            ))
        except ValueError as exception:
            raise FluidPropertyFileError(
                'Unable to read fluid properties file: some data in the file '
                'are not numeric') from exception

        if raw_file_data.shape != (7, num_samples):
            raise FluidPropertyFileError(
                'Unable to read fluid properties file: data array has shape '
                f'{raw_file_data.shape}, but expected {(7, num_samples)}')

        # Store data -- columns correspond to different pressures, rows
        # correspond to different temperatures
        shape = (self.num_temperature, self.num_pressure)

        for i, prop in enumerate(self.__file_format):
            attr_name = prop[3]
            setattr(self, attr_name, np.reshape(raw_file_data[i], shape))

        self.contents.clear()
        self.contents.extend(original_contents)
