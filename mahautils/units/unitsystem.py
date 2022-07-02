"""
This module contains classes intended to represent a system of
units, such as the `International System of Units (SI)
<https://www.nist.gov/pml/weights-and-measures/metric-si/si-units>`__.
"""


class UnitSystem:
    """Base class representing a system of units

    Base class that can be used to represent a system of units
    with an arbitrary number of fundamental units

    Attributes
    ----------
    num_fundamental_units : int
        Number of fundamental units in the system of units
    name : str, optional
        Short name of the system of units (default is ``''``)
    description : str, optional
        Description of the system of units (default is ``''``)
    """
    def __init__(self, num_fundamental_units: int,
                 name: str = '', description: str = ''):
        # Store number of fundamental units
        if not(isinstance(num_fundamental_units, int)):
            raise TypeError(
                'Argument "num_fundamental_units" must be of type "int"')
        if num_fundamental_units <= 0:
            raise ValueError(
                'Argument "num_fundamental_units" must be positive')
        self._num_fundamental_units = num_fundamental_units

        # Store name and description
        if not(isinstance(name, str)):
            raise TypeError('Argument "name" must be of type "str"')
        self.name = name

        if not(isinstance(description, str)):
            raise TypeError('Argument "description" must be of type "str"')
        self.description = description

    def __repr__(self):
        return str(self)

    def __str__(self):
        representation = str(self.__class__)

        if self.name != '':
            representation += f' - {self.name}'

        if self.description != '':
            representation += f' - {self.description}'

        return representation

    @property
    def num_fundamental_units(self):
        """Returns the number of fundamental units in the system of units"""
        return self._num_fundamental_units


class UnitSystemSI(UnitSystem):
    """Class representing the SI system of units

    Class that can be used to represent the International System of
    Units (SI).  This system of units has 7 fundamental units, which
    are described in the "Notes" section.

    Notes
    -----
    The fundamental units in the SI system are:

    - Length: meter [m]
    - Time: second [s]
    - Amount of substance: mole [mole]
    - Electric current: ampere [A]
    - Temperature: Kelvin [K]
    - Luminous intensity: candela [cd]
    - Mass: kilogram [kg]

    References
    ----------
    https://www.nist.gov/pml/weights-and-measures/metric-si/si-units
    """
    def __init__(self):
        super().__init__(
            num_fundamental_units=7,
            name='SI',
            description='International System of Units'
        )
