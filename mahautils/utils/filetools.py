"""
This module contains functions for processing and analyzing files.
"""

import hashlib
import pathlib
from typing import Union


def compute_file_hash(file: Union[str, pathlib.Path],
                      hash_function: str = 'sha256'):
    """Computes a file hash

    Computes and returns the hash of a file on the disk. Users can select
    the hash function from those supported by ``hashlib``

    Parameters
    ----------
    file : str or pathlib.Path
        File whose hash is to be computed
    hash_function : str, optional
        Hash function, selected from the options described in the
        "Notes" section (default is ``'sha256'``)

    Returns
    -------
    str
        Name of hash function (in the format used by ``hashlib``) which
        was computed
    str
        Hash of ``file`` as computed by the hash function specified
        by ``hash_function``

    Notes
    -----
    Any hash function included in Python's ``hashlib`` module can be used,
    as described here: https://docs.python.org/3/library/hashlib.html.

    Inputs for the ``hash_function`` argument are not case-sensitive, and
    dashes (``-``) and underscores (``_``) can be used interchangeably, or
    omitted.  Thus, to use the SHA-256 hash function, any of the following
    are valid inputs: ``'256256'``, ``'SHA-256'``, ``'sha_256'``.
    """
    # Set hash function
    hash_name = hash_function.lower().replace('-', '').replace('_', '')
    file_hash_function = getattr(hashlib, hash_name)

    # Compute file hash
    file_hash: hashlib._Hash = file_hash_function()
    with open(file, 'rb') as fileID:
        while block := fileID.read(file_hash.block_size):
            file_hash.update(block)

    return (hash_name, file_hash.hexdigest())
