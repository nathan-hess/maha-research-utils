"""This module provides a class intended for reading, parsing, and writing
files which store simulation results produced by the Maha Multics software.
"""

import pathlib
import re
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pyxx

from mahautils.dictionaries.dictionary import Dictionary
from .configfile import MahaMulticsConfigFile
from .exceptions import (
    FileNotParsedError,
    InvalidSimResultsFormatError,
)
from .units import MahaMulticsUnitConverter


class _SimResultsEntry:
    """An object for storing information about simulation results variables

    This class is intended used by :py:class:`SimResults` to store metadata
    and (possibly) simulation results data for variables in Maha Multics
    simulation results files.
    """

    def __init__(self,
                 required: bool,
                 units: str,
                 data: Optional[
                     Union[np.ndarray, List[float], Tuple[float, ...]]] = None,
                 description: Optional[str] = None,
                 group: Optional[str] = None,
                 ) -> None:
        self.data = data
        self.description = description
        self.group = group
        self.required = required
        self.units = units

    def __repr__(self) -> str:
        return (
            f'[{"Required" if self.required else "Optional"}] '
            f'[Units: {self.units}] '
            f'{self.description}, '
            f'{self.data}'
        )

    def __str__(self) -> str:
        return self.__repr__()


class SimResults(MahaMulticsConfigFile):
    """An object representing a Maha Multics simulation results file

    The Maha Multics software uses simulation results files to configure which
    simulation results will be generated and to store the results.  This class
    is capable of parsing such files and providing an interface through which
    users can interact with and manipulate data in the file.
    """

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None,
                 unit_converter: Optional[pyxx.units.UnitConverter] = None
                 ) -> None:
        super().__init__(path=path)

        # Initialize variables
        self._title: Union[str, None] = None
        self._compile_options: Dict[str, str] = {}
        self._data: Dictionary[str, _SimResultsEntry] = Dictionary()

        self._unit_converter = MahaMulticsUnitConverter() \
            if unit_converter is None else unit_converter

        # If path was provided, read file
        if path is not None:
            self.read(path)
            self.parse()

    @property
    def compile_options(self) -> Dict[str, str]:
        """A dictionary containing options with which the Maha Multics
        software was compiled

        Note that this dictionary is returned **by reference**, so modifying
        the returned value will modify the object attribute.
        """
        return self._compile_options

    @property
    def num_time_steps(self) -> int:
        """The number of time steps in the data array of the simulation
        results file"""
        if hasattr(self, '_num_time_steps'):
            return self._num_time_steps

        raise FileNotParsedError(
            'Attribute "num_time_steps" is not defined; file has not '
            'yet been parsed')

    @property
    def title(self) -> Union[str, None]:
        """A title describing the contents of the simulation results file"""
        return self._title

    @title.setter
    def title(self, title: Union[str, None]) -> None:
        if not isinstance(title, (str, type(None))):
            raise TypeError('Argument "title" must be of type "str"')

        self._title = title

    @property
    def unit_converter(self) -> pyxx.units.UnitConverter:
        """The unit converter used to convert the units of quantities stored
        in the simulation results file"""
        return self._unit_converter

    @property
    def vars(self) -> Tuple[str, ...]:
        """A tuple containing all variable names listed in the simulation
        results file

        This property contains all variables listed in the "printDict" section
        of the simulation results file.  There may or may not be simulation
        results data available for any given variable.
        """
        return tuple(self._data.keys())

    def parse(self) -> None:
        """Parses the file content in the :py:attr:`contents` list and
        populates attributes (such as :py:attr:`title`) with extracted data

        This method parses the data in :py:attr:`contents`, extracting
        configuration and simulation results data and storing it in this
        object's attributes for easier reading and editing.

        Note that calling this method will alter the data in
        :py:attr:`contents` (performs actions such as removing comments and
        blank lines).
        """
        # Verify that file contents have been read
        if len(self.contents) == 0:
            raise FileNotParsedError(
                'Unable to parse file. File has not yet been read')

        # Extract title
        for line in self.contents:
            if re.match(r'^\s*#\s*Title', line):
                self.title = line.split('Title:', maxsplit=1)[1].strip()
                break

            self.title = None

        # Extract options with which Maha Multics software was compiled
        for line in self.contents:
            if line.strip().startswith('#_OPTIONs:'):
                options_list = line.split('#_OPTIONs:', maxsplit=1)[1].split(',')

                for opt in options_list:
                    opt_parsed = [x.strip() for x in opt.split('=', maxsplit=1)]
                    self._compile_options[opt_parsed[0]] = opt_parsed[1]

                break

        # Pre-process input file (to prepare to read simulation results data)
        self.clean_contents(
            remove_comments         = True,
            skip_full_line_comments = False,
            strip                   = True,
            concat_lines            = False,
            remove_blank_lines      = True
        )

        # Extract list of variables in "printDict"
        sim_results_vars, idx, _ = self._extract_section_by_keyword(
            section_label      = 'printDict',
            begin_regex        = r'\s*printDict\s*{\s*',
            end_regex          = r'\s*}\s*',
            section_line_regex = r'\s*([@?])\s*([\w\d\._]+)\s+\[([^\s]+)\]\s*',
            max_sections       = 1,
        )

        for var in sim_results_vars:
            required_char, key, units = var.groups()

            if required_char == '@':
                required = True
            elif required_char == '?':
                required = False
            else:
                # This condition should never be reached (an error would have
                # been thrown when attempting to extract the section since the
                # regex wouldn't have matched) but it is included as a backup
                raise InvalidSimResultsFormatError(
                    f'Invalid character "{required_char}" indicating whether '
                    'a variable is required. The only valid characters are '
                    '"@" and "?"')  # pragma: no cover

            self._data[key] = _SimResultsEntry(required, units)

        # Extract simulation data
        self._num_time_steps = 0

        i = idx
        while i < len(self.contents):
            line = self.contents[i]

            if line.startswith('$'):
                # Parse list of variables for which simulation data
                # are present
                data_array_vars: List[List[str]] = [
                    var.split(':') for var in line.split('$')[1:]
                ]

                for var_data in data_array_vars:
                    if len(var_data) != 3:
                        raise InvalidSimResultsFormatError(
                            'In data array variable list, all entries should '
                            'be colon-separated key, units, and description. '
                            'The following variable does not fit this format: '
                            f'{":".join(var_data)}'
                        )

                    key = var_data[0]
                    units = var_data[1]
                    description = var_data[2]

                    if key not in self._data:
                        raise InvalidSimResultsFormatError(
                            f'Key "{key}" was found in simulation results data '
                            'array but not in "printDict" section'
                        )

                    if self._data[key].units != units:
                        raise InvalidSimResultsFormatError(
                            f'For key "{key}," units in "printDict" section '
                            f'({self._data[key].units}) and in data array '
                            f'section ({units}) do not match'
                        )

                    self._data[key].description = description

                    num_data_array_vars = len(data_array_vars)

                # Parse simulation data
                try:
                    data_array = np.transpose(np.array(
                        [x.split() for x in self.contents[i+1:]],
                        dtype=np.float64,
                    ))

                    if data_array.ndim != 2:
                        raise AssertionError(
                            'Simulation results data array must be 2D')

                    if data_array.shape[0] != num_data_array_vars:
                        raise AssertionError(
                            f'Expected {num_data_array_vars} in simulation '
                            'results data array, but found '
                            f'{data_array.shape[0]}'
                        )

                except (AssertionError, ValueError) as exception:
                    raise InvalidSimResultsFormatError(
                        'Unable to read simulation results data array'
                    ) from exception

                for i in range(num_data_array_vars):
                    key = data_array_vars[i][0]
                    self._data[key].data = data_array[i]

                # Store number of time steps of simulation results
                self._num_time_steps = data_array.shape[1]

                break

            i += 1
