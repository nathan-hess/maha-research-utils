"""Constants shared throughout the MahaUtils SimViewer GUI.
"""

from typing import Dict

# Importing the package version is a cylic import, but because the
# `__version__` variable is defined at the beginning of
# `mahautils/__init__.py`, it is cached and cyclic import does not
# cause problems
from mahautils import __version__ as VERSION  # pylint: disable=R0401  # noqa: F401

from mahautils.multics.simresults import SimResults
from mahautils.utils.dictionary import Dictionary


# GENERAL PROJECT SETTINGS ---------------------------------------------------
PROJECT_NAME = 'MahaUtils'
GUI_LONG_NAME = 'Simulation Results Viewer'
GUI_SHORT_NAME = 'SimViewer'

REPO_URL = 'https://github.com/nathan-hess/maha-research-utils'


# TYPE ALIASES ---------------------------------------------------------------
# Type of global variable which stores simulation results files
SIM_RESULTS_FILE_T = Dictionary[str, Dict[str, SimResults]]


# STYLING --------------------------------------------------------------------
# Margin between tab bar and content in configuration panel
TAB_BAR_PADDING = '20px'
