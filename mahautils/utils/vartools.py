"""
This module contains functions for processing and analyzing variables.
"""

from typing import Any, Union


def check_len_equal(item1: Any, item2: Any, *args: Any):
    """Checks whether the lengths of a set of lists or tuples are equal

    Evaluates the lengths of a set of items (such as lists, tuples, or
    strings), returning whether all items have the same length as well as
    either the length of all items (if all lengths are equal) or a list
    containing the lengths of each item (if they are not equal)

    Parameters
    ----------
    item1 : Any
        First item whose length to evaluate
    item2 : Any
        Second item whose length to evaluate
    *args : Any, optional
        Any other items whose lengths are to be evaluated

    Returns
    -------
    bool
        Whether all items have the same length
    int or list
        Returns an integer containing the length of all items (if all
        lengths are equal), or a list containing the lengths of each
        item (if lengths differ)
    """
    lengths = [len(item1)] + [len(item2)] + [len(i) for i in args]

    if len(set(lengths)) == 1:
        return True, lengths[0]
    else:
        return False, lengths


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


def max_list_item_len(input_list: Union[list, tuple]):
    """Finds the maximum length of any item in a list or tuple

    Parameters
    ----------
    input_list : list or tuple
        Array of items to process

    Returns
    -------
    int
        Length of item in list with maximum length
    """
    return max(list(map(len, input_list)))
