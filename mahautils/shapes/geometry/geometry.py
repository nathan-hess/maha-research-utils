"""Class for representing arbitrary geometry
"""

from typing import Optional, Union


class Geometry:
    """Base class for representing arbitrary geometry
    """

    def __init__(self, units: Optional[str] = None) -> None:
        """Creates a new object representing arbitrary geometry

        Parameters
        ----------
        units : str, optional
            The units in which the geometry is defined, or ``None`` to
            indicate dimensionless geometry or that units are to be ignored
            (default is ``None``)
        """
        self.units = units

    @property
    def units(self) -> Union[str, None]:
        """The units in which the geometry is defined"""
        return self._units

    @units.setter
    def units(self, units: Optional[str]) -> None:
        if units is None:
            self._units = None
        else:
            self._units = str(units)

    def _has_identical_units(self, geometry: 'Geometry') -> bool:
        """Checks that the units of two :py:class:`Geometry` objects are
        identical

        Parameters
        ----------
        geometry : Geometry
            Another :py:class:`Geometry` instance or subclass whose units to
            check

        Returns
        -------
        bool
            Returns ``True`` if both objects have units of ``None`` or
            identical units, and ``False`` otherwise
        """
        if self.units is None:
            return geometry.units is None

        if geometry.units is None:
            return self.units is None

        return self.units == geometry.units
