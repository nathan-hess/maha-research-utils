"""This module provides a class intended for reading, parsing, and writing
files which store polygon geometry used by the Maha Multics software.
"""

import copy
import math
import pathlib
import re
from typing import List, Optional, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import numpy as np
import plotly.express as px        # type: ignore
import plotly.graph_objects as go  # type: ignore
import pyxx

from mahautils.shapes.geometry.polygon import Polygon
from mahautils.shapes.geometry.shape_open_closed import ClosedShape2D
from mahautils.shapes.plotting import _create_blank_plotly_figure, _figure_config
from mahautils.shapes.layer import Layer
from mahautils.utils.dictionary import Dictionary
from .configfile import MahaMulticsConfigFile
from .exceptions import PolygonFileFormatError, PolygonFileMissingDataError


class PolygonFile(MahaMulticsConfigFile):
    """An object representing a Maha Multics polygon file

    The Maha Multics software uses polygon files to store geometry used for
    setting boundary conditions when running fluid simulations.  This class
    is capable of parsing such files and providing an interface through which
    users can interact with and manipulate data in the file (through the
    :py:attr:`polygon_data` attribute).

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

        This method returns a :py:class:`mahautils.utils.Dictionary` instance
        containing the polygon data in the file.  The keys are the time values
        defined in the file (with units given by :py:attr:`time_units`) and
        the values are :py:class:`Layer` instances containing the polygons
        corresponding to each time step.  This dictionary can be directly
        edited to modify the polygon file (adding new time steps, removing
        time steps, changing polygon properties, etc.).

        .. important::

            The dictionary is returned **by reference**, so editing the
            returned dictionary will directly edit data in the
            :py:class:`PolygonFile` instance.

        Notes
        -----
        This property can only be accessed if :py:attr:`polygon_merge_method`,
        :py:attr:`time_extrap_method`, and :py:attr:`time_units` are all
        defined (even for polygon files with a single time step, since
        additional time steps may be added by modifying the polygon data
        dictionary).  This ensures consistency of the data stored in the
        :py:class:`PolygonFile` object.  To access the polygon data before
        setting these properties, use :py:attr:`polygon_data_readonly`.

        Any of the methods for adding or removing data provided by
        :py:class:`mahautils.utils.Dictionary` can be used to modify polygon
        data.  For instance, to insert a new time step prior to an existing
        time, simply use :py:meth:`mahautils.utils.Dictionary.insert_before`.
        *This is why there is no "add polygon" method -- accessing the
        dictionary methods provides greater flexibility.*
        """
        # Verify that polygon file metadata is defined; otherwise it is
        # ambiguous what units and meaning user-specified polygons and time
        # steps have (i.e., if you add a new time step to the polygon data
        # dictionary at t=2, what units are t=2?)
        if None in [
            self._polygon_merge_method,
            self._time_extrap_method,
            self._time_units,
        ]:
            raise PolygonFileMissingDataError(
                'In order to edit or view the "polygon_data" dictionary, the '
                'following attributes must be set: (\'polygon_merge_method\', '
                '\'time_extrap_method\', \'time_units\')')

        return self._polygon_data

    @property
    def polygon_data_readonly(self) -> Dictionary[float, Layer]:
        """A copy of the dictionary containing the polygon data in the file

        This method returns a :py:class:`mahautils.utils.Dictionary` instance
        containing the polygon data in the file.  The keys are the time values
        defined in the file (with units given by :py:attr:`time_units`) and
        the values are :py:class:`Layer` instances containing the polygons
        corresponding to each time step.

        .. important::

            The dictionary is returned **by copy**, so editing the
            returned dictionary will **not** directly edit data in the
            :py:class:`PolygonFile` instance.

        Notes
        -----
        Unlike :py:attr:`polygon_data`, this method does **not** require the
        :py:attr:`polygon_merge_method`, :py:attr:`time_extrap_method`, and
        :py:attr:`time_units` properties to be defined defined.
        """
        return copy.deepcopy(self._polygon_data)

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

    def filter_times(self, interval: float, tolerance: float = 1e-12) -> None:
        """Reduces the number of time steps in a polygon file

        Prunes time steps from a polygon file at user-specified intervals.
        This can be useful, for instance, if you have a polygon file with a
        time step of 0.01 seconds and you want to increase the time step to
        0.1 seconds.

        Parameters
        ----------
        interval : float
            The spacing at which to keep time steps, in units of
            :py:attr:`time_units`
        tolerance : float, optional
            The allowable difference between retained time steps and intervals
            of size ``interval`` (default is ``1e-12``)

        Notes
        -----
        Time steps are kept if they fall within a distance of ``tolerance``
        of ``{..., -2*interval, -interval, 0, interval, 2*interval, ...}``
        """
        for t in self.time_values:
            if abs(interval*round(t / interval) - t) > tolerance:
                del self._polygon_data[t]

    def parse(self) -> None:
        """Parses the file content in the :py:attr:`contents` list and
        populates attributes (such as the dictionary returned by
        :py:attr:`polygon_data`) with extracted data

        This method parses the data in :py:attr:`contents`, checking for
        polygon file format errors and extracting data on individual polygons
        for easier reading and modification.
        """
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
                    'time and time step must be numbers'
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
            layer = Layer(print_multiline=False,
                          color=px.colors.qualitative.Plotly[0])

            for _ in range(polygons_per_time_step):
                if len(self.contents) < (line_idx + 2):
                    raise PolygonFileFormatError(
                        'Polygon file appears to be missing data for '
                        'some polygons')

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

        if line_idx != (len(self.contents) - 1):
            raise PolygonFileFormatError(
                'Polygon file contains more polygons than expected')

        self.contents.clear()
        self.contents.extend(original_contents)

    def plot(self, delay: float = 100, show: bool = True,
             return_fig: bool = False) -> Union[go.Figure, None]:
        """Generates an animated plot showing the geometry in the polygon file

        Polygons in the file are illustrated as filled, solid shapes, and
        construction geometry is illustrated as dotted outlines.

        Parameters
        ----------
        delay : float, optional
            The delay (in milliseconds) between each frame when animating the
            plot (default is ``100``)
        show : bool, optional
            Whether to open the figure in a browser (default is ``True``)
        return_fig : bool, optional
            Whether to return the figure (default is ``False``)

        Returns
        -------
        go.Figure
            An animated Plotly figure depicting the polygon file.  Returned if
            and only if ``return_fig`` is ``True``
        """
        # Verify that all polygons have the same units and determine range of
        # coordinates
        units = None
        xmin = math.inf
        xmax = -math.inf
        ymin = math.inf
        ymax = -math.inf

        for t, layer in self._polygon_data.items():
            for polygon in layer:
                if polygon.units is None:
                    raise PolygonFileMissingDataError(
                        'Units were not provided for polygon at time '
                        f'{t} {self.time_units}')

                if units is None:
                    units = polygon.units
                elif polygon.units != units:
                    raise PolygonFileFormatError(
                        'Polygons must have the same units to be plotted. '
                        f'Polygon at time {t} {self.time_units} has units '
                        f'{polygon.units} but previous polygons had units '
                        f'{units}')

                x, y = polygon.xy_coordinates()
                xmin = min(xmin, x.min())
                xmax = max(xmax, x.max())
                ymin = min(ymin, y.min())
                ymax = max(ymax, y.max())

        x_pad = 0.05*(xmax - xmin)
        y_pad = 0.05*(ymax - ymin)

        # Determine maximum number of traces per layer (since Plotly
        # animations require all frames to have the same number of traces)
        max_layer_traces = 0
        for layer in self._polygon_data.values():
            layer_traces = 0

            for polygon in layer:
                if polygon.construction:
                    layer_traces += 1
                else:
                    layer_traces += 2

            max_layer_traces = max(max_layer_traces, layer_traces)

        # Create frames
        first_layer_fig = _create_blank_plotly_figure()
        frames = []
        for i, (t, layer) in enumerate(self._polygon_data.items()):
            layer_fig: go.Figure = layer.plot(units=units, show=False,
                                              return_fig=True)

            for _ in range(max_layer_traces - len(layer_fig.data)):
                layer_fig.add_trace(go.Scatter(x=[], y=[]))

            frames.append(
                go.Frame(data=layer_fig.data, layout=layer_fig.layout, name=t))

            if i == 0:
                first_layer_fig = layer_fig

        # Create main figure
        figure = go.Figure(data=first_layer_fig.data,
                           layout=first_layer_fig.layout,
                           frames=frames)

        frame_args = {
            'frame': {'duration': delay},
            'mode': 'immediate',
            'fromcurrent': True,
            'transition': {'duration': 0},
        }

        sliders = [{
            'steps': [
                {
                    'args': [[frame.name], frame_args],
                    'label': f'{float(frame.name):.8g}',
                    'method': 'animate',
                } for frame in frames
            ],

            # Styling
            'x': 0.05,
            'y': 0,
            'len': 0.95,
            'pad': {'b': 10, 't': 60},
        }]

        figure.update_layout(
            xaxis={'range': [xmin-x_pad, xmax+x_pad], 'autorange': False},
            yaxis={'range': [ymin-y_pad, ymax+y_pad], 'autorange': False},
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, frame_args],
                        'label': '&#9654;',
                        'method': 'animate',
                    },
                    {
                        'args': [[None], frame_args],
                        'label': '<b>||</b>',
                        'method': 'animate',
                    },
                ],
                'direction': 'left',
                'type': 'buttons',

                # Styling
                'x': 0.03,
                'y': 0,
                'pad': {'r': 10, 't': 80},
            }],
            sliders=sliders,
        )

        if show:
            figure.show(config=_figure_config)  # pragma: no cover

        if return_fig:
            return figure

        return None

    def time_step(self, units: Optional[str] = None) -> float:
        """Returns the time step for the polygon file

        Verifies that the polygon file has a constant, positive time step between
        successive values in :py:attr:`time_values` and returns this time step.
        If the polygon file has only a single time step, ``0`` is returned.

        Parameters
        ----------
        units : str, optional
            The units in which the time step should be returned.  Required to
            be provided if the polygon file has more than one time step, but
            optional otherwise (default is ``None``)

        Returns
        -------
        float
            The time step between successive values in :py:attr:`time_values`,
            or ``0`` for polygon files with a single time step

        Raises
        ------
        PolygonFileFormatError
            If the polygon file has multiple time values but the time step
            between them is not consistent

        Notes
        -----
        The term "time" is used loosely for polygon files, and "time" may also
        be given in terms of quantities such as shaft rotation angle.  For
        more information, refer to the :ref:`fileref-polygon_file` page.
        """
        if self.num_time_steps <= 1:
            return 0

        if units is None:
            raise TypeError(
                f'Polygon file has {self.num_time_steps} time steps, so '
                'argument "units" must be provided')

        fp_tolerance = 1e-12

        time_vals = np.array(self.time_values, dtype=np.float64)
        time_steps = time_vals[1:] - time_vals[:-1]

        mean_time_step = float(np.mean(time_steps))
        max_diff = float(np.max(np.abs(time_steps - mean_time_step)))

        if max_diff > fp_tolerance:
            raise PolygonFileFormatError(
                'Inconsistent time step in polygon file. The mean time step is '
                f'{mean_time_step} {self.time_units} but individual time steps '
                f'differ by up to {max_diff} {self.time_units}'
            )

        time_step = float(self.unit_converter.convert(
            quantity=mean_time_step,
            from_unit=self.time_units, to_unit=units))

        if time_step <= 0:
            raise PolygonFileFormatError(
                'Polygon file time step cannot be negative or zero '
                f'(calculated time step is {time_step} {self.time_units})')

        return time_step

    def update_contents(self) -> None:
        """Updates the :py:attr:`contents` list based on object attributes

        This method synchronizes the :py:attr:`contents` list with the data
        stored in the :py:class:`PolygonFile` attributes.  This step should
        generally be performed prior to calling :py:meth:`write`, as writing
        a file directly saves the data in :py:attr:`contents` to disk.

        Construction polygons are not added to the :py:attr:`contents` list.
        """
        self.contents.clear()

        # Determine number of non-construction polygons per time step
        num_polygons = np.array(
            [sum(not shape.construction for shape in x)
             for x in self._polygon_data.values()])
        polygons_per_time_step = num_polygons[0]

        if not np.all(num_polygons == polygons_per_time_step):
            raise PolygonFileFormatError(
                'Different numbers of polygons are present at different time '
                'steps. To write a polygon file, all time steps must have the '
                'same number of polygons')

        # Write file
        self.contents.append(f'{self.num_time_steps} {polygons_per_time_step} '
                             f'{self.polygon_merge_method}')

        if self.num_time_steps > 1:
            time_step = self.time_step(self.time_units)

            self.contents.append(f'{self.time_units}: {self.time_values[0]} '
                                 f'{time_step} {self.time_extrap_method}')

        for t, layer in self._polygon_data.items():
            for polygon in layer:
                if polygon.construction:
                    continue

                if polygon.units is None:
                    raise PolygonFileMissingDataError(
                        'Units were not provided for polygon at time '
                        f'{t} {self.time_units}')

                if not isinstance(polygon, ClosedShape2D):
                    raise PolygonFileFormatError(
                        f'Polygon at time {t} {self.time_units} is not a '
                        f'subclass of `{ClosedShape2D.__name__}`')

                self.contents.append(f'{len(polygon.points())} '
                                     f'{polygon.polygon_file_enclosed_conv}')

                for coordinates in polygon.xy_coordinates(repeat_end=False):
                    coordinates_str = [str(x) for x in coordinates]
                    self.contents.append(
                        f'{polygon.units}: {" ".join(coordinates_str)}')
