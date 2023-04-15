"""This module provides a class intended for reading and parsing VTK files
used by the Maha Multics software.
"""

import enum
import io
import pathlib
import re
import string
from typing import Any, Dict, List, Tuple, Union, Optional

# Mypy type checking disabled for packages that are not PEP 561-compliant
import numpy as np
import pandas as pd            # type: ignore
import pyxx
import scipy.interpolate       # type: ignore
import vtk                     # type: ignore
import vtk.util.numpy_support  # type: ignore  # pylint: disable=E0401,E0611

from mahautils.utils.capture_printing import CaptureStderr
from .exceptions import (
    FileNotParsedError,
    VTKIdentifierNameError,
    VTKInvalidIdentifierError,
    VTKFormatError,
)
from .units import MahaMulticsUnitConverter

# Type definitions
PointCoordinates = Union[List[float], Tuple[float, ...], np.ndarray]
ListOfPoints = Union[
    List[PointCoordinates],
    Tuple[PointCoordinates, ...],
    np.ndarray
]


class VTKDataType(enum.Enum):
    """The type of point data stored in a VTK file

    VTK files can store a variety of types of data (scalars, vectors, tensors,
    etc.).  This :py:class:`enum.Enum` specifies the different types that can
    be read by the MahaUtils package.
    """

    #: Scalar data series
    scalar = enum.auto()

    #: Vector data series
    vector = enum.auto()


