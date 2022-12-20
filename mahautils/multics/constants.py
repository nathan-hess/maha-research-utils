"""Constants used in the Maha Multics software and related input/output files
are defined in this module, so they can be used for unit conversions and other
computations in the :py:mod:`mahautils.multics` module.
"""

# Atmospheric pressure
ATMOSPHERIC_PRESSURE_PA = 101325    # Pa (absolute pressure)


# Standard acceleration due to gravity
# https://physics.nist.gov/cgi-bin/cuu/Value?gn
STANDARD_GRAVITY = 9.80665  # m/s^2


# Conversion factors
# Inches to meters
_IN_TO_M_SCALE = 0.0254  # m/in

# Pound-mass to kilograms
_LBM_TO_KG_SCALE = 0.45359237  # kg/lbm

# Pound-force to Newtons
_LBF_TO_N_SCALE = 4.4482216152605  # N/lbf

# Pounds per square inch (psi) to pascals (Pa)
_PSI_TO_PA_SCALE = (_LBM_TO_KG_SCALE * STANDARD_GRAVITY) \
    / (_IN_TO_M_SCALE**2)  # Pa/psi

# Degrees Celsius to Kelvin
_DEG_C_TO_K_OFFSET = 273.15

# Degrees Fahrenheit to Kelvin
_DEG_F_TO_K_SCALE = 5/9
_DEG_F_TO_K_OFFSET = -32 * _DEG_F_TO_K_SCALE + _DEG_C_TO_K_OFFSET
