"""Customized exceptions for the :py:mod:`mahautils.multics` module
"""

# GENERAL EXCEPTIONS
class MahaMulticsFileFormatError(Exception):
    """General exception for errors related to Maha Multics file parsers"""

class FileNotParsedError(MahaMulticsFileFormatError):
    """Error thrown when attempting to retrieve information from a file, but
    before the file has been read or contents populated"""


# SIMULATION RESULTS FILES
class SimResultsError(MahaMulticsFileFormatError):
    """General exception for errors related to Maha Multics simulation results
    files"""

class InvalidSimResultsFormatError(SimResultsError):
    """Maha Multics simulation results file content does not match expected
    format"""

class SimResultsKeyError(SimResultsError, KeyError):
    """Attempting to access a given variable in a simulation results file, but
    the variable is not present in the file"""

class SimResultsDataNotFoundError(SimResultsError, ValueError):
    """Error thrown if attempting to access data in a simulation results file
    that has not yet been defined"""

class SimResultsOverwriteError(SimResultsError):
    """Error thrown if overwriting data in a simulation results file that
    should not be overwritten"""


# VTK FILES
class VTKFormatError(MahaMulticsFileFormatError):
    """Error thrown if VTK file contains data in an unexpected format"""

class VTKIdentifierNameError(VTKFormatError, ValueError):
    """Error thrown if VTK file data identifier name has an invalid format"""

class VTKInvalidIdentifierError(IndexError):
    """Error thrown if attempting to retrieve data from a VTK file, but the
    identifier provided by the user does not correspond to a single column
    in the VTK data DataFrame"""
