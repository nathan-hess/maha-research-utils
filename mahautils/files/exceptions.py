class InvalidFileFormat(Exception):
    """File format does not match expected format"""


class VarExists(KeyError):
    """Maha Multics input dictionary variable already exists"""


class VarDoesNotExist(KeyError):
    """Maha Multics input dictionary variable does not exist"""


class VTKFormatError(Exception):
    """VTK file does not have expected data format"""
