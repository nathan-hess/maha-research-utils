"""This module provides a class intended for reading and parsing VTK files
used by the Maha Multics software.
"""

import pathlib
import re
import string
from typing import Any, List, Union, Optional

import numpy as np
import pandas as pd            # type: ignore
import pyxx
import vtk                     # type: ignore
import vtk.util.numpy_support  # type: ignore  # pylint: disable=E0401,E0611

from .exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
    VTKInvalidIdentifier,
    VTKFormatError,
)
from .units import MahaMulticsUnitConverter


class VTKFile(pyxx.files.BinaryFile):
    """An object for representing VTK files

    VTK files are commonly used with the Maha Multics software to store film
    property distributions and other simulation results.  This class provides
    the ability to read and parse such files, and perform tasks such as
    extracting particular data, converting the units of data stored in the VTK
    file, and plotting scalar property distributions.
    """

    # Regular expression describing expected format for identifiers that
    # follow the naming convention used at the Maha Fluid Power Research
    # Center
    __maha_name_convention_regex = r'^([^\s]+)\[([^\s]+)\]$'

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None,
                 unit_converter: Optional[pyxx.units.UnitConverter] = None,
                 **kwargs) -> None:
        """Creates an object that can parse data from a VTK file

        Creates an instance of the :py:class:`VTKFile` class and optionally
        reads and parses a specified VTK file.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename of the VTK file to read and parse (default
            is ``None``).  If set to ``None``, no VTK file is read
        unit_converter : pyxx.units.UnitConverter, optional
            A :py:class:`pyxx.units.UnitConverter` instance which will be
            used to convert units of quantities stored in the VTK file
            (default is ``None``).  If set to ``None``, the
            :py:class:`MahaMulticsUnitConverter` unit converter will be used
            to perform unit conversions
        **kwargs
            Any valid arguments (other than ``path``) for the :py:meth:`read`
            method can be passed to this constructor as keyword arguments
        """
        super().__init__(path)

        # Initialize variables
        self._coordinate_units: Union[str, None] = None

        if unit_converter is None:
            self.unit_converter = MahaMulticsUnitConverter()
        else:
            self.unit_converter = unit_converter

        # If file is specified, read the file
        if path is not None:
            self.read(path=path, **kwargs)

    @property
    def coordinate_units(self) -> Union[str, None]:
        """The units in which the :math:`x`-, :math:`y`-, and
        :math:`z`-coordinates of points in the VTK file are stored
        """
        return self._coordinate_units

    @property
    def num_points(self) -> int:
        """The number of points in the VTK grid for which vector, scalar,
        and/or tensor data are stored
        """
        try:
            return self._num_points
        except AttributeError as exception:
            raise FileNotParsedError(
                'Number of points in VTK grid is not defined; VTK file has '
                'not yet been read') from exception

    @property
    def pointdata_df(self) -> pd.DataFrame:
        """A Pandas DataFrame containing the coordinates of each point in the
        VTK file and any scalar or vector data for the point

        This DataFrame stores the raw data parsed from the VTK file.  The
        first three columns of the file store the :math:`x`-, :math:`y`-, and
        :math:`z`-coordinates of point in the VTK grid, and subsequent columns
        store the raw scalar or vector data for each point.  Data are stored
        in the same units defined in the VTK file.
        """
        try:
            return self._df.copy(deep=True)
        except AttributeError as exception:
            raise FileNotParsedError(
                'Point data DataFrame is not defined; VTK file has not yet '
                'been read') from exception

    @property
    def unit_converter(self) -> pyxx.units.UnitConverter:
        """The unit converter used to perform unit conversions for quantities
        stored in the VTK file

        This attribute must be an instance or subclass of a
        :py:class:`pyxx.units.UnitConverter` object.
        """
        return self._unit_converter

    @unit_converter.setter
    def unit_converter(self,
                       unit_converter: Optional[pyxx.units.UnitConverter]
                       ) -> None:
        if not isinstance(unit_converter, pyxx.units.UnitConverter):
            raise TypeError(
                'Argument "unit_converter" must be an instance or subclass '
                'of "pyxx.units.UnitConverter"')

        self._unit_converter = unit_converter

    @property
    def use_maha_name_convention(self) -> bool:
        """Whether the data identifiers in the VTK file follow the naming
        convention adopted by the Maha Fluid Power Research Center

        At the Maha Fluid Power Research Center, the convention for naming
        VTK data identifiers (for both scalar and vector data) is to first
        specify a descriptive name, followed by the unit in square brackets.
        There should be no whitespace in the entire identifier.

        For instance, one potential identifier that could denote VTK data
        storing pressure in units of Pascal might be: ``pressure[Pa]``.
        Similarly, an identifier for VTK data storing the velocity of a
        tractor might be ``tractorVelocity[m/s]``.
        """
        try:
            return self._use_maha_name_convention
        except AttributeError as exception:
            raise FileNotParsedError(
                'VTK identifier naming convenction is not defined; VTK file '
                'has not yet been read') from exception

    def _check_name_convention_compliance_id(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError(
                f'VTK data name {name} is not of type "str"')

        if self.use_maha_name_convention:
            if not re.match(self.__maha_name_convention_regex, name):
                raise VTKIdentifierNameError(
                    f'Invalid VTK data identifier: "{name}"')

    def _check_name_convention_compliance_unit(self, unit: Union[Any, None]
                                               ) -> None:
        if self.use_maha_name_convention:
            if unit is None:
                raise TypeError(
                    'VTK file uses the Maha naming convention, so '
                    'argument "unit" cannot be `None`')

        elif unit is not None:
            raise TypeError(
                'VTK file does not use Maha naming convention, so '
                'argument "unit" must be `None`')

    def _find_column_id(self, identifier: str) -> str:
        # Validate inputs
        if not isinstance(identifier, str):
            raise TypeError('Argument "identifier" must be of type "str"')

        # If not using the Maha name convention, simply check that the
        # identifier exists as one of the DataFrame columns
        if not self.use_maha_name_convention:
            if identifier not in self._df:
                raise VTKInvalidIdentifier(
                    f'Data specified by identifier "{identifier}" not found '
                    'in VTK file')

        # If using the Maha name convention, users can either specify the
        # identifier with or without the unit (e.g., 'pFilm[bar]' or 'pFilm'),
        # so determine which of these is a valid column name (and if neither,
        # throw an error)
        else:
            if identifier not in self._df:
                matches = []
                for column in self._df.columns:
                    if identifier == self._parse_column_id(column, 'name'):
                        matches.append(column)

                if len(matches) == 0:
                    raise VTKInvalidIdentifier(
                        f'Data specified by identifier "{identifier}" not found '
                        'in VTK file')

                if len(matches) > 1:
                    raise VTKInvalidIdentifier(
                        f'Identifier "{identifier}" matches multiple data '
                        f'fields in the VTK file: {matches}')

                identifier = matches[0]

        return identifier

    def _parse_column_id(self, identifier: str, target: str) -> str:
        if not self.use_maha_name_convention:
            raise AttributeError(
                'Parsing VTK data identifier is not a valid action when VTK '
                'file does not use the Maha naming convention')

        matches = re.search(self.__maha_name_convention_regex, str(identifier))

        if matches is None:
            raise VTKIdentifierNameError(
                f'Invalid VTK data identifier: "{identifier}"')

        if target == 'name':
            return matches.group(1)
        if target == 'unit':
            return matches.group(2)

        raise ValueError('Argument "target" must be one of: ["name", "unit"]')

    def coordinates(self, axis: str, unit: Optional[str] = None) -> np.ndarray:
        """Returns a NumPy array containing the coordinates of all grid points
        in the VTK file along a particular coordinate axis

        VTK files store data (scalars, vectors, etc.) at a set of defined grid
        points in 3D.  This method returns a 1D NumPy array containing the
        coordinates of the coordinates of such points along an axis specified
        by ``axis``.  Point coordinates are returned in the order in which
        they were defined in the VTK file.

        Parameters
        ----------
        axis : str
            The coordinate axis for which to retrieve coordinates.  Must be
            exactly one of: ``'x'``, ``'y'``, ``'z'``
        unit : str, optional
            The unit in which the VTK points should be returned (default is
            ``None``).  Must be provided if :py:attr:`use_maha_name_convention`
            is ``True`` and omitted if :py:attr:`use_maha_name_convention` is
            ``False``

        Returns
        -------
        np.ndarray
            A 1D NumPy array containing the coordinates of all VTK grid points
            along the axis specified by ``axis``

        Raises
        ------
        FileNotParsedError
            If attempting to call this method before calling :py:meth:`read`
            to read and parse a VTK file
        """
        try:
            if axis.lower() == 'x':
                column = self.__xyz_coordinate_columns[0]
            elif axis.lower() == 'y':
                column = self.__xyz_coordinate_columns[1]
            elif axis.lower() == 'z':
                column = self.__xyz_coordinate_columns[2]
            else:
                raise ValueError(
                    'Argument "axis" must be exactly one of: ["x", "y", "z"]')
        except AttributeError as exception:
            raise FileNotParsedError(
                'Cannot retrieve VTK x-coordinates; VTK file has not yet '
                'been read') from exception

        return self.extract_data_series(column, unit)

    def extract_data_series(self, identifier: str, unit: Optional[str] = None
                            ) -> np.ndarray:
        # SETUP --------------------------------------------------------------
        # Verify that file has been read
        if not hasattr(self, '_df'):
            raise FileNotParsedError(
                'Unable to retrieve VTK data; VTK file has not yet '
                'been read')

        # Check that identifier matches a single column in the DataFrame
        identifier = self._find_column_id(identifier)

        # Verify that unit was provided if and only if using Maha naming
        # convention
        self._check_name_convention_compliance_unit(unit)

        # CASE 1: Not using Maha naming convention ---------------------------
        if not self.use_maha_name_convention:
            return self._df[identifier].to_numpy()

        # CASE 2: Using Maha naming convention -------------------------------
        # Extract raw data from DataFrame
        from_unit = self._parse_column_id(identifier, 'unit')
        raw_data = self._df[identifier].to_numpy()

        # Convert raw data units
        return self.unit_converter.convert(
            raw_data, from_unit=from_unit, to_unit=str(unit))

    def extract_dataframe(self, identifiers: List[str],
                          units: Optional[List[str]] = None) -> pd.DataFrame:
        # SETUP --------------------------------------------------------------
        # Verify that unit was provided if and only if using Maha naming
        # convention
        self._check_name_convention_compliance_unit(units)

        # CASE 1: Not using Maha naming convention ---------------------------
        if not self.use_maha_name_convention:
            df_data = {
                identifier: self.extract_data_series(identifier)
                    for identifier in identifiers  # noqa: E131
            }

        # CASE 2: Using Maha naming convention -------------------------------
        else:
            # Ensure that units are a list of strings
            #   Add Mypy exclusion because if "units" is `None`, an error
            #   would have been thrown by name convention compliance check
            units = [str(unit) for unit in units]  # type: ignore

            # Validate inputs
            if len(identifiers) != len(units):
                raise ValueError(
                    'Arguments "identifiers" and "units" must be lists of '
                    'strings with the same number of items')

            # Extract and convert units of data from VTK file
            df_data = {}
            for i, identifier in enumerate(identifiers):
                name = self._parse_column_id(self._find_column_id(identifier),
                                             target='name')
                unit = units[i]

                df_data[f'{name}[{unit}]'] \
                    = self.extract_data_series(identifier, unit)

        return pd.DataFrame(df_data)

    def points(self, unit: Optional[str] = None) -> np.ndarray:
        """Returns a list of all grid points in the VTK file

        VTK files store data (scalars, vectors, etc.) at a set of defined grid
        points in 3D.  This method returns a list containing the coordinates
        of all such points.  Refer to the "Notes" section for details about
        the format of the returned points.

        Parameters
        ----------
        unit : str, optional
            The unit in which the VTK points should be returned (default is
            ``None``).  Must be provided if :py:attr:`use_maha_name_convention`
            is ``True`` and omitted if :py:attr:`use_maha_name_convention` is
            ``False``

        Returns
        -------
        np.ndarray
            A NumPy array containing a list of all VTK grid points.  Refer to
            the "Notes" section for details about the format of the array

        Raises
        ------
        FileNotParsedError
            If attempting to call this method before calling :py:meth:`read`
            to read and parse a VTK file

        Notes
        -----
        The VTK grid points are returned as a 2D array, where the first index
        specifies a particular point (out of the :py:attr:`num_points` points)
        and the second index specifies the coordinate axis (:math:`x`,
        :math:`y`, or :math:`z`).

        For example, suppose that the VTK file stored data for five points:
        ``(x1, y1, z1)``, ``(x2, y2, z2)``, ..., ``(x5, y5, z5)``.  In this
        case, the :py:meth:`points` method would return:

        .. code-block:: python

            array([[x1, y1, z1],
                   [x2, y2, z2],
                   [x3, y3, z3],
                   [x4, y4, z4],
                   [x5, y5, z5]])

        Point coordinates are returned in the order in which they were defined
        in the VTK file.
        """
        try:
            return np.array([self.extract_data_series(name, unit)
                             for name in self.__xyz_coordinate_columns]
                            ).transpose()
        except AttributeError as exception:
            raise FileNotParsedError(
                'Cannot retrieve VTK grid points; VTK file has not yet '
                'been read') from exception

    def read(self,
             path: Optional[Union[str, pathlib.Path]] = None,
             use_maha_name_convention: bool = False,
             coordinate_units: Optional[str] = None
             ) -> None:
        """Reads a VTK file from the disk

        This method reads a VTK file from the disk, parsing its content and
        storing the data as a Pandas DataFrame in the :py:attr:`pointdata`
        attribute.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename from which to read the VTK file (default is
            ``None``).  If not provided or ``None``, the file will be read
            from the location specified by the :py:attr:`path` attribute
        use_maha_name_convention : bool, optional
            Whether the attribute names in the VTK file follow the naming
            convention adopted by the Maha Fluid Power Research Center (see
            the :py:attr:`use_maha_name_convention` attribute for additional
            details).  Must be ``True`` to perform unit conversions on VTK
            array data (default is ``True``)
        coordinate_units : str, optional
            The units used by the coordinate system in the VTK file (default
            is ``None``).  If set to ``None``, no unit conversions can be
            performed for the VTK point locations
        """
        # SETUP --------------------------------------------------------------
        # Set "path" attribute, verify file exists, and store file hashes
        #   Mypy type annotation added because mmediately after calling
        #   `set_read_metadata()`, the "path" attribute cannot be `None`
        #   or else an error would have been thrown
        self.set_read_metadata(path)
        self.path: pathlib.Path

        # Store naming convention and verify that "coordinate_units"
        # is provided if and only if using the Maha naming convention
        self._use_maha_name_convention = bool(use_maha_name_convention)
        self._check_name_convention_compliance_unit(coordinate_units)

        # Store units of VTK grid points
        if self.use_maha_name_convention:
            # Verify that unit doesn't have spaces or other invalid characters
            permissible_chars \
                = string.ascii_letters + string.digits + '()[]{}*/+-^'

            if not pyxx.strings.str_includes_only(str(coordinate_units),
                                                  permissible_chars):
                raise ValueError(
                    f'Unit "{coordinate_units}" contains invalid characters')

            self._coordinate_units = str(coordinate_units)
        else:
            self._coordinate_units = None

        # READ VTK FILE ------------------------------------------------------
        # Set up VTK reader
        reader = vtk.vtkDataSetReader()
        reader.SetFileName(str(self.path))

        # Configure VTK to read all available VTK arrays
        reader.ReadAllFieldsOn()
        reader.ReadAllScalarsOn()
        reader.ReadAllVectorsOn()
        reader.ReadAllTensorsOn()

        # Read data from VTK file
        reader.Update()
        output = reader.GetOutput()

        # PARSE VTK FILE -----------------------------------------------------
        # Number of points stored in the file and coordinates of each point
        self._num_points = int(output.GetNumberOfPoints())

        x_points: List[float] = []
        y_points: List[float] = []
        z_points: List[float] = []
        for i in range(self.num_points):
            x, y, z = output.GetPoint(i)

            x_points.append(float(x))
            y_points.append(float(y))
            z_points.append(float(z))

        if use_maha_name_convention:
            df_data = {
                f'x[{self.coordinate_units}]': x_points,
                f'y[{self.coordinate_units}]': y_points,
                f'z[{self.coordinate_units}]': z_points,
            }
        else:
            df_data = {'x': x_points, 'y': y_points, 'z': z_points}

        self.__xyz_coordinate_columns = tuple(df_data.keys())

        # Read all arrays from VTK file
        point_data = output.GetPointData()
        data_id_names = list(self.__xyz_coordinate_columns)
        for i in range(point_data.GetNumberOfArrays()):
            identifier = str(point_data.GetArray(i).GetName())

            if identifier in self.__xyz_coordinate_columns:
                raise VTKIdentifierNameError(
                    f'Invalid VTK data identifier "{identifier}" (matches '
                    'name of one of the point coordinate columns)')

            if identifier in df_data:
                raise VTKIdentifierNameError(
                    f'Invalid VTK data identifier "{identifier}" (multiple '
                    'VTK data use the same identifier)')

            self._check_name_convention_compliance_id(identifier)
            if self.use_maha_name_convention:
                name = self._parse_column_id(identifier, 'name')

                if name in data_id_names:
                    raise VTKIdentifierNameError(
                        f'Invalid VTK data identifier "{identifier}" (multiple '
                        f'identifiers use the same name "{name}")')

                data_id_names.append(name)

            try:
                array = np.array(
                    vtk.util.numpy_support.vtk_to_numpy(point_data.GetArray(i)),
                    dtype=np.float64)
            except ValueError as exception:
                raise VTKFormatError(
                    f'VTK point data "{identifier}" does not appear to be a '
                    'valid array of numbers') from exception

            # Validate data format and perform pre-processing
            if array.shape[0] != self.num_points:
                raise VTKFormatError(
                    f'VTK point data "{identifier}" has {len(array)} '
                    'elements, which does not match number of VTK grid '
                    f'points ({self.num_points})')

            # Modify data to match expected format for Pandas
            if array.ndim == 1:  # Array contains a scalar for each grid point
                pd_array = list(array)
            elif array.ndim == 2:  # Array contains a vector for each grid point
                if not array.shape[1] == 3:
                    raise VTKFormatError(
                        'VTK vector data should have 3 components (x, y, z), '
                        f'but data specified by "{identifier}" has '
                        f'{array.shape[1]} components')

                pd_array = [(v[0], v[1], v[2]) for v in array]
            else:
                raise VTKFormatError(
                    f'VTK point data specified by "{identifier}" has invalid '
                    f'dimensions {array.shape}. Valid dimensions are:\n'
                    f'-- Scalar data: ({self.num_points},)\n'
                    f'-- Vector data: ({self.num_points}, 3)')

            # Store data
            df_data[identifier] = pd_array

        # CREATE PANDAS DATAFRAME --------------------------------------------
        self._df = pd.DataFrame(df_data)
