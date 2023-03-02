"""Constants shared throughout the MahaUtils SimViewer GUI.
"""

# Importing the package version is a cylic import, but because the
# `__version__` variable is defined at the beginning of
# `mahautils/__init__.py`, it is cached and cyclic import does not
# cause problems
from mahautils import __version__ as VERSION  # pylint: disable=R0401  # noqa: F401

PROJECT_NAME = 'MahaUtils'
GUI_LONG_NAME = 'Simulation Results Viewer'
GUI_SHORT_NAME = 'SimViewer'

REPO_URL = 'https://github.com/nathan-hess/maha-research-utils'
