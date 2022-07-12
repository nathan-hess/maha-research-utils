"""
This module contains classes for representing units that are part of a given
system of units.
"""

from typing import Any, Callable, List, Optional, Tuple, Union

import numpy as np

from .unitsystem import UnitSystem, UnitSystemSI

# Disable Pylint's "unused argument" warnings.  In this case, we want to allow
# users to pass keyword arguments but ignore them -- this allows users to
# define different units using the same code.
#
# For instance, using the line below, if users set "myUnit" using one
# of the lines below:
#   myUnit = mahautils.units.Unit(...)
#   myUnit = mahautils.units.UnitLinearSI(...)
# Then they can easily define different units using the same code:
#   unit = myUnit(unit_system=UnitSystem(1), ...)
#
# However, if units didn't accept other keyword arguments, then this approach
# would fail because the different classes of units in this module require
# different combinations of keyword arguments
#
# pylint: disable=unused-argument


class Unit:
    """Base class for representing a unit

    This class can be used to represent an arbitrary unit that is part
    of a given system of units

    Attributes
    ----------
    derived_exponents : np.ndarray
        A list of exponents relating the given object's units to the
        fundamental/base units of the unit system
    identifier : str
        A short identifier describing the unit (example: kg)
    from_base_function : Callable[[np.ndarray], np.ndarray]
        A function that transforms a value in the base units of
        ``self.unit_system`` to the given object's units
    name : str
        A name describing the unit (example: kilogram)
    to_base_function : Callable[[np.ndarray], np.ndarray]
        A function that transforms a value in the given object's units
        to a value using only the base units of ``self.unit_system``
    unit_system : mahautils.units.UnitSystem
        The system of units to which the unit belongs

    Methods
    -------
    from_base()
        Converts a value or array from base units of the unit
        system to the given unit
    to_base()
        Converts a value or array from the given unit to the base
        units of the unit system
    """

    def __init__(self, unit_system: UnitSystem,
                 derived_exponents: Union[List[float], Tuple[float, ...],
                                          np.ndarray],
                 to_base_function: Callable[[np.ndarray], np.ndarray],
                 from_base_function: Callable[[np.ndarray], np.ndarray],
                 identifier: Optional[str] = None, name: Optional[str] = None,
                 **kwargs: Any):
        """Define an arbitrary unit

        Defines a fundamental or derived unit that is part of a given system
        of units

        Parameters
        ----------
        unit_system : mahautils.units.UnitSystem
            The system of units to which the unit belongs
        derived_exponents : list or tuple or np.ndarray
            A 1D list of exponents relating the given object's units to the
            fundamental/base units of the unit system
        to_base_function : Callable[[np.ndarray], np.ndarray]
            A function that transforms a value in the given object's units
            to a value using only the base units of ``self.unit_system``
        from_base_function : Callable[[np.ndarray], np.ndarray]
            A function that transforms a value in the base units of
            ``self.unit_system`` to the given object's units
        identifier : str, optional
            A short identifier describing the unit (example: kg) (default
            is ``None``)
        name : str, optional
            A name describing the unit (example: kilogram) (default
            is ``None``)
        **kwargs : Any, optional
            Other keyword arguments (can be passed as inputs but are ignored)
        """
        # Store system of units
        self._unit_system = unit_system

        # Store identifier and name
        if not(identifier is None or isinstance(identifier, str)):
            raise TypeError('Argument "identifier" must be of type "str"')
        self._identifier = identifier

        if not(name is None or isinstance(name, str)):
            raise TypeError('Argument "name" must be of type "str"')
        self._name = name

        # Store exponents relating unit to fundamental units
        self._derived_exponents = np.array([float(i) for i in derived_exponents])

        # Verify that number of fundamental units matches that of unit system
        if len(self.derived_exponents) != self.unit_system.num_fundamental_units:
            raise ValueError(
                'Argument "derived_exponents" implies '
                f'{len(self.derived_exponents)} fundamental units but unit '
                f'system "{self.unit_system}" has '
                f'{self.unit_system.num_fundamental_units} fundamental units')

        # Store functions to transform to or from base units
        self._to_base_function = to_base_function
        self._from_base_function = from_base_function

    def __repr__(self):
        return f'{self.__class__} {str(self)}'

    def __str__(self):
        representation = ''

        if self.identifier is not None:
            representation += f'{self.identifier} - '

        if self.name is not None:
            representation += f'{self.name} - '

        representation += f'{self.derived_exponents}'

        return representation

    @property
    def derived_exponents(self):
        """Returns the exponents relating the unit to fundamental units"""
        return self._derived_exponents

    @property
    def identifier(self):
        """Returns an identifier describing the unit

        Returns a user-defined string that represents the unit
        (examples: kg, m, rad)
        """
        return self._identifier

    @property
    def from_base_function(self):
        """Returns the function that transforms a value from the base units
        of the unit system to the given unit"""
        return self._from_base_function

    @property
    def name(self):
        """Returns the name describing the unit

        Returns a user-defined string that describes the unit
        (examples: kilogram, meter, radian)
        """
        return self._name

    @property
    def to_base_function(self):
        """Returns the function that transforms a value from the given unit
        to the base units of the unit system"""
        return self._to_base_function

    @property
    def unit_system(self):
        """Returns the system of units to which the unit belongs"""
        return self._unit_system

    def from_base(self, value: Union[np.ndarray, list, tuple, float]):
        """Converts a value or array from base units of the unit
        system to the given unit"""
        inputs = np.array(value)

        return self.from_base_function(inputs)

    def to_base(self, value: Union[np.ndarray, list, tuple, float]):
        """Converts a value or array from the given unit to the base
        units of the unit system"""
        inputs = np.array(value)

        return self.to_base_function(inputs)


