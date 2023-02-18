"""This module provides a class intended for reading and parsing fluid
property files used by the Maha Multics software.
"""

import copy
import pathlib
from typing import Optional, Union

import numpy as np

from .configfile import MahaMulticsConfigFile
from .exceptions import (
    FileNotParsedError,
    FluidPropertyFileError,
)


class FluidPropertyFile(MahaMulticsConfigFile):
    """An object representing a Maha Multics fluid properties file

    The Maha Multics software requires fluid properties to simulate
    lubrication behavior.  One method of providing fluid properties is with
    formatted fluid property files.  This class allows such files to be read
    so their properties can be viewed.
    """

    __file_format = (
        # Symbol   Description                         Units     Attribute name
        ('rho',    'density',                          'kg/m^3', '_density'      ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('K',      'bulk modulus',                     'Pa'    , '_bulk_modulus' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('nu',     'kinematic viscosity',              'm^2/s' , '_viscosity'    ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('cp',     'specific heat capacity',           'J/kg/K', '_specific_heat'),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('lambda', 'thermal conductivity',             'W/m/K' , '_thermal_cond' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('alpha',  'volumetric expansion coefficient', '1/K'   , '_expand_coeff' ),  # noqa: E202, E203, E501  # pylint: disable=C0301
        ('h',      'specific enthalpy',                'J/kg'  , '_enthalpy'     ),  # noqa: E202, E203, E501  # pylint: disable=C0301
    )

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None) -> None:
        super().__init__(path)

        # Initialize variables
        self._num_pressure: Union[int, None] = None
        self._num_temperature: Union[int, None] = None
        self._step_pressure: Union[float, None] = None
        self._step_temperature: Union[float, None] = None
        self._pressure_values: Union[np.ndarray, None] = None
        self._temperature_values: Union[np.ndarray, None] = None

        self._density: Union[np.ndarray, None] = None
        self._bulk_modulus: Union[np.ndarray, None] = None
        self._viscosity: Union[np.ndarray, None] = None
        self._specific_heat: Union[np.ndarray, None] = None
        self._thermal_conduct: Union[np.ndarray, None] = None
        self._expansion_coeff: Union[np.ndarray, None] = None
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

    def parse(self) -> None:
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
            raise ValueError(
                'Fluid property file temperature values do not have stated '
                f'temperature step (maximum difference: {max_diff})')

        max_diff = np.max(np.abs(
            (self._pressure_values[1:] - self._pressure_values[:-1])
            - self._step_pressure
        ))
        if max_diff > tolerance:
            raise ValueError(
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
