"""
This module contains functions for processing and simplifying strings
containing parentheses.  It provides functionality for identifying whether
parentheses in a string form matched pairs (every opening parenthesis has
a corresponding closing parenthesis, in the correct order), among other
capabilities.
"""

from typing import Union

from .exceptions import UnmatchedParenthesesError


def check_matched_parentheses(value: str):
    """Checks whether all opening parentheses in a string have
    corresponding closing parentheses

    Parameters
    ----------
    value : str
        String to process

    Returns
    -------
    bool
        Returns ``True`` if for every opening parenthesis (``(``),
        there is a closing parenthesis (``)``) that occurs later in
        the string, and ``False`` otherwise
    """
    counter = 0
    for char in value:
        if char == '(':
            counter += 1
        elif char == ')':
            counter -= 1

        # If counter is negative, this indicates that `)` occurred
        # before the corresponding `(`
        if counter < 0:
            return False

    return counter == 0


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


def find_skip_parentheses(value: str, target_chars: Union[str, tuple],
                          begin: int, direction: str = 'forward'):
    """Finds the index of a target character, skipping over matched
    parentheses

    This function is useful for finding the index of a particular character
    in a string, ignoring content inside of matched parentheses.  It begins
    at a given index in a string and searches until any of a given set of
    target characters are found.  If an opening or closing parenthesis is
    reached, the function skips to the corresponding parentheses that
    completes the pair before resuming the search (i.e., content inside of
    matched parentheses is not searched)

    Parameters
    ----------
    value : str
        String to search
    target_chars : str or tuple
        A string or tuple with one or more characters to search for
    begin : int
        Index in ``value`` at which to begin searching
    direction : str, optional
        Whether to search ``value`` in order of increasing or decreasing
        index.  Can be either ``'forward'`` or ``'reverse'`` (default
        is ``'forward'``)

    Returns
    -------
    int
        The index of the first occurence of any characters in ``target_chars``
        found in ``value``, beginning the search at index ``begin`` and
        searching in the direction specified by ``direction`` and ignoring
        content inside of matched parentheses.  If none of ``target_chars``
        are found, ``-1`` is returned

    Notes
    -----
    When searching, the function will not "enter" matched parentheses;
    however, if the index specified by ``begin`` is inside a set of
    parentheses, the function will search inside of these parentheses and
    can "leave" these parentheses and search in parts of the string outside
    these parentheses
    """
    # Verify that "value" argument is a string
    if not isinstance(value, str):
        raise TypeError('Argument "value" must be of type "str"')

    # Verify that "begin" is a valid index for the given string
    if not(-len(value) <= begin <= len(value) - 1):
        raise IndexError(
            f'Index {begin} at which to begin search is not valid for '
            f'string "{value}" (length {len(value)})')

    # Adjust if user provides an index relative to the end of the string
    i = begin + len(value) if begin < 0 else begin

    # Set increment by which to advance to next character when
    # searching string
    if direction not in ('forward', 'reverse'):
        raise ValueError('Argument "direction" must be one of: '
                         '"forward" or "reverse"')

    k = 1 if direction == 'forward' else -1

    while 0 <= i < len(value):
        # Check whether target character has been found
        if value[i] in target_chars:
            return i

        # Check whether an opening or closing parenthesis has been
        # found; if so, move to the end of the matched pair
        if any(((direction == 'forward' and value[i] == '('),
                (direction == 'reverse' and value[i] == ')'))):
            if (i := find_matching_parenthesis(value, i)) == -1:
                raise UnmatchedParenthesesError(
                    f'Unmatched parentheses found in string "{value}"')

        # Advance to next character in string
        i += k

    return -1


def strip_parentheses(value: str, max_pairs: int = 0, strip: bool = True,
                      return_num_pairs_removed: bool = False):
    """Remove matched leading/trailing parentheses from strings

    Removes matched parentheses from a string (i.e., if a string begins with
    ``(`` and the corresponding closing parenthesis ``)`` is the last
    character in the string, the parentheses are removed), as well as an
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
        # Only remove leading and trailing parentheses if they form
        # a matching pair
        if find_matching_parenthesis(value, -1) == 0:
            value = value[1:-1].strip() if strip else value[1:-1]
            num_removed += 1
        else:
            break

        # If the maximum number of pairs of parentheses have been
        # removed, exit the loop
        if num_removed >= max_pairs > 0:
            break

    # Output results
    if not return_num_pairs_removed:
        return value

    return value, num_removed
