"""This module provides a class intended for reading and parsing VTK files
used by the Maha Multics software.
"""

import pathlib
import re
from typing import List, Union, Optional

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

    def _check_vtk_id_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError(
                f'VTK data name {name} is not of type "str"')

        if self.use_maha_name_convention:
            if not re.match(r'^[^\s]+\[[^\s]+\]$', name):
                raise VTKIdentifierNameError(f'Invalid VTK data name: "{name}"')

    def read(self,
             path: Optional[Union[str, pathlib.Path]] = None,
             coordinate_units: Optional[str] = None,
             use_maha_name_convention: bool = True
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
        coordinate_units : str, optional
            The units used by the coordinate system in the VTK file (default
            is ``None``).  If set to ``None``, no unit conversions can be
            performed for the VTK point locations
        use_maha_name_convention : bool, optional
            Whether the attribute names in the VTK file follow the naming
            convention adopted by the Maha Fluid Power Research Center (see
            the :py:attr:`use_maha_name_convention` attribute for additional
            details).  Must be ``True`` to perform unit conversions on VTK
            array data (default is ``True``)
        """
        # SETUP --------------------------------------------------------------
        # Set "path" attribute, verify file exists, and store file hashes
        #   Mypy type annotation added because mmediately after calling
        #   `set_read_metadata()`, the "path" attribute cannot be `None`
        #   or else an error would have been thrown
        self.set_read_metadata(path)
        self.path: pathlib.Path

        # Store inputs
        self._coordinate_units = None if coordinate_units is None \
            else str(coordinate_units)
        self._use_maha_name_convention = bool(use_maha_name_convention)

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

        df_data = {'x': x_points, 'y': y_points, 'z': z_points}

        # Read all arrays from VTK file
        point_data = output.GetPointData()
        for i in range(point_data.GetNumberOfArrays()):
            name = str(point_data.GetArray(i).GetName())
            self._check_vtk_id_name(name)

            try:
                array = np.array(
                    vtk.util.numpy_support.vtk_to_numpy(point_data.GetArray(i)),
                    dtype=np.float64)
            except ValueError as exception:
                raise VTKFormatError(
                    f'VTK point data "{name}" does not appear to be a valid '
                    'array of numbers') from exception

            # Validate data format and perform pre-processing
            if array.shape[0] != self.num_points:
                raise VTKFormatError(
                    f'VTK point data "{name}" has {len(array)} elements, '
                    'which does not match number of VTK grid points '
                    f'({self.num_points})')

            # Modify data to match expected format for Pandas
            if array.ndim == 1:  # Array contains a scalar for each grid point
                pd_array = list(array)
            elif array.ndim == 2:  # Array contains a vector for each grid point
                if not array.shape[1] == 3:
                    raise VTKFormatError(
                        'VTK vector data should have 3 components (x, y, z), '
                        f'but data specified by "{name}" has {array.shape[1]} '
                        'components')

                pd_array = [(v[0], v[1], v[2]) for v in array]
            else:
                raise VTKFormatError(
                    f'VTK point data specified by "{name}" has invalid '
                    f'dimensions {array.shape}. Valid dimensions are:\n'
                    f'-- Scalar data: ({self.num_points},)\n'
                    f'-- Vector data: ({self.num_points}, 3)')

            # Store data
            df_data[name] = pd_array

        # CREATE PANDAS DATAFRAME --------------------------------------------
        self._df = pd.DataFrame(df_data)
