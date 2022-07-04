"""
This module contains functions for processing and analyzing strings.
"""


def strip_parentheses(value: str, max_pairs: int = 0, strip: bool = True,
                      return_num_pairs_removed: bool = False):
    """Remove matched leading/trailing parentheses from strings

    Removes matched parentheses from a string (i.e., if a string begins with
    ``(`` and ends with ``)``, the parentheses are removed), as well as an
    any leading and/or trailing whitespace. Users can optionally disable
    whitespace removal.  Note that if ``strip`` is set to ``False``, then
    matched parentheses are removed if and only if the first character in
    ``value`` is ``(`` and the last character is ``)``.

    Parameters
    ----------
    value : str
        String from which to remove matched parentheses and leading/trailing
        whitespace (if ``strip`` is ``True``)
    max_pairs : int, optional
        Maximum pairs of matched parentheses to remove.  Set to ``0`` to
        remove an unlimited number of matched parentheses (default is ``0``)
    strip : bool, optional
        Whether to remove leading and/or trailing whitespace when processing
        ``value`` (default is ``True``)
    return_num_pairs_removed : bool, optional
        Whether to return the number of pairs of parentheses that were removed
        (default is ``False``)

    Returns
    -------
    str
        Input string ``value`` with matched parentheses removed
    int
        The number of pairs of matched parentheses that were removed (returned
        if and only if ``return_num_pairs_removed`` is ``True``)
    """
    value = value.strip() if strip else value

    num_removed = 0
    while (value.startswith('(') and value.endswith(')')):
        value = value[1:-1]
        num_removed += 1

        value = value.strip() if strip else value

        if num_removed >= max_pairs > 0:
            break

    if not return_num_pairs_removed:
        return value

    return value, num_removed
