"""This module provides a class intended for reading, parsing, and writing
files which store polygon geometry used by the Maha Multics software.
"""

import copy
import pathlib
import re
from typing import List, Optional, Union

import numpy as np
import pyxx

from mahautils.shapes.geometry.polygon import Polygon
from mahautils.shapes.layer import Layer
from mahautils.utils.dictionary import Dictionary
from .configfile import MahaMulticsConfigFile
from .exceptions import PolygonFileFormatError, PolygonFileMissingDataError


class PolygonFile(MahaMulticsConfigFile):
    """An object representing a Maha Multics polygon file

    The Maha Multics software uses polygon files to store geometry used for
    setting boundary conditions when running fluid simulations.  This class
    is capable of parsing such files and providing an interface through which
    users can interact with and manipulate data in the file.

    .. note::

        The data structure in :py:class:`PolygonFile` objects largely mirrors
        the content of Maha Multics polygon files, although there are a few
        differences (for which descriptive error messages are displayed).  For
        more information about the format of these files, refer to the
        :ref:`fileref-polygon_file` page.
    """

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None,
                 unit_converter: Optional[pyxx.units.UnitConverter] = None
                 ) -> None:
        super().__init__(path=path, unit_converter=unit_converter)

        # Initialize variables
        self._polygon_data: Dictionary[float, Layer] = Dictionary(
            required_key_type=(float, int),
            required_value_type=Layer,
        )
        self.trailing_newline = True

        self._polygon_merge_method: Union[int, None] = None
        self._time_extrap_method: Union[int, None] = None
        self._time_units: Union[str, None] = None

        # If path was provided, read file
        if path is not None:
            self.read(path, parse=True)

    @property
    def num_time_steps(self) -> int:
        """The number of time steps in the polygon file"""
        return len(self._polygon_data)

    @property
    def polygon_data(self) -> Dictionary[float, Layer]:
        """A reference to the dictionary containing the polygon data in the
        file

        This is a :py:class:`mahautils.utils.Dictionary` instance containing
        the polygon data in the file.  The keys in the dictionary are the time
        values (with units given by :py:attr:`time_units`) and the values
        should be :py:class:`mahautils.shapes.Layer` instances containing
        :py:class:`mahautils.shapes.Polygon` objects corresponding to each
        time step.

        Warnings
        --------
        This dictionary is returned **by reference**, so modifying it will
        alter the data in the :py:class:`PolygonFile` object.

        Notes
        -----
        This attribute can only be accessed if :py:attr:`polygon_merge_method`,
        :py:attr:`time_extrap_method`, and :py:attr:`time_units` are all set
        to values other than ``None``.
        """
        if (
            self.polygon_merge_method is None
            or (
                self.num_time_steps > 1
                and None in [self.time_extrap_method, self.time_units]
            )
        ):
            raise PolygonFileMissingDataError(
                'In order to edit or view the "polygon_data" dictionary, the '
                'following attributes must be set: (\'polygon_merge_method\', '
                '\'time_extrap_method\', \'time_units\')')

        return self._polygon_data

    @property
    def polygon_merge_method(self) -> int:
        """The method used to combine disjoint polygons

        This attribute represents the method for combining multiple disjoint
        polygons and is applied for all time steps (a limitation hard-coded
        in the Maha Multics software).

        For more information and a list of permissible values for the,
        :py:attr:`polygon_merge_method` property refer to the
        :ref:`Polygon File Format <fileref-polygon_file-polygon_merge>` page.
        """
        if self._polygon_merge_method is None:
            raise PolygonFileMissingDataError(
                'Attribute "polygon_merge_method" has not been defined')

        return self._polygon_merge_method

    @polygon_merge_method.setter
    def polygon_merge_method(self, polygon_merge_method: int) -> None:
        valid_choices = (0, 1, 2)
        if polygon_merge_method not in valid_choices:
            raise ValueError(
                'Polygon merge method (for combining multiple disjoint '
                f'polygons) must be one of the following: {valid_choices}'
            )

        self._polygon_merge_method = int(polygon_merge_method)

    @property
    def time_extrap_method(self) -> int:
        """The method used to handle time values outside the defined time range

        This property defines how the Maha Multics software will handle time
        values outside the range given by :py:attr:`time_values`.

        For more information and a list of permissible values for the,
        :py:attr:`time_extrap_method` property refer to the
        :ref:`Polygon File Format <fileref-polygon_file-time_extrap>` page.
        """
        if self._time_extrap_method is None:
            raise PolygonFileMissingDataError(
                'Attribute "time_extrap_method" has not been defined')

        return self._time_extrap_method

    @time_extrap_method.setter
    def time_extrap_method(self, time_extrap_method: int) -> None:
        valid_choices = (0, 2, 3)
        if time_extrap_method not in valid_choices:
            raise ValueError(
                'Time step extrapolation method must be one of the '
                f'following: {valid_choices}'
            )

        self._time_extrap_method = int(time_extrap_method)

    @property
    def time_units(self) -> str:
        """The units in which "time" values are stored in the polygon file

        Note that the term "time" is used loosely for polygon files, and "time"
        may also be given in terms of quantities such as shaft rotation angle.
        For more information, refer to the :ref:`fileref-polygon_file` page.
        """
        if self._time_units is None:
            raise PolygonFileMissingDataError(
                'Attribute "time_units" has not been defined')

        return self._time_units

    @time_units.setter
    def time_units(self, time_units: str) -> None:
        time_units = str(time_units)

        if not self.unit_converter.is_defined_unit(time_units):
            raise ValueError(f'Time units "{time_units}" are not defined in '
                             'this object\'s unit converter')

        self._time_units = time_units

    @property
    def time_values(self) -> List[float]:
        """The values of "time" defined in the polygon file

        This method returns a **copy** of the list of time values, so modifying
        the returned list will **not** affect the time values stored in the
        polygon file.  The time values are returned with units given by
        :py:attr:`time_units`.
        """
        return list(self._polygon_data.keys())

    def __parse_int(self, value: Union[str, float], error_message: str) -> int:
        if pyxx.numbers.is_integer(value):
            return int(float(value))

        raise PolygonFileFormatError(error_message)

    def parse(self) -> None:
        super().parse()
        original_contents = copy.deepcopy(self.contents)

        # Remove comments and whitespace
        self.clean_contents(
            remove_comments    = True,
            strip              = True,
            concat_lines       = False,
            remove_blank_lines = False,
        )

        # Extract header
        line_idx = 0
        metadata = [x.strip() for x in self.contents[line_idx].split(maxsplit=2)]

        try:
            num_time_steps = self.__parse_int(
                value=metadata[0],
                error_message=(f'Error parsing polygon file (line {line_idx+1}): '
                               'number of time steps must be an integer'))
            polygons_per_time_step = self.__parse_int(
                value=metadata[1],
                error_message=(f'Error parsing polygon file (line {line_idx+1}): '
                               'polygons per time step must be an integer'))
            self.polygon_merge_method = self.__parse_int(
                value=metadata[2],
                error_message=(f'Error parsing polygon file (line {line_idx+1}): '
                               'disjoint polygon merge method must be an integer'))
        except IndexError as exception:
            raise PolygonFileFormatError(
                f'Error parsing polygon file (line {line_idx+1}): missing '
                'header data. The number of time steps, polygons per time '
                'step, and disjoint polygon merge method must be provided as '
                'whitespace-separated numbers'
            ) from exception
        except ValueError as exception:
            exception.args = ('Error parsing polygon file (line '
                              f'{line_idx+1}): {exception.args[0]}',)
            raise

        if num_time_steps > 1:
            line_idx += 1
            line = self.contents[line_idx]

            regex = r'^\s*(.+):\s*([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)\s*$'
            groups = re.search(regex, line)

            if groups is None:
                raise PolygonFileFormatError(
                    f'Error parsing polygon file (line {line_idx+1}): time '
                    'values are not formatted correctly')

            try:
                self.time_units = str(groups.group(1))
            except ValueError as exception:
                exception.args = ('Error parsing polygon file (line '
                                  f'{line_idx+1}): {exception.args[0]}',)
                raise

            try:
                initial_time = float(groups.group(2))
                time_step = float(groups.group(3))
            except (TypeError, ValueError) as exception:
                raise PolygonFileFormatError(
                    f'Error parsing polygon file (line {line_idx+1}): initial '
                    'time and number of time steps must be numbers'
                ) from exception

            try:
                self.time_extrap_method = self.__parse_int(
                    value=groups.group(4),
                    error_message=('Error parsing polygon file (line '
                                   f'{line_idx+1}): time step extrapolation '
                                   'method must be an integer')
                )
            except ValueError as exception:
                exception.args = ('Error parsing polygon file (line '
                                  f'{line_idx+1}): {exception.args[0]}',)
                raise

            time_vals = list(np.linspace(
                initial_time, time_step*(num_time_steps - 1) + initial_time,
                num_time_steps))

        else:
            time_vals = [0]

        # Extract polygon coordinates
        for i in range(num_time_steps):
            layer = Layer(print_multiline=False)

            for _ in range(polygons_per_time_step):
                # Extract polygon metadata
                line_idx += 1

                try:
                    num_coordinates, enclosed_convention = (
                        [self.__parse_int(x,
                                          'Error parsing polygon file (line '
                                          f'{line_idx+1}): number of coordinates '
                                          'and polygon file enclosed convention '
                                          'must be integers')
                         for x in self.contents[line_idx].split(maxsplit=1)]
                    )
                except ValueError as exception:
                    raise PolygonFileFormatError(
                        f'Error parsing polygon file (line {line_idx+1}): '
                        'both number of coordinates and polygon file enclosed '
                        'convention must be provided'
                    ) from exception

                # Extract polygon x-coordinates
                line_idx += 1

                x_units, x_coordinates_str \
                    = self.contents[line_idx].split(':', maxsplit=1)
                x_units = x_units.strip()

                try:
                    x_coordinates = np.array(x_coordinates_str.split(),
                                             dtype=np.float64)
                except (TypeError, ValueError) as exception:
                    raise PolygonFileFormatError(
                        f'Error parsing polygon file (line {line_idx+1}): '
                        'x-coordinates are not a whitespace-separated list '
                        'of numbers'
                    ) from exception

                # Extract polygon y-coordinates
                line_idx += 1

                y_units, y_coordinates_str \
                    = self.contents[line_idx].split(':', maxsplit=1)
                y_units = y_units.strip()

                try:
                    y_coordinates = np.array(y_coordinates_str.split(),
                                             dtype=np.float64)
                except (TypeError, ValueError) as exception:
                    raise PolygonFileFormatError(
                        f'Error parsing polygon file (line {line_idx+1}): '
                        'y-coordinates are not a whitespace-separated list '
                        'of numbers'
                    ) from exception

                # Validate polygon data formatting
                if not (len(x_coordinates) == len(y_coordinates)
                        == num_coordinates):
                    raise PolygonFileFormatError(
                        f'Error parsing polygon file (lines {line_idx}-'
                        f'{line_idx+1}): expected {num_coordinates} point '
                        f'coordinates, but found {len(x_coordinates)} x-'
                        f'coordinates and {len(y_coordinates)} y-coordinates')

                for k, units in enumerate((x_units, y_units)):
                    if not self.unit_converter.is_defined_unit(units):
                        raise PolygonFileFormatError(
                            f'Error parsing polygon file (line {line_idx+k}): '
                            f'unrecognized units "{units}"')

                if x_units != y_units:
                    raise PolygonFileFormatError(
                        f'Error parsing polygon file (lines {line_idx}-'
                        f'{line_idx+1}): units for x-coordinates and y-'
                        'coordinates must be equal')

                # Create polygon from coordinates
                coordinates = (x_coordinates, y_coordinates)

                layer.append(
                    Polygon(vertices=np.transpose(np.stack(coordinates)),
                            polygon_file_enclosed_conv=enclosed_convention,
                            units=x_units)
                )

            self._polygon_data[time_vals[i]] = layer

        self.contents.clear()
        self.contents.extend(original_contents)
