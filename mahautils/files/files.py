"""
Base class for processing files of any type (text or binary)
"""

import pathlib
from typing import Union

from mahautils.utils.filetools import compute_file_hash


class File:
    """Base class for processing files of any type (text or binary)

    Attributes
    ----------
    file : pathlib.Path
        File that the object represents
    hashes : dict
        Dictionary containing file hash(es), if they have been computed

    Methods
    -------
    compute_hashes(hash_functions=['md5', 'sha256'])
        Computes file hashes and populates the ``hashes`` dictionary
    """

    def __init__(self, file: Union[str, pathlib.Path]):
        """Define an arbitrary file

        Creates an object that represents and can be used to process a file of
        any type (text or binary)

        Parameters
        ----------
        file : str or pathlib.Path
            File that the object is to represent
        """
        # File path
        self._file = pathlib.Path(file).resolve()

        # File hashes
        self._hashes: dict = {}

    def __repr__(self):
        # Display class
        representation = f'{__class__}\n'

        # Display path and filename
        representation += f'--> File: {str(self._file)}\n'

        # Display file hashes
        if len(self._hashes) > 0:
            header = '--> File hash:' \
                if len(self._hashes) == 1 else '--> File hashes:'
            representation += self.__file_hash_str(header, 4)

        return representation[:-1]

    def __str__(self):
        return str(self._file)

    def __file_hash_str(self, header: str, indent: int = 0):
        file_hash_str = f'{header}\n'

        for i in self._hashes.items():
            file_hash_str += f'{" " * indent}{i[0]}: {i[1]}\n'

        return file_hash_str

    @property
    def file(self):
        """Returns the file path and filename"""
        return self._file

    @property
    def hashes(self):
        """Returns the file hashes"""
        return self._hashes

    def compute_file_hashes(self,
                            hash_functions: Union[tuple, str] = ('md5', 'sha256')):
        """Computes hashes of the file

        Computes the hashes of the file and populates the ``self.hashes``
        dictionary with their values

        Parameters
        ----------
        hash_functions : tuple or str
            Tuple of strings (or individual string) specifying which hash(es)
            to compute. Any hash functions supported by ``hashlib`` can be
            used. Default is ``('md5', 'sha256')``

        See Also
        --------
        mahautils.utils.filetools.compute_file_hash :
            Function used to compute file hashes
        """
        if not self.file.exists():
            raise FileNotFoundError(
                f'Cannot compute hash for non-existent file "{self.file}"'
            )

        if isinstance(hash_functions, str):
            hash_functions = (hash_functions,)

        # Compute file hash(es)
        for func in hash_functions:
            hash_name, file_hash = compute_file_hash(self.file, func)
            self._hashes[hash_name] = file_hash