class UnitLinear(Unit):
    """Class for representing units with linear transformations to/from
    the base units

    Defines a unit in which the transformations to/from the base units
    of the system of units (that is, the functions given by
    ``self.from_base_function`` and ``self.to_base_function``) are linear

    Attributes
    ----------
    offset : float
        Constant value added when converting from the given object's
        units to the base units
    scale : float
        Multiplicative factor applied when converting from the given
        object's units to the base units

    See Also
    --------
    mahautils.units.Unit : Parent class

    Notes
    -----
    To convert an array of arbitrary dimensions ``inputs`` from the given
    object's units to the base units, the following equation is applied:

    .. code-block:: python

        outputs = (scale * inputs) + offset
    """

    def __init__(self, unit_system: UnitSystem,
                 derived_exponents: Union[List[float], Tuple[float, ...],
                                          np.ndarray],
                 scale: float, offset: float,
                 identifier: Optional[str] = None, name: Optional[str] = None,
                 **kwargs):
        # Store inputs
        if not isinstance(scale, (float, int, np.number)):
            raise TypeError('Argument "scale" must be of type "float"')
        self._scale = float(scale)

        if not isinstance(scale, (float, int, np.number)):
            raise TypeError('Argument "scale" must be of type "float"')
        self._offset = float(offset)

        # Initialize object
        super().__init__(
            unit_system        = unit_system,
            derived_exponents  = derived_exponents,
            to_base_function   = lambda x: scale * x + offset,
            from_base_function = lambda x: (x - offset) / scale,
            identifier         = identifier,
            name               = name
        )

    def __str__(self):
        return f'{super().__str__()} - scale: {self.scale} - offset: {self.offset}'

    @property
    def offset(self):
        """Returns the constant value added when converting from the given
        object's units to the base units"""
        return self._offset

    @property
    def scale(self):
        """Returns the multiplicative factor applied when converting from
        the given object's units to the base units"""
        return self._scale


class UnitLinearSI(UnitLinear):
    """Class for representing units with linear transformations to/from
    the base units and using the International System of Units (SI)

    See Also
    --------
    mahautils.units.Unit : Parent class
    mahautils.units.UnitLinear : Parent class
    """

    def __init__(self,
                 derived_exponents: Union[List[float], Tuple[float, ...],
                                          np.ndarray],
                 scale: float, offset: float,
                 identifier: Optional[str] = None, name: Optional[str] = None,
                 **kwargs):
        super().__init__(
            unit_system       = UnitSystemSI(),
            derived_exponents = derived_exponents,
            scale             = scale,
            offset            = offset,
            identifier        = identifier,
            name              = name
        )
