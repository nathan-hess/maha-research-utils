"""Utilities for managing data stored in arrays.
"""

from typing import Any

import numpy as np


def to_np_1D_array(value: Any, dtype: Any = None,
                   flatten: bool = True) -> np.ndarray:
    """Converts an input to a 1D NumPy array

    This function converts data of any type into a 1D NumPy array.

    Parameters
    ----------
    value : Any
        The data to convert to a 1D NumPy array
    dtype : Any, optional
        The required data type for the items in the NumPy array to be returned
        (default is ``None``, which imposes no data type requirement).  Any
        valid data type accepted by the ``numpy.array()`` function can be
        provided
    flatten : bool, optional
        Whether to use NumPy's `flatten <https://numpy.org/doc/stable/reference
        /generated/numpy.ndarray.flatten.html>`__ function to convert ``value``
        to a 1D array in the event ``value`` has two or more dimensions
        (default is ``True``)

    Returns
    -------
    np.ndarray
        The data in ``value``, converted to a 1D NumPy array
    """
    np_array = np.array(value, dtype=dtype)

    if flatten:
        np_array = np_array.flatten()

    if np_array.ndim == 0:
        np_array = np.expand_dims(np_array, axis=0)

    if np_array.ndim != 1:
        raise ValueError('Input must be at most 1D, but given '
                         f'data are {np_array.ndim}D')

    return np_array
