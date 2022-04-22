##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Custom package and module imports
from multics.utils.vartools import check_list_types, check_numeric_list_equal
from .dictionary import Dictionary
from .exceptions import IncompatibleUnits


##############################################################################
# --- CONSTANTS ------------------------------------------------------------ #
##############################################################################
BASE_UNITS = {
    'MKS': ['kg', 'm', 's', 'K', 'mol', 'A', 'cd'],
}


##############################################################################
# --- UNIT DICTIONARY ------------------------------------------------------ #
##############################################################################
class UnitDict(Dictionary):
    class Unit:
        def __init__(self, base_exps: list, m: float, b: float):
            # Validate inputs
            if not check_list_types(base_exps, (int, float), all):
                raise TypeError('All elements of "base_exps" must be '
                                'of type "int" or "float"')
            
            if not isinstance(m, (int, float)):
                raise TypeError('Input "m" must be of type "int" or "float"')
            
            if not isinstance(b, (int, float)):
                raise TypeError('Input "b" must be of type "int" or "float"')
            
            # Store inputs
            self.base_exps = base_exps
            self.m = m
            self.b = b

        def __str__(self) -> str:
            return f'{{{self.base_exps}; {self.m}*x + {self.b}}}'

        def to_base(self, x: float):
            """Convert a quantity to the base unit system

            Converts a value from the class's unit to the base system
            of units

            Parameters
            ----------
            x : float
                The value to convert to the base unit system
            """
            if not isinstance(x, (int, float)):
                raise TypeError('Input "x" must be of type "int" or "float"')

            return self.m * x + self.b
        
        def from_base(self, x: float):
            """Convert a quantity to the class's units from base unit system

            Converts a value to the class's unit from the base system
            of units

            Parameters
            ----------
            x : float
                The value to convert to the class's unit
            """
            if not isinstance(x, (int, float)):
                raise TypeError('Input "x" must be of type "int" or "float"')

            return (x - self.b) / self.m

    def __init__(self, base_unit_names: list):
        super().__init__()

        # Validate inputs
        if not isinstance(base_unit_names, list):
            raise TypeError('Input "base_unit_names" must be a list')
        
        if not check_list_types(base_unit_names, str, all):
            raise TypeError('All elements of "base_unit_names" '
                            'must be of type "str"')
        
        # Store inputs
        self.base_unit_names = base_unit_names
        self._num_base_units = len(base_unit_names)
    
    def add_unit(self, unit: str, base_exps: list, m: float, b: float):
        """Adds a unit to the unit dictionary

        Stores a unit with a known relationship to the base units
        in the unit dictionary

        Parameters
        ----------
        unit : str
            Name or abbreviation of the unit to store
        base_exps : list
            List containing the powers to which each base unit should be
            raised to match the units of the input argument unit
        m : float
            Value by which to multiply values in the input unit by to
            obtain a value in the base units
        b : float
            Value to add (after multiplying by ``m``) to values in the
            input unit to obtain a value in the base units
        """
        # Validate inputs
        if not isinstance(unit, str):
            raise TypeError('Input "unit" must be a string')
        
        if (len(base_exps) != self._num_base_units):
            raise ValueError(f'Length of "base_exps" must '
                             f'be {self._num_base_units}')
        
        # Check whether unit is already defined
        if unit in self._contents:
            raise ValueError(f'Unit "{unit}" has already been defined')

        self._contents[unit] = self.Unit(base_exps, m, b)

    def check_unit_defined(self, units, throw_error: bool = False):
        '''Checks whether unit is defined in unit dictionary'''
        if isinstance(units, str):
            units = (units,)
        for unit in units:
            if unit not in self._contents:
                if throw_error:
                    raise KeyError(f'Unit "{unit}" is not defined')
                return False
        return True

    def check_compatible_types(self, unit1: str, unit2: str,
                               throw_error: bool = False):
        """Checks whether a unit can be converted to another unit
        
        Checks whether units are compatible (are composed)
        """
        list_eq = check_numeric_list_equal(
            list1=self._contents[unit1].base_exps,
            list2=self._contents[unit2].base_exps,
            throw_error=False
        )
        
        if not list_eq:
            if throw_error:
                raise IncompatibleUnits(f'Units "{unit1}" and "{unit2}" '
                                        f'are not compatible')
            else:
                return False
        
        return True

    def convert_unit(self, x: float, from_unit: str, to_unit: str):
        '''Converts a value from one unit to another'''
        if not isinstance(x, (int, float)):
            raise TypeError('Input "x" must be of type "int" or "float"')
        
        for unit in [from_unit, to_unit]:
            self.check_unit_defined(unit, throw_error=True)

        self.check_compatible_types(from_unit, to_unit, throw_error=True)
        
        x_base = self._contents[from_unit].to_base(x)
        return self._contents[to_unit].from_base(x_base)
