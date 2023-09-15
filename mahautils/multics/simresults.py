"""This module provides a class intended for reading, parsing, and writing
files which store simulation results produced by the Maha Multics software.
"""

import copy
import pathlib
import re
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pyxx

from mahautils.utils.dictionary import Dictionary
from .configfile import MahaMulticsConfigFile
from .exceptions import (
    InvalidSimResultsFormatError,
    SimResultsError,
    SimResultsDataNotFoundError,
    SimResultsKeyError,
    SimResultsOverwriteError,
)


class _SimResultsEntry:
    """An object for storing information about simulation results variables

    This class is intended used by :py:class:`SimResults` to store metadata
    and (possibly) simulation results data for variables in Maha Multics
    simulation results files.
    """

    # Whether to include raw data when converting `_SimResultsEntry` objects
    # to a printable string representation
    show_data = True

    def __init__(self,
                 required: bool,
                 units: str,
                 data: Optional[
                     Union[np.ndarray, List[float], Tuple[float, ...]]] = None,
                 description: Optional[str] = None,
                 group: Optional[str] = None,
                 ) -> None:
        # Mypy exclusions in constructor were added as workarounds
        # for python/mypy#3004
        self.data = data  # type: ignore
        self.description = description
        self.group = group
        self.required = required
        self.units = units

    def __repr__(self) -> str:
        representation = (
            f'[{"Required" if self.required else "Optional"}] '
            f'[Units: {self.units}]'
        )

        if self.description is not None:
            representation += f' {self.description}'

            if (self.show_data) and (self.data is not None):
                representation += ','

        if (self.show_data) and (self.data is not None):
            array_str = np.array2string(self.data, precision=2)
            representation += f' {array_str}'

        return representation

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def data(self) -> Union[np.ndarray, None]:
        """A time series of simulation results data for the given variable"""
        return self._data

    @data.setter
    def data(self,
             data: Optional[Union[
                 np.ndarray, List[float], Tuple[float, ...]]]
             ) -> None:
        if data is None:
            self._data = None
        else:
            self._data = np.array(data, dtype=np.float64)

            if self._data.ndim != 1:
                raise ValueError('Simulation results data must be 1D')

    @property
    def description(self) -> Union[str, None]:
        """A string describing the variable"""
        return self._description

    @description.setter
    def description(self, description: Optional[str]) -> None:
        if description is None:
            self._description = None
        else:
            self._description = str(description)

    @property
    def group(self) -> Union[str, None]:
        """A string identifying a group to which multiple simulation results
        variables may belong"""
        return self._group

    @group.setter
    def group(self, group: Optional[str]) -> None:
        if group is None:
            self._group = None
        else:
            self._group = str(group)

    @property
    def required(self) -> bool:
        """Whether the Maha Multics software is required to output data for
        the simulation results variable when running

        If unable to output the variable, the Maha Multics software should
        exit with error.
        """
        return self._required

    @required.setter
    def required(self, required: bool) -> None:
        self._required = bool(required)

    @property
    def units(self) -> str:
        """The units of the data stored for the simulation results variable"""
        return self._units

    @units.setter
    def units(self, units: str) -> None:
        self._units = str(units)


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
        """Creates an object that can read and write Maha Multics simulation
        results files

        Creates an instance of the :py:class:`SimResults` class and optionally
        reads and parses a specified Maha Multics simulation results file.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename of the simulation results file to read and
            parse (default is ``None``).  If set to ``None``, no file is read
        unit_converter : pyxx.units.UnitConverter, optional
            A :py:class:`pyxx.units.UnitConverter` instance which will be
            used to convert units of quantities stored in the simulation
            results file (default is ``None``).  If set to ``None``, the
            :py:class:`MahaMulticsUnitConverter` unit converter will be used
            to perform unit conversions
        """
        super().__init__(path=path, unit_converter=unit_converter)

        self.__printdict_begin_regex = r'^\s*printDict\s*{\s*'
        self.__printdict_end_regex = r'^\s*}\s*$'

        self.__maha_multics_version_identifier = 'Multics Version'
        self.__maha_multics_commit_identifier = 'Multics Git Commit Hash'
        self.__sim_version_identifier = 'Main Sketch Version'

        # Initialize variables
        self._compile_options: Dict[str, str] = {}
        self._data: Dictionary[str, _SimResultsEntry] = Dictionary(
            custom_except_class=SimResultsKeyError,
            custom_except_msg='Variable "%s" not found in simulation results file'
        )
        self._maha_multics_commit: Union[str, None] = None
        self._maha_multics_version: Union[str, None] = None
        self._num_time_steps: int = 0
        self._sim_version: Union[str, None] = None
        self._title: Union[str, None] = None
        self.trailing_newline = True

        # If path was provided, read file
        if path is not None:
            self.read(path, parse=True)

    def __repr__(self) -> str:
        representation = [
            f'{self.__class__}',
            f'Title:      {self.title}',
        ]

        representation.append(f'Time steps: {self.num_time_steps}')

        representation.extend([
            f'Hashes:     {self.hashes}',
            '',
            self.__str__(),
        ])

        return '\n'.join(representation)

    def __str__(self) -> str:
        _SimResultsEntry.show_data = True
        return self.__get_printable_vars_str(self.variables)

    @property
    def compile_options(self) -> Dict[str, str]:
        """A dictionary containing options with which the Maha Multics
        software was compiled

        Note that this dictionary is returned **by reference**, so modifying
        the returned value will modify the object attribute.
        """
        return self._compile_options

    @property
    def maha_multics_commit(self) -> Union[str, None]:
        """The Git commit hash of the Maha Multics software with which the simulation
        was compiled"""
        return self._maha_multics_commit

    @maha_multics_commit.setter
    def maha_multics_commit(self, maha_multics_commit: Union[str, None]) -> None:
        if not isinstance(maha_multics_commit, (str, type(None))):
            raise TypeError('Argument "maha_multics_commit" must be of type '
                            '"str" or "None"')

        self._maha_multics_commit = maha_multics_commit

    @property
    def maha_multics_version(self) -> Union[str, None]:
        """The version of the Maha Multics software with which the simulation
        was compiled"""
        return self._maha_multics_version

    @maha_multics_version.setter
    def maha_multics_version(self, maha_multics_version: Union[str, None]) -> None:
        if not isinstance(maha_multics_version, (str, type(None))):
            raise TypeError('Argument "maha_multics_version" must be of type '
                            '"str" or "None"')

        self._maha_multics_version = maha_multics_version

    @property
    def num_time_steps(self) -> int:
        """The number of time steps in the data array of the simulation
        results file"""
        return self._num_time_steps

    @property
    def sim_version(self) -> Union[str, None]:
        """The simulation version of the ``main.cpp`` file which was used to
        generate the data in the simulation results file"""
        return self._sim_version

    @sim_version.setter
    def sim_version(self, sim_version: Union[str, None]) -> None:
        if not isinstance(sim_version, (str, type(None))):
            raise TypeError('Argument "sim_version" must be of type '
                            '"str" or "None"')

        self._sim_version = sim_version

    @property
    def title(self) -> Union[str, None]:
        """A title describing the contents of the simulation results file"""
        return self._title

    @title.setter
    def title(self, title: Union[str, None]) -> None:
        if not isinstance(title, (str, type(None))):
            raise TypeError('Argument "title" must be of type "str" or "None"')

        self._title = title

    @property
    def variables(self) -> Tuple[str, ...]:
        """A tuple containing all variable names listed in the simulation
        results file

        This property contains all variables listed in the "printDict" section
        of the simulation results file.  There may or may not be simulation
        results data available for any given variable.
        """
        return tuple(self._data.keys())

    def __get_printable_vars_str(self,
                                 variables: Union[List[str], Tuple[str, ...]],
                                 indent: int = 2
                                 ) -> str:
        if len(variables) == 0:
            representation = '[No simulation results variables found]'

        else:
            max_key_len = pyxx.arrays.max_list_item_len(variables)

            representation = ''

            for group in (list(self.list_groups()) + [None]):
                var_str = [group if group is not None else 'No Group Assigned']

                for var in variables:
                    if self._data[var].group == group:
                        var_str.append(
                            f'{" "*indent}{var:{max_key_len+1}s}: '
                            f'{str(self._data[var])}'
                        )

                if len(var_str) > 1:
                    representation += '\n'.join(var_str) + '\n'

        return representation.strip('\n')

    def __parse_metadata_comment(self, identifier: str) -> Union[str, None]:
        for line in self.contents:
            if re.match(r'^\s*#\s*' + re.escape(identifier) + r'\:', line):
                return line.split(f'{identifier}:', maxsplit=1)[1].strip()

        return None

    def _remove_vars_with_asterisk(self) -> None:
        # Extract names of all simulation results variables whose data are
        # included in the file
        data_vars: List[str] = []
        i = 0
        while i < len(self.contents):
            if (line := self.contents[i]).startswith('$'):
                data_vars = [var.split(':')[0] for var in line.split('$')[1:]]
                break

            i += 1

        i = 0
        while i < len(self.contents):
            line = self.contents[i]

            if (
                groups := re.search(self.__printdict_begin_regex + r'(.*)', line)
            ) is not None:
                if (line := groups.groups()[-1]) != '':
                    self.contents[i] = 'printDict{'
                    self.contents.insert(i + 1, '    ' + line)

                i += 1
                line = self.contents[i]

                while not re.match(self.__printdict_end_regex, line):
                    # Identify problematic keys (with asterisks)
                    line_groups = re.search(
                        r'^\s*([@?])\s*([\w\d\._\*\(\,\)]+)\s+\[([^\s]+)\]\s*$',
                        line)

                    # If key with asterisk was found, remove it and replace
                    # with simulation results variables
                    if line_groups is not None:
                        asterisk_key = line_groups.group(2)

                        if '*' in asterisk_key:
                            if len(data_vars) == 0:
                                raise SimResultsDataNotFoundError(
                                    'Simulation results files with asterisks (*) '
                                    'in variable names can only be read if the '
                                    'line beginning with "$" providing detailed '
                                    'variable names and descriptions is present')

                            # Find any matching simulation results variables
                            asterisk_seqs = (
                                re.findall(r'\*\(\d+\,\d+\)', asterisk_key)
                                + ['**']
                            )

                            key_regex = asterisk_key
                            for seq in asterisk_seqs:
                                key_regex = key_regex.replace(seq, '*')

                            key_regex = re.escape(key_regex).replace(r'\*', r'\d+')

                            matching_keys = []
                            for var in data_vars:
                                if re.match(key_regex, var):
                                    matching_keys.append(var)

                            matching_keys.reverse()

                            # Add matching simulation results variables to file
                            del self.contents[i]

                            for var in matching_keys:
                                self.contents.insert(
                                    i, line.replace(asterisk_key, var))

                            i += len(matching_keys) - 1

                    i += 1
                    line = self.contents[i]

                # Coverage.py is unable to detect 'break' statements
                # https://github.com/nedbat/coveragepy/issues/772
                break  # pragma: no cover

            i += 1

    def append(self, key: str, required: bool, units: str,
               data: Optional[
                   Union[np.ndarray, List[float], Tuple[float, ...]]] = None,
               description: Optional[str] = None,
               group: Optional[str] = None,
               ) -> None:
        """Adds a variable to the simulation results file

        Adds a new variable to the simulation results file, placing it at the
        end of the :py:attr:`variables` list.

        Parameters
        ----------
        key : str
            A unique name to identify the variable
        required : bool
            Whether the simulation results variable is required to be
            outputted by Maha Multics
        units : str
            The units of the variable's data
        data : np.ndarray or list or tuple, optional
            If desired, a 1D array consisting of the simulation results data
            for the variable can be provided (default is ``None``)
        description : str, optional
            An optional description of the simulation results variable
            (default is ``None``)
        group : str, optional
            An optional group to which the variable belongs (default is
            ``None``)

        Raises
        ------
        SimResultsOverwriteError
            If a variable ``key`` already exists in the simulation results file
        """
        if key in self.variables:
            raise SimResultsOverwriteError(
                f'Simulation results variable "{key}" already exists')

        self._data[key] = _SimResultsEntry(
            required    = required,
            units       = units,
            data        = None,
            description = description,
            group       = group
        )

        self.set_data(key, data, units)

    def clear(self) -> None:
        """Removes all data stored in this object"""
        self._compile_options = {}
        self._data = Dictionary(
            custom_except_class=SimResultsKeyError,
            custom_except_msg='Variable "%s" not found in simulation results file'
        )
        self._maha_multics_commit = None
        self._maha_multics_version = None
        self._num_time_steps = 0
        self._sim_version = None
        self._title = None
        self.trailing_newline = True

    def clear_data(self, regex_pattern: str = '.+') -> List[str]:
        """Removes simulation results data for any variable(s) with names
        matching a given regex pattern

        Parameters
        ----------
        regex_pattern : str, optional
            Any variables in :py:attr:`variables` matching this regex pattern
            will have existing simulation results data deleted (default is
            ``'.+'``, which matches all variable names)

        Returns
        -------
        list
            A list containing the variable names whose data were deleted
        """
        cleared_vars = []

        for var in self.variables:
            if re.match(regex_pattern, var):
                cleared_vars.append(var)
                self._data[var].data = None

        keys_without_data = [x.data is None for x in self._data.values()]
        if all(keys_without_data):
            self._num_time_steps = 0

        return cleared_vars

    def get_data(self, key: str, units: str) -> np.ndarray:
        """Extracts simulation results data by variable name

        Extracts data corresponding to a specific simulation results variable
        and returns it as a NumPy array with user-specified units, performing
        a unit conversion if necessary.

        Parameters
        ----------
        key : str
            The name of the variable whose data to extract
        units : str
            The units in which the simulation results data should be returned

        Returns
        -------
        np.ndarray
            A NumPy array containing the simulation results data for variable
            ``key``, in units of ``units``
        """
        # Extract data
        data_ref = self._data[key].data

        if data_ref is None:
            raise SimResultsDataNotFoundError(
                f'No simulation results data are present for key "{key}"')

        data = data_ref.copy()
        stored_units = self._data[key].units

        # Perform unit conversion if necessary
        if units == stored_units:
            return data

        return self.unit_converter.convert(
            quantity=data, from_unit=stored_units, to_unit=units)

    def get_description(self, key: str) -> Union[str, None]:
        """Returns the description (if assigned) of a variable in the
        simulation results file

        Parameters
        ----------
        key : str
            The name of the variable whose description to retrieve

        Returns
        -------
        str or None
            A string containing the description of the simulation results
            variable, or ``None`` if no description is available
        """
        return self._data[key].description

    def get_group(self, key: str) -> Union[str, None]:
        """Returns the name of the group (if assigned) of a variable in the
        simulation results file

        Parameters
        ----------
        key : str
            The name of the variable whose group to retrieve

        Returns
        -------
        str or None
            A string containing the name of the group of the simulation
            results variable, or ``None`` if no group has been assigned
        """
        return self._data[key].group

    def get_required(self, key: str) -> bool:
        """Returns whether a variable in the simulation results file is
        specified as "required"

        Variables specified as "required" indicates to the Maha Multics
        software that the simulation should exit with error if unable to
        output these values.

        Parameters
        ----------
        key : str
            The name of the variable whose data to extract

        Returns
        -------
        bool
            Whether the variable specified by ``key`` is marked as "required"
            in the simulation results file
        """
        return self._data[key].required

    def get_units(self, key: str) -> str:
        """Returns the "raw" units in which data in the simulation results
        file are stored

        When extracting data with :py:meth:`get_data`, the units can be
        converted to any valid unit; however, the data in :py:class:`SimResults`
        objects is internally stored with a particular set of units.  This
        method returns these units of the internally stored data.

        Parameters
        ----------
        key : str
            The name of the variable whose units to return

        Returns
        -------
        str
            The internally stored units of data in the simulation results file
        """
        return self._data[key].units

    def list_groups(self) -> Tuple[str, ...]:
        """Returns a tuple containing all variable groups in the simulation
        results file

        Returns
        -------
        tuple
            A tuple of strings, where each string is a variable group in the
            simulation results file
        """
        groups = []
        for entry in self._data.values():
            if (entry.group is not None) and (entry.group not in groups):
                groups.append(entry.group)

        return tuple(groups)

    def parse(self) -> None:
        """Parses the file content in the :py:attr:`contents` list and
        populates attributes (such as :py:attr:`title`) with extracted data

        This method parses the data in :py:attr:`contents`, extracting
        configuration and simulation results data and storing it in this
        object's attributes for easier reading and editing.
        """
        # Verify that file contents have been read
        super().parse()

        original_contents = copy.deepcopy(self.contents)

        # Extract title
        self.title = self.__parse_metadata_comment('Title')
        self.maha_multics_version \
            = self.__parse_metadata_comment(self.__maha_multics_version_identifier)
        self.maha_multics_commit \
            = self.__parse_metadata_comment(self.__maha_multics_commit_identifier)
        self.sim_version \
            = self.__parse_metadata_comment(self.__sim_version_identifier)

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
            remove_comments    = False,
            strip              = True,
            concat_lines       = False,
            remove_blank_lines = True
        )

        self._remove_vars_with_asterisk()

        # Extract list of variables in "printDict"
        sim_results_vars, comments, _, num_sec = self.extract_section_by_keyword(
            section_label      = 'printDict',
            begin_regex        = self.__printdict_begin_regex,
            end_regex          = self.__printdict_end_regex,
            section_line_regex = r'^\s*([@?])\s*([\w\d\._]+)\s+\[([^\s]+)\]\s*$',
            max_sections       = 1,
        )

        if num_sec == 0:
            raise InvalidSimResultsFormatError(
                'Unable to find "printDict" section in simulation results file')

        group_name = None
        for i, var in enumerate(sim_results_vars):
            if len(comments[i]) > 0:
                group_name = '\n'.join(
                    [self._extract_full_line_comment_text(x)
                     for x in comments[i]]
                )

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

            self._data[key] = _SimResultsEntry(required, units, group=group_name)

        # Extract simulation data
        self.clean_contents(
            remove_comments         = True,
            skip_full_line_comments = False,
            strip                   = True,
            concat_lines            = False,
            remove_blank_lines      = True
        )

        self._num_time_steps = 0

        i = 0
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
                    description = var_data[2] if len(var_data[2]) > 0 else None

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
                    # Replace "nan(ind)" with "nan" since MSVC compiler outputs
                    # NaN as "nan(ind)" but this can't be converted by NumPy
                    data_array = np.transpose(np.array(
                        [x.replace('nan(ind)', 'nan').split()
                         for x in self.contents[i+1:]],
                        dtype=np.float64,
                    ))

                    if data_array.ndim != 2:
                        # Due to the list comprehension above, this condition
                        # should never occur; however, it is checked anyway to
                        # be safe
                        raise AssertionError(  # pragma: no cover
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

        self.contents.clear()
        self.contents.extend(original_contents)

    def remove(self, key: str) -> None:
        """Removes a simulation results variable

        Removes a variable and any associated data from the simulation results
        file.

        Parameters
        ----------
        key : str
            The name of the variable to remove
        """
        if key not in self.variables:
            raise SimResultsKeyError(
                f'Simulation results variable "{key}" does not exist')

        del self._data[key]

    def search(self, keyword: str,
               search_fields: Union[
                   str, Tuple[str, ...], List[str]
               ] = ('keys', 'description', 'group', 'units'),
               case_sensitive: bool = False,
               show_data: bool = False,
               print_results: bool = True,
               return_results: bool = False,
               ) -> Union[Tuple[str, ...], None]:
        """Searches the simulation results file for a given search term

        This method can be useful for finding data, particularly in a large
        simulation results file.  It performs a relatively basic search,
        checking to see if a given term ``keyword`` is in any of the specified
        search fields.  The exact ``keyword`` must be found to register a
        match; similar terms are not considered a match.  To match any string,
        set ``keyword`` to ``''``.

        Parameters
        ----------
        keyword : str
            The term to search for
        search_fields : str or tuple or list, optional
            One or more simulation results variable attributes in which to
            search for ``keyword`` (default is to search all possible
            attributes, ``('keys', 'description', 'group', 'units')``)
        case_sensitive : bool, optional
            Whether to perform a case-sensitive search (default is ``False``)
        show_data : bool, optional
            Whether to print simulation results data, if available, for each
            variable (default is ``False``).  Setting this to ``True`` can
            considerably increase output verbosity
        print_results : bool, optional
            Whether to display results to the terminal (default is ``True``)
        return_results : bool, optional
            Whether to return a tuple of strings containing the simulation
            results variable keys for all search matches (default is ``False``)

        Returns
        -------
        tuple
            A tuple of strings containing all simulation results variable keys
            (i.e., selected from :py:attr:`variables`) for which search
            matches were registered.  Only returned if ``return_results`` is
            ``True``
        """
        keyword = str(keyword)
        if not case_sensitive:
            keyword = keyword.lower()

        search_fields = pyxx.arrays.convert_to_tuple(search_fields)
        invalid_fields = (set(search_fields)
                          - set(('keys', 'description', 'group', 'units')))
        if len(invalid_fields) > 0:
            raise ValueError(f'Invalid search fields: {invalid_fields}')

        _SimResultsEntry.show_data = show_data

        matches = []
        for var in self.variables:
            if 'keys' in search_fields:
                key = var
                if not case_sensitive:
                    key = key.lower()

                if keyword in key:
                    matches.append(var)
                    continue

            if 'description' in search_fields:
                if (description := self._data[var].description) is not None:
                    if not case_sensitive:
                        description = description.lower()

                    if keyword in description:
                        matches.append(var)
                        continue

            if 'group' in search_fields:
                if (group := self._data[var].group) is not None:
                    if not case_sensitive:
                        group = group.lower()

                    if keyword in group:
                        matches.append(var)
                        continue

            if 'units' in search_fields:
                units = self._data[var].units
                if not case_sensitive:
                    units = units.lower()

                if keyword in units:
                    matches.append(var)
                    continue

        if print_results:
            print(self.__get_printable_vars_str(matches))

        if return_results:
            return tuple(matches)

        return None

    def set_data(self, key: str,
                 data: Union[np.ndarray, List[float], Tuple[float, ...], None],
                 units: Optional[str] = None) -> None:
        """Adds or replaces simulation results data by variable name

        Parameters
        ----------
        key : str
            The name of the variable whose data to store
        data : np.ndarray or list or tuple
            A 1D array containing the data (in units of ``units``) to store
        units : str
            The units in which the simulation results data should be stored
        """
        if data is not None:
            # Store units
            if units is None:
                raise TypeError('If argument "data" is not `None`, argument '
                                '"units" must be provided')

            self._data[key].units = units

            # Validate data shape
            if self.num_time_steps == 0:
                self._num_time_steps = len(data)

            elif (self.num_time_steps > 0) and (len(data) != self.num_time_steps):
                raise ValueError(
                    f'Simulation results file has data for {self.num_time_steps} '
                    f'time steps. Cannot add new data series with {len(data)} '
                    'time steps')

        self._data[key].data = data

    def set_description(self, key: str, description: Union[str, None]) -> None:
        """Adds or modifies the description of a variable in the simulation
        results file

        Parameters
        ----------
        key : str
            The name of the variable whose description to retrieve
        description : str or None
            The description of the simulation results variable, or ``None`` to
            remove the description
        """
        self._data[key].description = description

    def set_group(self, key: str, group: Union[str, None]) -> None:
        """Sets or modifies the name of the group of a variable in the
        simulation results file

        Parameters
        ----------
        key : str
            The name of the variable whose group to retrieve
        description : str or None
            The group name of the simulation results variable, or ``None`` to
            remove the group name
        """
        self._data[key].group = group

    def set_required(self, key: str, required: bool) -> None:
        """Modifies whether a variable in the simulation results file is
        specified as "required"

        Variables specified as "required" indicates to the Maha Multics
        software that the simulation should exit with error if unable to
        output these values.

        Parameters
        ----------
        key : str
            The name of the variable whose data to extract
        required : bool
            Whether the variable specified by ``key`` is marked as "required"
            in the simulation results file
        """
        self._data[key].required = required

    def set_units(self, key: str, units: str,
                  action_if_data_present: str = 'error') -> None:
        """Modifies the units of a variable in the simulation results file

        Parameters
        ----------
        key : str
            The name of the variable whose units to modify
        units : str
            The units to assign to variable ``key``
        action_if_data_present : str, optional
            The action that should be taken if simulation results data for
            ``key`` are already present in the simulation results file
            (default is ``'error'``).  See "Notes" section for additional
            information

        Notes
        -----
        In the case that simulation results data for ``key`` already exist, it
        is not obvious how this case should be handled: should the data also
        be converted to the new units, or should only the units be changed?

        MahaUtils provides three options to handle this case:

        1. ``'error'``: If simulation results data are present, throw an error
        2. ``'convert_data'``: If simulation results data are present, convert
           it to the units given by the ``units`` argument (e.g., :math:`3\ m`
           would become :math:`0.003\ mm`)
        3. ``'keep_data_values'``: If simulation results data are present,
           keep the same values of the data but change the units (e.g.,
           :math:`3\ m` would become :math:`3\ mm`)
        """
        # Validate inputs
        valid_actions = ['error', 'convert_data', 'keep_data_values']
        if action_if_data_present not in valid_actions:
            raise ValueError('Action if data present must be selected '
                             f'from {valid_actions}')

        # Take no action if units match existing units
        if self._data[key].units == units:
            return

        # Store units
        if self._data[key].data is not None:
            if action_if_data_present == 'error':
                raise SimResultsOverwriteError(
                    f'Unable to set units for "{key}" because simulation '
                    'results data are already present')

            if action_if_data_present == 'convert_data':
                self._data[key].data = self.unit_converter.convert(
                    self._data[key].data,
                    from_unit=self._data[key].units, to_unit=units
                )

            if action_if_data_present == 'keep_data_values':
                pass

        self._data[key].units = units

    def update_contents(self, add_sim_data: bool = True, indent: int = 4,
                        padding: int = 4) -> None:
        """Updates the :py:attr:`contents` list based on object attributes

        This method synchronizes the :py:attr:`contents` list with the data
        stored in the :py:class:`SimResults` attributes (:py:attr:`title`,
        variables added by :py:meth:`append`, etc.).  This step should
        generally be performed prior to calling :py:meth:`write`, as writing
        a file directly saves the data in :py:attr:`contents` to disk.

        Parameters
        ----------
        add_sim_data : bool, optional
            Whether to add simulation results data to the end of
            :py:attr:`contents` (default is ``True``)
        indent : int, optional
            The number of spaces to use for indentation in the file (default
            is ``4``)
        padding : int, optional
            The number of spaces to place between simulation results variable
            names and the units in the ``printDict`` section of the simulation
            results file (default is ``4``)
        """
        if self.comment_chars is None:
            # This condition should not be reached since comment characters
            # are hard-coded for simulation results files, but the check is
            # still present to be safe
            raise SimResultsError(  # pragma: no cover
                'Cannot update contents until the "comment_chars" attribute '
                'is defined')
        comment_char = self.comment_chars[0]

        self.contents.clear()

        # Write title
        if self.title is not None:
            self.contents.append(f'{comment_char} Title: {self.title}')
            self.contents.append('')

        # Write "printDict" section
        self.contents.append('printDict{')

        if len(self.variables) > 0:
            max_key_len = pyxx.arrays.max_list_item_len(self.variables)
            for group in ([None] + list(self.list_groups())):
                group_lines = []
                group_vars_added = False

                if group is not None:
                    group_lines.append(f'{" "*indent}{comment_char} {group}')

                for var in self.variables:
                    if self._data[var].group == group:
                        group_vars_added = True
                        group_lines.append(
                            f'{" "*indent}'
                            f'{"@" if self._data[var].required else "?"}'
                            f'{var:{max_key_len}s}'
                            f'{" "*padding}[{self._data[var].units}]'
                        )

                # This should always be true, since the list of groups is
                # identified by the contents of "_data" (which guarantees
                # that each group should have at least one variable)
                if group_vars_added:  # pragma: no cover
                    self.contents.extend(group_lines + [''])
        else:
            self.contents.append('')

        self.contents[-1] = '}'

        # Write additional metadata
        if self.maha_multics_version is not None:
            self.contents.append(f'# {self.__maha_multics_version_identifier}: '
                                 f'{self.maha_multics_version}')

        if self.maha_multics_commit is not None:
            self.contents.append(f'# {self.__maha_multics_commit_identifier}: '
                                 f'{self.maha_multics_commit}')

        if self.sim_version is not None:
            self.contents.append(f'# {self.__sim_version_identifier}: '
                                 f'{self.sim_version}')

        # Write simulation data, if available
        if add_sim_data:
            # Simulation results variables and descriptions
            data_vars = ''
            data_array = []
            for var in self.variables:
                data = self._data[var].data

                if data is not None:
                    if (description := self._data[var].description) is None:
                        description = ''

                    data_vars += (f'${var}:{self._data[var].units}:{description}')

                    data_array.append(data)

            # Simulation results data
            if len(data_vars) > 0:
                self.contents.append(data_vars)

                # Compilation options
                if len(self.compile_options) > 0:
                    compile_opts_str = ', '.join(
                        [f'{k} = {v}' for k, v in self.compile_options.items()])
                    self.contents.append(f'#_OPTIONs: {compile_opts_str}'.strip())

                # Simulation results data
                for line in np.transpose(np.array(data_array, dtype=np.float64)):
                    self.contents.append(' '.join([str(x) for x in line]))
