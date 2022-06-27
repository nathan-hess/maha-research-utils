"""
This module contains functions for processing and analyzing variables.
"""

from typing import Any


def convert_to_tuple(value: Any):
    """Convert an input to a tuple

    Convert any input to a one-element tuple, or directly return
    the input (if it is already a tuple)

    Parameters
    ----------
    value : Any
        Value to convert to a tuple

    Returns
    -------
    tuple
        Directly returns ``value`` if it is already a tuple; otherwise,
        a one-element tuple containing ``value`` is returned

    Notes
    -----
    This function is intended to address an issue in which a value
    such as ``('value')`` is not considered a tuple (in this case,
    it would be a string), which may be unintuitive to users since
    it is in parentheses.  This function addresses this issue by
    converting any input to a tuple
    """
    if not isinstance(value, tuple):
        return (value,)
    return value