class VTKFile(pyxx.files.BinaryFile):
    """An object for representing VTK files

    VTK files are commonly used with the Maha Multics software to store film
    property distributions and other simulation results.  This class provides
    the ability to read and parse such files, and perform tasks such as
    extracting particular data, converting the units of data stored in the VTK
    file, and plotting scalar property distributions.
    """

    # Regular expression describing expected format for VTK data identifiers
    # to facilitate unit conversions
    __unit_conversion_regex = r'^([^\s]+)\[([^\s]+)\]$'

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
        self._vtk_data_types: Dict[str, VTKDataType] = {}

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
    def identifiers(self) -> List[str]:
        """The list of all VTK data identifiers for data stored in the file"""
        return list(self._df.columns)

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
    def unit_conversion_enabled(self) -> bool:
        """Whether the :py:class:`VTKFile` instance is capable of performing
        unit conversions on VTK data

        VTK files don't inherently store data.  However, it can be useful to
        perform unit conversions and extract data from VTK files in different
        units than the data were stored.  The :py:class:`VTKFile` provides
        such unit conversion capability, but in order to do so, the user must
        appropriately name the data identifiers in the VTK file such that they
        include the unit in which the data are stored.

        The naming convention adopted in this package to facilitate unit
        conversions for VTK data requires that VTK data identifiers (for both
        scalar and vector data) are formatted in two parts: (1) a descriptive
        name, (2) the unit in square brackets.  There should be no whitespace
        in any part of the identifier.

        For instance, one potential identifier that could denote VTK data
        storing pressure in units of Pascal might be: ``pressure[Pa]``.
        Similarly, an identifier for VTK data storing the velocity of a
        tractor might be ``tractorVelocity[m/s]``.
        """
        try:
            return self._unit_conversion_enabled
        except AttributeError as exception:
            raise FileNotParsedError(
                'VTK identifier naming convenction is not defined; VTK file '
                'has not yet been read') from exception

    @property
    def unit_converter(self) -> pyxx.units.UnitConverter:
        """The unit converter used to perform unit conversions for quantities
        stored in the VTK file

        This attribute must be an instance or subclass of a
        :py:class:`pyxx.units.UnitConverter` object.  Unit conversions are
        only performed if :py:attr:`unit_conversion_enabled` is ``True``.
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

    def _check_unit_conversion_compliance_args(self, unit: Any) -> None:
        """Verifies that, when retrieving VTK data, the user specified or
        omitted a unit in agreement with the unit conversion settings
        specified by :py:attr:`unit_conversion_enabled`

        Several methods in the :py:class:`VTKFile` class retrieve VTK data
        and perform unit conversions if :py:attr:`unit_conversion_enabled`
        is ``True``.  These methods need to verify that a unit was provided
        when unit conversions are enabled, and to avoid user confusion and
        potential bugs (i.e., a user thinks a unit conversion is being
        performed but it is not), the method should verify that a unit was not
        provided if unit conversions are disabled.  Rather than repeating the
        code to perform this check throughout the :py:class:`VTKFile` class
        source code, this method can be called and will throw a descriptive
        error if any of the aforementioned conditions are not satisfied.

        Parameters
        ----------
        unit : Any
            The argument passed by the user specifying the unit to which VTK
            data should be converted (or ``None`` if no unit was specified)

        Raises
        ------
        TypeError
            If unit conversions are disabled but the user specified a unit, or
            if unit conversions are enabled but the user omitted a unit
        """
        if self.unit_conversion_enabled:
            if unit is None:
                raise TypeError(
                    'VTK unit conversions are enabled, so argument "unit" '
                    'cannot be `None`')

        elif unit is not None:
            raise TypeError(
                'VTK unit conversions are not enabled, so argument "unit" '
                'must be `None`')

    def _check_unit_conversion_compliance_id(self, identifier: str) -> None:
        """Verifies that a given VTK data identifier matches the naming
        convention required by :py:attr:`unit_conversion_enabled`

        VTK data identifiers must be strings, and if unit conversions are
        enabled (:py:attr:`unit_conversion_enabled` is ``True``), then the
        VTK data identifiers must follow a specific format including the unit.
        This method confirms that these requirements are met, and throws a
        descriptive error if they are not.

        Parameters
        ----------
        identifier : str
            The VTK data identifier (i.e., the column name of the VTK data
            DataFrame stored in :py:attr:`pointdata_df`) to be checked

        Raises
        ------
        TypeError
            If ``identifier`` is not of type ``str``
        VTKIdentifierNameError
            If :py:attr:`unit_conversion_enabled` is ``True`` and
            ``identifier`` does not match the required format (described for
            the :py:attr:`unit_conversion_enabled` attribute)
        """
        if not isinstance(identifier, str):
            raise TypeError(
                f'VTK data name {identifier} is not of type "str"')

        if self.unit_conversion_enabled:
            if not re.match(self.__unit_conversion_regex, identifier):
                raise VTKIdentifierNameError(
                    f'Invalid VTK data identifier: "{identifier}"')

    def _find_column_id(self, identifier: str) -> str:
        # Validate inputs
        if not isinstance(identifier, str):
            raise TypeError('Argument "identifier" must be of type "str"')

        # If unit conversions are disabled, simply check that the
        # identifier exists as one of the DataFrame columns
        if not self.unit_conversion_enabled:
            if identifier not in self._df:
                raise VTKInvalidIdentifierError(
                    f'Data specified by identifier "{identifier}" not found '
                    'in VTK file')

        # If unit conversions are enabled, users can specify the identifier
        # with or without the unit (e.g., 'pFilm[bar]' or 'pFilm'), so
        # determine which of these is a valid column name (and if neither,
        # throw an error)
        else:
            if identifier not in self._df:
                matches = []
                for column in self._df.columns:
                    if identifier == self._parse_column_id(column, 'name'):
                        matches.append(column)

                if len(matches) == 0:
                    raise VTKInvalidIdentifierError(
                        f'Data specified by identifier "{identifier}" not found '
                        'in VTK file')

                if len(matches) > 1:
                    # Ideally, it should never be possible to reach this
                    # statement because an error would have been thrown while
                    # reading the VTK file.  However, this check is still
                    # implemented as a backup precaution

                    raise VTKInvalidIdentifierError(  # pragma: no cover
                        f'Identifier "{identifier}" matches multiple data '
                        f'fields in the VTK file: {matches}')

                # At this point, there must be only a single item in `matches`,
                # corresponding to the column name of the VTK data identifier
                identifier = matches[0]

        return identifier

    def _parse_column_id(self, identifier: str, target: str) -> str:
        if not self.unit_conversion_enabled:
            raise AttributeError(
                'Parsing VTK data identifier is not a valid action when VTK '
                'unit conversions are disabled')

        matches = re.search(self.__unit_conversion_regex, str(identifier))

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
            ``None``).  Must be provided if :py:attr:`unit_conversion_enabled`
            is ``True`` and omitted if :py:attr:`unit_conversion_enabled` is
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
        """Returns a NumPy array containing a single VTK data field

        VTK files store data (scalars, vectors, etc.) at a set of defined grid
        points in 3D.  This method retrieves a single such field of data (i.e.,
        it retrieves one column in :py:attr:`pointdata_df`), and returns the
        resulting values in a NumPy array.

        Parameters
        ----------
        identifier : str
            The identifier specifying the data in the VTK file to return
        unit : str, optional
            The units in which the data should be returned (only applicable if
            :py:attr:`unit_conversion_enabled` is ``True``; otherwise, must
            not be specified)

        Returns
        -------
        np.ndarray
            A NumPy array containing the data corresponding to ``identifier``
            in the VTK file
        """
        # SETUP --------------------------------------------------------------
        # Verify that file has been read
        if not hasattr(self, '_df'):
            raise FileNotParsedError(
                'Unable to retrieve VTK data; VTK file has not yet '
                'been read')

        # Check that identifier matches a single column in the DataFrame
        identifier = self._find_column_id(identifier)

        # Verify that unit was provided if and only if unit conversions
        # are enabled
        self._check_unit_conversion_compliance_args(unit)

        # Extract raw data from DataFrame
        raw_data = self._df[identifier].to_numpy()

        if raw_data.dtype != np.float64:
            # For vector data, the Pandas `.to_numpy()` method returns a
            # NumPy array with `dtype=object`.  Vector data should be an array
            # of floating-point numbers, which is performed here
            raw_data = np.array([x.astype(np.float64) for x in raw_data])

        # CASE 1: Unit conversions disabled ----------------------------------
        if not self.unit_conversion_enabled:
            return raw_data

        # CASE 2: Unit conversions enabled -----------------------------------
        # Convert raw data units
        from_unit = self._parse_column_id(identifier, 'unit')
        return self.unit_converter.convert(
            raw_data, from_unit=from_unit, to_unit=str(unit))

    def extract_dataframe(self, identifiers: List[str],
                          units: Optional[List[str]] = None) -> pd.DataFrame:
        """Returns a Pandas DataFrame containing one or more VTK data fields

        VTK files store data (scalars, vectors, etc.) at a set of defined grid
        points in 3D.  This method retrieves one or more such fields of data
        (i.e., it retrieves one or more columns in :py:attr:`pointdata_df`),
        and returns the resulting values in a Pandas DataFrame.

        Parameters
        ----------
        identifiers : list of str
            The (one or more) identifiers specifying the data in the VTK file
            to return
        units : list of str, optional
            The units in which the data should be returned (only applicable if
            :py:attr:`unit_conversion_enabled` is ``True``; otherwise, must
            not be specified).  If supplied, ``units`` should be a list of
            strings of equal length as ``identifiers``

        Returns
        -------
        pd.DataFrame
            A Pandas DataFrame containing the columns of :py:attr:`pointdata_df`
            corresponding to ``identifiers`` in the VTK file
        """
        # SETUP --------------------------------------------------------------
        # Verify that file has been read
        if not hasattr(self, '_df'):
            raise FileNotParsedError(
                'Unable to retrieve VTK data; VTK file has not yet '
                'been read')

        # Verify that unit was provided if and only if unit conversions
        # are enabled
        self._check_unit_conversion_compliance_args(units)

        # CASE 1: Unit conversions disabled ----------------------------------
        if not self.unit_conversion_enabled:
            df_data = {
                identifier: list(self.extract_data_series(identifier))
                    for identifier in identifiers  # noqa: E131
            }

        # CASE 2: Unit conversions enabled -----------------------------------
        else:
            # Ensure that units are a list of strings
            #   Add Mypy exclusion because if "units" is `None`, an error
            #   would have been thrown by unit conversion compliance check
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
                    = list(self.extract_data_series(identifier, unit))

        return pd.DataFrame(df_data)

    def interpolate(self, identifier: str,
                    query_points: ListOfPoints,
                    interpolator_type: str,
                    output_units: Optional[str] = None,
                    query_point_units: Optional[str] = None,
                    interpolate_axes:
                        Union[List[str], Tuple[str, ...], str]
                        = ('x', 'y', 'z'),
                    idx_slice: Union[slice, tuple] = slice(None),
                    **kwargs
                    ) -> np.ndarray:
        """Interpolates data from the VTK file

        Retrieves the value of a given data field stored in the VTK file,
        interpolating between VTK grid points if necessary.  Interpolation is
        performed using the :py:mod:`scipy.interpolate` package
        (https://docs.scipy.org/doc/scipy/reference/interpolate.html).

        Parameters
        ----------
        identifier : str
            The identifier specifying the data in the VTK file to return
        query_points : tuple or list or np.ndarray
            The point(s) at which to return possibly interpolated value(s) of
            the VTK data corresponding to ``identifier``
        interpolator_type : str
            The SciPy interpolation function to use to perform interpolation.
            Can be selected from any of the options in the "Notes" section
        output_units : str, optional
            The units in which the data should be returned (only applicable if
            :py:attr:`unit_conversion_enabled` is ``True``; otherwise, must
            not be specified)
        query_point_units : str, optional
            The units of the ``query_points`` argument (only applicable if
            :py:attr:`unit_conversion_enabled` is ``True``; otherwise, must
            not be specified)
        interpolate_axes : list or tuple or set or str, optional
            The coordinate axes on which interpolation should be performed.
            Must be selected from any combination of ``'x'``, ``'y'``, and
            ``'z'`` (default is ``('x', 'y', 'z')``)
        idx_slice : slice or tuple, optional
            Filters the points in the VTK file and only uses a subset of
            points for interpolation (default is ``slice(None)`` which uses
            all points in the VTK file).  See the "Notes" section for more
            information
        **kwargs
            Any keyword arguments to be supplied to the SciPy interpolation
            function specified by ``interpolator_type``.  See the "Notes"
            section for more information

        Returns
        -------
        np.ndarray
            The interpolated value(s) of the VTK data given by ``identifier``
            at the query points ``query_points``

        Notes
        -----
        **Interpolation Functions**

        The following interpolation functions are available (set the
        ``interpolator_type`` argument to the given string to use each):

        - ``'griddata'``: The :py:class:`scipy.interpolate.griddata`
          interpolation function for unstructured, multivariate interpolation
          (`reference <https://docs.scipy.org/doc/scipy/reference/generated
          /scipy.interpolate.griddata.html>`__)
        - ``'RBFInterpolator'``: The :py:class:`scipy.interpolate.RBFInterpolator`
          function for unstructured, multivariate interpolation using a radial
          basis function (`reference <https://docs.scipy.org/doc/scipy/reference
          /generated/scipy.interpolate.RBFInterpolator.html>`__)

        Review the SciPy documentation for questions about parameters for the
        interpolation functions.  **These interpolation functions require data
        and interpolation parameters to meet specific mathematical requirements,
        and errors may be encountered if such requirements are not met.**  This
        may require using non-default parameters of the :py:meth:`interpolate`
        method.

        For instance, if your VTK file is defined on a 2D ``xy``-plane and you
        attempt to perform 3D interpolation (i.e., you set ``interpolation_axes``
        to ``('x', 'y', 'z')``) using ``griddata`` with ``method='linear'``, an
        error will be thrown.  In this case, you need to reduce the problem to
        a 2D interpolation by setting ``interpolation_axes`` to ``('x', 'y')``.

        **Point Coordinates**

        The order in which ``interpolate_axes`` values are provided must be in
        the following sequence: ``(x, y, z)``.  An error will be thrown if an
        argument such as ``interpolate_axes=('y', 'x', 'z')`` is provided.

        **Filtering/Slicing Points**

        In some cases, it may be desirable to perform interpolation using only
        a subset of points in the VTK file.  For instance, if a lubricating
        film lies on a specific face, it may be desirable to only perform
        interpolation using that face.

        The ``idx_slice`` argument facilitates this use case.  Either a Python
        :py:class:`slice` object can be passed as input, or a tuple of array
        indices generated by NumPy's :py:meth:`index_exp` or :py:meth:`np.s_`
        methods (`more information <https://numpy.org/doc/stable/reference
        /generated/numpy.s_.html>`__).

        Note that if using :py:meth:`index_exp` or :py:meth:`np.s_`, only a
        1D index tuple should be generated (e.g., ``np.index_exp[0:4]``).  An
        easy way to test the index tuple is to apply it to the output of
        :py:meth:`points` (e.g., ``vtk_file.points()[np.index_exp[...]]``)
        and observe whether the desired points are extracted (these are the
        points that would be used for interpolation).
        """
        # Validate inputs
        axes = list(interpolate_axes)
        num_axes = len(axes)

        allowed_axes = {'x', 'y', 'z'}
        if not set(axes).issubset(allowed_axes):
            raise ValueError(
                'Argument "interpolate_axes" contains invalid items: '
                f'{set(axes) - allowed_axes}')

        if len(set(axes)) != len(axes):
            raise ValueError(
                'Argument "interpolate_axes" contains duplicate values')

        if not (1 <= num_axes <= 3):
            raise ValueError('Number of interpolation dimensions must be '
                             'between 1 and 3 (inclusive)')

        if not axes == sorted(axes):
            raise ValueError(
                'Argument "interpolate_axes" must be in the following '
                f'sequence: {sorted(axes)}')

        self._check_unit_conversion_compliance_args(output_units)
        self._check_unit_conversion_compliance_args(query_point_units)

        try:
            # Convert query points to NumPy array
            query_points_ndarray = np.array(query_points, dtype=np.float64)

            if query_points_ndarray.ndim == 1:
                query_points_ndarray = np.expand_dims(query_points_ndarray,
                                                      axis=0)

            # Check that query points have expected shape
            if not query_points_ndarray.ndim == 2:
                raise ValueError('Query points must be provided as a 2D array')

            if not query_points_ndarray.shape[1] == num_axes:
                raise ValueError(
                    f'Query points must each have {num_axes} coordinates '
                    f'({", ".join(sorted(axes))})')

        except ValueError as exception:
            raise ValueError(
                'Invalid format of "query_points" argument. This argument '
                f'should be provided as a shape (N,{num_axes}) NumPy array '
                'of N points') from exception

        if not isinstance(idx_slice, slice):
            if not isinstance(idx_slice, tuple):
                raise TypeError(
                    'Argument "idx_slice" must be of type "slice" or "tuple"')

            if len(idx_slice) != 1:
                raise ValueError('Argument "idx_slice" is of type "tuple" '
                                 'but length is not 1')

        # Extract point coordinates of all points in VTK file
        coordinates = []
        if 'x' in axes:
            coordinates.append(self.coordinates('x', query_point_units)[idx_slice])
        if 'y' in axes:
            coordinates.append(self.coordinates('y', query_point_units)[idx_slice])
        if 'z' in axes:
            coordinates.append(self.coordinates('z', query_point_units)[idx_slice])

        points = np.stack(coordinates, axis=1)

        # Extract scalar data for all points in VTK file
        scalar_data = self.extract_data_series(identifier, output_units)[idx_slice]

        # Perform interpolation
        if (interpolator_type == 'griddata'):
            return scipy.interpolate.griddata(
                points = points,
                values = scalar_data,
                xi     = query_points_ndarray,
                **kwargs
            )

        if (interpolator_type == 'RBFInterpolator'):
            interpolator = scipy.interpolate.RBFInterpolator(
                y = points,
                d = scalar_data,
                **kwargs
            )

            return interpolator(query_points_ndarray)

        raise ValueError(f'Interpolator "{interpolator_type}" is not supported')

    def is_scalar(self, identifier: str) -> bool:
        """Whether a given VTK data identifier stores scalar point data

        Parameters
        ----------
        identifier : str
            The VTK data identifier to analyze

        Returns
        -------
        bool
            Returns ``True`` if the VTK data identifier given by ``identifier``
            stores scalar data, and ``False`` otherwise
        """
        column = self._find_column_id(identifier)
        return self._vtk_data_types[column] == VTKDataType.scalar

    def is_vector(self, identifier: str) -> bool:
        """Whether a given VTK data identifier stores vector point data

        Parameters
        ----------
        identifier : str
            The VTK data identifier to analyze

        Returns
        -------
        bool
            Returns ``True`` if the VTK data identifier given by ``identifier``
            stores vector data, and ``False`` otherwise
        """
        column = self._find_column_id(identifier)
        return self._vtk_data_types[column] == VTKDataType.vector

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
            ``None``).  Must be provided if :py:attr:`unit_conversion_enabled`
            is ``True`` and omitted if :py:attr:`unit_conversion_enabled` is
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
             unit_conversion_enabled: bool = False,
             coordinate_units: Optional[str] = None,
             strict: bool = False,
             fallback_units: Optional[Dict[str, str]] = None
             ) -> None:
        """Reads a VTK file from the disk

        This method reads a VTK file from the disk, parsing its content and
        storing the data as a Pandas DataFrame in the :py:attr:`pointdata_df`
        attribute.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            The path and filename from which to read the VTK file (default is
            ``None``).  If not provided or ``None``, the file will be read
            from the location specified by the :py:attr:`path` attribute
        unit_conversion_enabled : bool, optional
            Whether to enable unit conversions for the VTK file data (see
            the :py:attr:`unit_conversion_enabled` attribute for additional
            details) (default is ``False``)
        coordinate_units : str, optional
            The units used by the coordinate system in the VTK file (default
            is ``None``).  Must be provided if :py:attr:`unit_conversion_enabled`
            is ``True`` and omitted if :py:attr:`unit_conversion_enabled` is
            ``False``
        strict : bool, optional
            Whether to throw an exception if the data in the VTK file being
            read are not formatted in a valid way
        fallback_units : dict, optional
            This setting allows VTK files where some data are missing units
            in the identifier to still be read with unit conversions enabled.
            Must be a dictionary where keys and values are both strings.  If
            :py:attr:`unit_conversion_enabled` is ``True`` and a VTK data
            identifier does not include the data units, then if there is a key
            in ``fallback_units`` matching the identifier, the corresponding
            value in ``fallback_units`` will be set as the units

        Warnings
        --------
        If there are two point data fields in the VTK file with exactly the
        same identifier, only one of the fields (the last one with the
        identifier) will be read.

        Setting ``strict`` to ``True`` modifies the ``stderr`` file descriptor,
        including redirecting ``stderr`` to a temporary file, so it can cause
        problems for other code that relies on streams (for instance, it may
        cause ``unittest`` tests to fail in some cases).
        """
        # SETUP --------------------------------------------------------------
        # Set "path" attribute, verify file exists, and store file hashes
        #   Mypy type annotation added because immediately after calling
        #   `set_read_metadata()`, the "path" attribute cannot be `None`
        #   or else an error would have been thrown
        self.set_read_metadata(path)
        self.path: pathlib.Path

        # Enable/disable unit conversion and verify that "coordinate_units"
        # is provided if and only if unit conversions are enabled
        self._unit_conversion_enabled = bool(unit_conversion_enabled)
        self._check_unit_conversion_compliance_args(coordinate_units)

        # Store units of VTK grid points
        if self.unit_conversion_enabled:
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
        if strict:
            stderr_stream = io.BytesIO()
            with CaptureStderr(stderr_stream):
                reader.Update()

            if len(stderr_stream.getvalue()) > 0:
                error_message = stderr_stream.getvalue().decode("utf_8")

                raise VTKFormatError(
                    f'VTK file "{self.path}" could not be read successfully. '
                    f'The following error was encountered: {error_message}')
        else:
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

        if unit_conversion_enabled:
            df_data = {
                f'x[{self.coordinate_units}]': x_points,
                f'y[{self.coordinate_units}]': y_points,
                f'z[{self.coordinate_units}]': z_points,
            }
        else:
            df_data = {'x': x_points, 'y': y_points, 'z': z_points}

        self.__xyz_coordinate_columns = tuple(df_data.keys())

        self._vtk_data_types \
            = dict(zip(self.__xyz_coordinate_columns,
                       [VTKDataType.scalar] * len(self.__xyz_coordinate_columns)))

        # Read all arrays from VTK file
        point_data = output.GetPointData()

        if self.unit_conversion_enabled:
            data_id_names = [self._parse_column_id(x, 'name')
                             for x in self.__xyz_coordinate_columns]
        else:
            data_id_names = list(self.__xyz_coordinate_columns)

        for i in range(point_data.GetNumberOfArrays()):
            identifier = str(point_data.GetArray(i).GetName())

            if identifier in self.__xyz_coordinate_columns:
                raise VTKIdentifierNameError(
                    f'Invalid VTK data identifier "{identifier}" (matches '
                    'name of one of the point coordinate columns)')

            try:
                self._check_unit_conversion_compliance_id(identifier)
            except VTKIdentifierNameError:
                if (fallback_units is not None) and (identifier in fallback_units):
                    # Add units to data identifier
                    identifier = identifier + f'[{fallback_units[identifier]}]'

                    # Re-check identifier format compliance
                    self._check_unit_conversion_compliance_id(identifier)
                else:
                    raise

            if self.unit_conversion_enabled:
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
                self._vtk_data_types[identifier] = VTKDataType.scalar
                pd_array = list(array)
            elif array.ndim == 2:  # Array contains a vector for each grid point
                if not array.shape[1] == 3:
                    raise VTKFormatError(
                        'VTK vector data should have 3 components (x, y, z), '
                        f'but data specified by "{identifier}" has '
                        f'{array.shape[1]} components')

                self._vtk_data_types[identifier] = VTKDataType.vector
                pd_array = [np.array([v[0], v[1], v[2]]) for v in array]
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
