"""This module provides a class intended for reading and parsing VTK files
used by the Maha Multics software.
"""

import pathlib
import re
from typing import List, Union, Optional
import string

import numpy as np
import pandas as pd            # type: ignore
import pyxx
import vtk                     # type: ignore
import vtk.util.numpy_support  # type: ignore  # pylint: disable=E0401,E0611

from .exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
    VTKFormatError,
)


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
                 **kwargs) -> None:
        """Creates an object that can parse data from a VTK file

        Creates an instance of the :py:class:`VTKFile` class and optionally
        reads and parses a specified VTK file.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename of the VTK file to read and parse (default
            is ``None``).  If set to ``None``, no VTK file is read
        **kwargs
            Any valid arguments (other than ``path``) for the :py:meth:`read`
            method can be passed to this constructor as keyword arguments
        """
        super().__init__(path)

        # Initialize variables
        self._coordinate_units: Union[str, None] = None

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

        # Store inputs
        self._use_maha_name_convention = bool(use_maha_name_convention)

        if self.use_maha_name_convention:
            if coordinate_units is None:
                raise ValueError(
                    'If using the Maha VTK identifier naming convention, '
                    'then argument "coordinate_units" cannot be `None`')

            permissible_chars \
                = string.ascii_letters + string.digits + '()[]{}*/+-^'
            if not pyxx.strings.str_includes_only(coordinate_units,
                                                  permissible_chars):
                raise ValueError(
                    f'Unit "{coordinate_units}" contains invalid characters')

            self._coordinate_units = str(coordinate_units)
        else:
            if coordinate_units is not None:
                raise ValueError(
                    'If not using the Maha VTK identifier naming convention, '
                    'then argument "coordinate_units" must be `None`')
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
