"""
This module contains functions for processing and analyzing strings.
"""


def find_matching_parenthesis(value: str, begin: int):
    """Finds the index of the parenthesis matching a parenthesis at
    a given index

    Finds the "other parenthesis" that forms a closed pair of matched
    parenthesis in a string ``value``, beginning from the parenthesis
    at index ``begin``. Note that if the character at index ``begin``
    is ``(``, then ``value`` is searched in the forward direction (left
    to right), while if it is ``)`` then the search direction is reversed
    (right to left).

    Parameters
    ----------
    value : str
        String to search for matching parenthesis
    begin : int
        Index in ``value`` where one of the parentheses in the matched
        pair is found

    Returns
    -------
    int
        Returns the index of the matching parenthesis, or ``-1`` if the
        parenthesis at index ``begin`` in ``value`` does not have a
        matching parenthesis in ``value``

    Raises
    ------
    ValueError
        If the character at index ``begin`` in ``value`` is not one of
        ``(`` or ``)``
    """
    # Adjust if user provides an index relative to the end of the string
    if begin < 0:
        begin += len(value)

    # Define search direction and ending index depending on whether the
    # `begin` index specifies and opening or closing parenthesis
    begin_char = value[begin]

    if begin_char == '(':
        k = 1
        end = len(value)
    elif begin_char == ')':
        k = -1
        end = -1
    else:
        raise ValueError(f'Character at index {begin} of "{value}" is '
                         f'"{begin_char}", which is not a parenthesis')

    # Search string to find the matching parenthesis
    counter = 0
    for i in range(begin, end, k):
        if value[i] == '(':
            counter += 1
        elif value[i] == ')':
            counter -= 1

        # The first time `counter` returns to zero, the matching
        # parenthesis has been found
        if counter == 0:
            return i

    return -1


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
