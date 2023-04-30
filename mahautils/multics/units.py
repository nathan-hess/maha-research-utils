"""Unit conversion utilities for the :py:mod:`mahautils.multics` module.  The
classes in this module are intended to aid in performing unit conversions when
reading and writing Maha Multics-related files.  The units typically defined
in Maha Multics input files are included by default in these unit converter
objects.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pyxx

from .constants import (
    _DEG_C_TO_K_OFFSET,
    _DEG_F_TO_K_OFFSET,
    _DEG_F_TO_K_SCALE,
    _LBF_TO_N_SCALE,
    _LBM_TO_KG_SCALE,
    _IN_TO_M_SCALE,
    _PSI_TO_PA_SCALE,
    ATMOSPHERIC_PRESSURE_PA,
)


# Custom system of units
class MahaMulticsUnitSystem(pyxx.units.UnitSystem):
    """A Maha Multics-specific system of units

    This class is a modified version of the :py:class:`pyxx.units.UnitSystem`
    class.  It represents a system of units similar to SI, with the following
    base units:

    1. Mass: kilogram [:math:`kg`]
    2. Length: meter [:math:`m`]
    3. Time: second [:math:`s`]
    4. Temperature: Kelvin [:math:`K`]
    5. Amount of substance: mole [:math:`mol`]
    6. Electric current: ampere [:math:`A`]
    7. Luminous intensity: candela [:math:`cd`]

    By using a custom system of units for Maha Multics, it automatically
    ensures that unit conversions can only be performed for Maha
    Multics-compatible units.
    """

    def __init__(self):
        """Creates an instance of a Maha Multics-specific system of units
        with seven base units
        """
        super().__init__(
            num_base_units=7,
            name='SI',
            description=('International System of Units, customized for the '
                         'Maha Multics software')
        )


# Custom unit class that automatically uses the Maha Multics-specific
# system of units
class MahaMulticsUnit(pyxx.units.UnitLinear):
    """Class for representing units with linear transformations to/from
    the base units, customized to the Maha Multics software

    Defines a unit in which the transformations to/from the base units
    of the system of units (that is, the functions given by
    :py:attr:`from_base_function` and :py:attr:`to_base_function`) are linear.
    A large portion of the units encountered in everyday use can be considered
    linear units, so this class was created to simplify defining such units.

    Notes
    -----
    To convert an array of arbitrary dimensions ``inputs`` from the given
    object's unit to the base units, the following equation is applied:

    .. code-block:: python

        outputs = (scale * inputs) + offset
    """

    def __init__(self,
                 base_unit_exps:
                     Union[List[float], Tuple[float, ...], np.ndarray],
                 scale: float, offset: float,
                 identifier: Optional[str] = None, name: Optional[str] = None
                 ) -> None:
        """Creates an instance of the :py:class:`MahaMulticsUnit` class

        Defines an object representing a base or derived unit in which the
        functions converting a value to/from the base units of the system
        of units :py:attr:`unit_system` are linear functions and the system
        of units is specific to the Maha Multics software.

        Parameters
        ----------
        base_unit_exps : list or tuple or np.ndarray
            A 1D list of exponents relating the given object's unit to the
            base units of ``unit system``
        scale : float
            The multiplicative factor applied when converting from
            the given object's unit to the base units
        offset : float
            The constant value added when converting from the given
            object's unit to the base units
        identifier : str, optional
            A short identifier describing the unit (example: ``'kg'``)
            (default is ``None``)
        name : str, optional
            A name describing the unit (example: ``'kilogram'``) (default
            is ``None``)
        """
        super().__init__(
            unit_system    = MahaMulticsUnitSystem(),
            base_unit_exps = base_unit_exps,
            scale          = scale,
            offset         = offset,
            identifier     = identifier,
            name           = name
        )


_MAHA_MULTICS_DEFAULT_UNITS: Dict[str, Dict[str, Any]] = {
    ## BASE UNITS ------------------------------------------------------------
    'kg': {
        'unit': MahaMulticsUnit((1, 0, 0, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('mass',),
        'name': 'kilogram',
        'description': 'Unit of measure of mass',
        'aliases': ('kilogram', 'kilograms'),
    },
    'm': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('length',),
        'name': 'meter',
        'aliases': ('meter', 'meters'),
    },
    's': {
        'unit': MahaMulticsUnit((0, 0, 1, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('time',),
        'name': 'second',
        'aliases': ('sec', 'second', 'seconds'),
    },
    'K': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=1, offset=0),
        'tags': ('temperature',),
        'name': 'Kelvin',
    },
    'mol': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 1, 0, 0), scale=1, offset=0),
        'name': 'mole',
        'aliases': ('moles', 'mole'),
    },
    'A': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 1, 0), scale=1, offset=0),
        'name': 'ampere',
        'description': 'Unit of measure of electric current',
        'aliases': ('amp', 'amps'),
    },
    'cd': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 1), scale=1, offset=0),
        'tags': ('luminance',),
        'name': 'candela',
    },

    ## DIMENSIONLESS QUANTITIES ----------------------------------------------
    'dimensionless': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('dimensionless',),
        'name': 'dimensionless',
        'description': 'Unit assigned to dimensionless numbers',
        'aliases': ('-', 'unitless', 'null',),
    },

    ## PERCENTAGES -----------------------------------------------------------
    '%': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 0), scale=0.01, offset=0),
        'tags': ('percentage',),
        'name': 'percentage',
    },

    ## ANGLES ----------------------------------------------------------------
    'rad': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('angle',),
        'name': 'radian',
        'aliases': ('radian', 'radians'),
    },
    'deg': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 0), scale=math.pi/180,
                                offset=0),
        'tags': ('angle',),
        'name': 'degrees',
        'aliases': ('degree', 'degrees'),
    },
    'rev': {
        'unit': MahaMulticsUnit((0, 0, 0, 0, 0, 0, 0), scale=2*math.pi,
                                offset=0),
        'tags': ('angle',),
        'name': 'revolutions',
    },

    ## LENGTH ----------------------------------------------------------------
    'mm': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=0.001, offset=0),
        'tags': ('length',),
        'name': 'millimeter',
        'aliases': ('millimeter', 'millimeters'),
    },
    'cm': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=0.01, offset=0),
        'tags': ('length',),
        'name': 'centimeter',
        'aliases': ('centimeter', 'centimeters'),
    },
    'micron': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=1e-6, offset=0),
        'tags': ('length',),
        'name': 'micron',
        'aliases': ('microns',),
    },
    'in': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=_IN_TO_M_SCALE,
                                offset=0),
        'tags': ('length',),
        'name': 'inch',
        'aliases': ('inch', 'inches'),
    },
    'ft': {
        'unit': MahaMulticsUnit((0, 1, 0, 0, 0, 0, 0), scale=0.3048, offset=0),
        'tags': ('length',),
        'name': 'foot',
        'aliases': ('foot', 'feet'),
    },

    ## VOLUME ----------------------------------------------------------------
    'L': {
        'unit': MahaMulticsUnit((0, 3, 0, 0, 0, 0, 0), scale=0.001, offset=0),
        'tags': ('volume',),
        'name': 'liter',
        'aliases': ('liter', 'liters'),
    },

    ## MASS ------------------------------------------------------------------
    'g': {
        'unit': MahaMulticsUnit((1, 0, 0, 0, 0, 0, 0), scale=0.001, offset=0),
        'tags': ('mass',),
        'name': 'gram',
        'aliases': ('gram', 'grams'),
    },
    'lbm': {
        'unit': MahaMulticsUnit((1, 0, 0, 0, 0, 0, 0), scale=_LBM_TO_KG_SCALE,
                                offset=0),
        'tags': ('mass',),
        'name': 'pound-mass',
        'description': 'Avoirdupois pound-mass',
    },

    ## FORCE -----------------------------------------------------------------
    'N': {
        'unit': MahaMulticsUnit((1, 1, -2, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('force',),
        'name': 'Newtons',
        'aliases': ('Newton', 'Newtons'),
    },
    'kN': {
        'unit': MahaMulticsUnit((1, 1, -2, 0, 0, 0, 0), scale=1000, offset=0),
        'tags': ('force',),
        'name': 'kilonewtons',
        'aliases': ('kilonewton', 'kilonewtons'),
    },
    'lbf': {
        'unit': MahaMulticsUnit((1, 1, -2, 0, 0, 0, 0), scale=_LBF_TO_N_SCALE,
                                offset=0),
        'tags': ('force',),
        'name': 'pound-force',
        'description': 'Avoirdupois pound-force',
    },

    ## PRESSURE --------------------------------------------------------------
    'Pa_a': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('pressure',),
        'name': 'pascal-absolute',
        'description': 'Absolute pressure in units of pascals',
    },
    'Pa': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1,
                                offset=ATMOSPHERIC_PRESSURE_PA),
        'tags': ('pressure',),
        'name': 'pascal-gauge',
        'description': 'Gauge pressure in units of pascals',
    },
    'MPa_a': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1e6, offset=0),
        'tags': ('pressure',),
        'name': 'megapascal-absolute',
        'description': 'Absolute pressure in units of megapascals',
    },
    'GPa_a': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1e9, offset=0),
        'tags': ('pressure',),
        'name': 'gigapascal-absolute',
        'description': 'Absolute pressure in units of gigapascals',
    },
    'bar_a': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1e5, offset=0),
        'tags': ('pressure',),
        'name': 'bar-absolute',
        'description': 'Absolute pressure in units of bar',
    },
    'bar': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=1e5,
                                offset=ATMOSPHERIC_PRESSURE_PA),
        'tags': ('pressure',),
        'name': 'bar-gauge',
        'description': 'Gauge pressure in units of bar',
    },
    'psi_a': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=_PSI_TO_PA_SCALE,
                                offset=0),
        'tags': ('pressure',),
        'name': 'psi-absolute',
        'description': 'Absolute pressure in units of pounds per square inch',
    },
    'psi': {
        'unit': MahaMulticsUnit((1, -1, -2, 0, 0, 0, 0), scale=_PSI_TO_PA_SCALE,
                                offset=ATMOSPHERIC_PRESSURE_PA),
        'tags': ('pressure',),
        'name': 'psi-gauge',
        'description': 'Gauge pressure in units of pounds per square inch',
    },

    ## TEMPERATURE -----------------------------------------------------------
    'degC': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=1,
                                offset=_DEG_C_TO_K_OFFSET),
        'tags': ('temperature',),
        'name': 'degrees-Celsius',
        'description': 'Degrees Celsius',
    },
    'degF': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=_DEG_F_TO_K_SCALE,
                                offset=_DEG_F_TO_K_OFFSET),
        'tags': ('temperature',),
        'name': 'degrees-Fahrenheit',
        'description': 'Degrees Fahrenheit',
    },
    'degR': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=_DEG_F_TO_K_SCALE,
                                offset=0),
        'tags': ('temperature',),
        'name': 'degrees-Rankine',
        'description': 'Degrees Rankine',
    },
    'degC_diff': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=1, offset=0),
        'tags': ('temperature',),
        'name': 'degrees-Celsius-change',
        'description': 'Change in temperature in degrees Celsius',
    },
    'degF_diff': {
        'unit': MahaMulticsUnit((0, 0, 0, 1, 0, 0, 0), scale=_DEG_F_TO_K_SCALE,
                                offset=0),
        'tags': ('temperature',),
        'name': 'degrees-Fahrenheit-change',
        'description': 'Change in temperature in degrees Fahrenheit',
    },

    # ABSOLUTE/DYNAMIC VISCOSITY ---------------------------------------------
    'cP': {
        'unit': MahaMulticsUnit((1, -1, -1, 0, 0, 0, 0), scale=0.001, offset=0),
        'tags': ('viscosity',),
        'name': 'centipoise',
        'description': 'Measure of absolute/dynamic viscosity',
    },

    # KINEMATIC VISCOSITY ----------------------------------------------------
    'St': {
        'unit': MahaMulticsUnit((0, 2, -1, 0, 0, 0, 0), scale=1e-4, offset=0),
        'tags': ('viscosity',),
        'name': 'stoke',
        'description': 'Measure of kinematic viscosity',
    },
    'cSt': {
        'unit': MahaMulticsUnit((0, 2, -1, 0, 0, 0, 0), scale=1e-6, offset=0),
        'tags': ('viscosity',),
        'name': 'centistoke',
        'description': 'Measure of kinematic viscosity',
    },

    # WORK/ENERGY ------------------------------------------------------------
    'J': {
        'unit': MahaMulticsUnit((1, 2, -2, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('work', 'energy',),
        'name': 'joule',
        'aliases': ('joule', 'joules'),
    },
    'kJ': {
        'unit': MahaMulticsUnit((1, 2, -2, 0, 0, 0, 0), scale=1000, offset=0),
        'tags': ('work', 'energy',),
        'name': 'kilojoule',
        'aliases': ('kilojoule', 'kilojoules'),
    },

    # POWER ------------------------------------------------------------------
    'W': {
        'unit': MahaMulticsUnit((1, 2, -3, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('power',),
        'name': 'watt',
        'aliases': ('watt', 'watts'),
    },
    'kW': {
        'unit': MahaMulticsUnit((1, 2, -3, 0, 0, 0, 0), scale=1000, offset=0),
        'tags': ('power',),
        'name': 'kilowatt',
        'aliases': ('kilowatt', 'kilowatts'),
    },

    ## TIME ------------------------------------------------------------------
    'ms': {
        'unit': MahaMulticsUnit((0, 0, 1, 0, 0, 0, 0), scale=0.001, offset=0),
        'tags': ('time',),
        'name': 'millisecond',
        'aliases': ('millisecond', 'milliseconds'),
    },
    'min': {
        'unit': MahaMulticsUnit((0, 0, 1, 0, 0, 0, 0), scale=60, offset=0),
        'tags': ('time',),
        'name': 'minute',
        'aliases': ('minute', 'minutes'),
    },
    'hr': {
        'unit': MahaMulticsUnit((0, 0, 1, 0, 0, 0, 0), scale=3600, offset=0),
        'tags': ('time',),
        'name': 'hour',
        'aliases': ('hour', 'hours'),
    },

    ## FREQUENCY -------------------------------------------------------------
    'Hz': {
        'unit': MahaMulticsUnit((0, 0, -1, 0, 0, 0, 0), scale=1, offset=0),
        'tags': ('frequency',),
        'name': 'hertz',
        'aliases': ('hertz',),
    },
    'kHz': {
        'unit': MahaMulticsUnit((0, 0, -1, 0, 0, 0, 0), scale=1e3, offset=0),
        'tags': ('frequency',),
        'name': 'kilohertz',
        'aliases': ('kilohertz',),
    },
    'MHz': {
        'unit': MahaMulticsUnit((0, 0, -1, 0, 0, 0, 0), scale=1e6, offset=0),
        'tags': ('frequency',),
        'name': 'megahertz',
        'aliases': ('megahertz',),
    },
    'GHz': {
        'unit': MahaMulticsUnit((0, 0, -1, 0, 0, 0, 0), scale=1e9, offset=0),
        'tags': ('frequency',),
        'name': 'gigahertz',
        'aliases': ('gigahertz',),
    },
}


class MahaMulticsUnitConverter(pyxx.units.UnitConverter):
    """A unit converter using the SI system of units, pre-filled with
    common units

    This class is identical in function to a :py:class:`UnitConveter`, with
    the exception that it has been initialized with a number of commonly-used
    units.  All units in a :py:class:`UnitConveterSI` are defined in terms of
    the SI system (https://www.nist.gov/pml/owm/metric-si/si-units), with the
    following sequence of seven base units (used in the
    :py:attr:`Unit.base_unit_exps` attribute of all units in the unit
    converter):

    1. Mass: kilogram [:math:`kg`]
    2. Length: meter [:math:`m`]
    3. Time: second [:math:`s`]
    4. Temperature: Kelvin [:math:`K`]
    5. Amount of substance: mole [:math:`mol`]
    6. Electric current: ampere [:math:`A`]
    7. Luminous intensity: candela [:math:`cd`]

    For a list of units available by default, please refer to the
    :ref:`section-unitconverter_units` page.
    """

    def __init__(self):
        """Creates a new unit converter using the SI system of units and
        populated with commonly-used units.

        Creates an new :py:class:`UnitConverterSI` instance.  This unit
        converter uses the SI system (specifically, the system of units
        referenced by :py:class:`UnitSystemSI`) and is pre-filled with a
        set of commonly-used units.
        """
        super().__init__(unit_system=MahaMulticsUnitSystem())

        for key, unit_data in _MAHA_MULTICS_DEFAULT_UNITS.items():
            self.add_unit(key=key, **unit_data)
