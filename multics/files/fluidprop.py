##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import numpy as np

import scipy.interpolate

# Custom package and module imports
from multics.utils.vartools import to_np_1D_array
from .exceptions import InvalidFileFormat
from .files import Table


##############################################################################
# --- CONSTANTS ------------------------------------------------------------ #
##############################################################################
DEFAULT_FLUID_PROP_FILE_LAYOUT = [
  # ['p',      'pressure',                         'Pa'    ],
  # ['T',      'temperature',                      'K'     ],
    ['rho',    'density',                          'kg/m^3'],
    ['K',      'bulk modulus',                     'Pa'    ],
    ['nu',     'kinematic viscosity',              'm^2/s' ],
    ['cp',     'specific heat capacity',           'J/kg/K'],
    ['lambda', 'thermal conductivity',             'W/m/K' ],
    ['alpha',  'volumetric expansion coefficient', '1/K'   ],
    ['h',      'specific enthalpy',                'J/kg'  ],
]


##############################################################################
# --- FLUID PROPERTY FILE READER/WRITER ------------------------------------ #
##############################################################################
class FluidPropertyFile(Table):
    def __init__(self, properties: list = DEFAULT_FLUID_PROP_FILE_LAYOUT,
                 comment_char: str = '#'):
        super().__init__(comment_char)

        # Declare variables
        self._num_T: int = None
        self._step_T: float = None

        self._num_p: int = None
        self._step_p: float = None

        self._vals_T: np.ndarray = None
        self._vals_p: np.ndarray = None

        self._table: np.ndarray = None

        # Store inputs
        self._num_props = len(properties)
        self._prop_variables    = [i[0] for i in properties]
        self._prop_descriptions = [i[1] for i in properties]
        self._prop_units        = [i[2] for i in properties]

    @property
    def num_properties(self):
        return self._num_props

    @property
    def num_temperature(self):
        return self._num_T
    
    @property
    def num_pressure(self):
        return self._num_p
    
    @property
    def step_temperature(self):
        return self._step_T
    
    @property
    def step_pressure(self):
        return self._step_p

    @property
    def vals_temperature(self):
        return list(self._vals_T)

    @property
    def vals_pressure(self):
        return list(self._vals_p)

    def read(self, input_file: str, tol: float = 1e-8):
        # Read raw file data
        super().read(input_file)
        super()._clean_contents()
        
        # PARSE FILE CONTENTS
        # Get number of temperature values and temperature step
        self._num_T = int(float(self._contents[0]))
        self._step_T = float(self._contents[1])

        # Get number of pressure values and pressure step
        self._num_p = int(float(self._contents[2]))
        self._step_p = float(self._contents[3])

        # Get list of all temperature values
        self._vals_T = np.array([float(i) for i in self._contents[4].split()])
        self._vals_p = np.array([float(i) for i in self._contents[5].split()])

        # Check that file has expected number of lines
        _expected_lines = self._num_T*self._num_p
        if not(len(self._contents[6:]) == _expected_lines):
            raise InvalidFileFormat(f'Fluid property file does not have '
                                    f'stated number of lines '
                                    f'({_expected_lines})')

        # Check that temperature and pressure steps match listed values
        _max_diff = max((self._vals_T[1:] - self._vals_T[:-1]) - self._step_T)
        if _max_diff > tol:
            raise ValueError(f'Fluid property file temperature values do not '
                             f'have stated temperature step (maximum '
                             f'difference: {_max_diff})')

        _max_diff = max((self._vals_p[1:] - self._vals_p[:-1]) - self._step_p)
        if _max_diff > tol:
            raise ValueError(f'Fluid property file pressure values do not '
                             f'have stated pressure step (maximum '
                             f'difference: {_max_diff})')

        # Read fluid property data
        self._table = [[] for i in range(self._num_props + 2)]

        i = 6
        for _t in self._vals_T:
            for _p in self._vals_p:
                # Save temperature and pressure
                self._table[0].append(_p)
                self._table[1].append(_t)

                # Save fluid properties
                _line = [float(j) for j in self._contents[i].split()]

                if len(_line) != self._num_props:
                    raise InvalidFileFormat(
                        f'Line {i+1}: Expected {self._num_props} properties '
                        f'but received {len(_line)}'
                    )

                for j in range(self._num_props):
                    self._table[j+2].append(_line[j])

                # Increment line counter
                i += 1
        
        # Convert table to NumPy array
        self._table = np.array(self._table)

    def get(self, pressure, temperature, prop: str, 
            interpolator: str = 'griddata', **kwargs):
        # Convert inputs to NumPy arrays
        _vals_p = to_np_1D_array(pressure)
        _vals_T = to_np_1D_array(temperature)

        # Check that input array sizes are compatible
        if ((len(_vals_p) > 1) and (len(_vals_T) > 1) \
                and (len(_vals_p) != len(_vals_T))):
            raise ValueError('Pressure and temperature arrays have '
                             'incompatible lengths')

        # Ensure pressure and temperature arrays have the same size
        if ((len(_vals_p) > 1) and (len(_vals_T) == 1)):
            _vals_T = np.repeat(_vals_T, len(_vals_p))

        elif ((len(_vals_T) > 1) and (len(_vals_p) == 1)):
            _vals_p = np.repeat(_vals_p, len(_vals_T))
    
        # Determine property whose values are to be interpolated
        if isinstance(prop, int):
            _idx = prop
        else:
            try:
                _idx = self._prop_variables.index(prop)
            except ValueError:
                _idx = self._prop_descriptions.index(prop)

        # Extract property data
        _prop_data = self._table[_idx + 2]

        # Perform interpolation
        if (interpolator == 'griddata'):
            if not 'method' in kwargs:
                raise KeyError('If "griddata" is chosen as the interpolation '
                               'function, a keyword argument "method" must '
                               'be provided')
            
            return list(scipy.interpolate.griddata(
                np.stack((self._table[0], self._table[1]), axis=1),
                _prop_data,
                np.stack((_vals_p, _vals_T), axis=1),
                method=kwargs['method']
            ))
