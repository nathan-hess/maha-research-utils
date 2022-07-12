"""
This module contains functions for parsing strings containing units and
providing a dictionary of each unit contained in the string and the exponent
to which the unit is raised.  For instance, the unit ``'kg*m/s^2'`` should
be converted to the format: ``{'kg': 1.0, 's': -2.0, 'm': 1.0}``.
"""

import copy
import string

from mahautils.utils.parentheses import (
    check_matched_parentheses,
    find_skip_parentheses,
    strip_parentheses,
)
from mahautils.utils.stringtools import (
    str_excludes_chars,
    split_at_index,
)
from .exceptions import (
    InvalidUnitError,
    InvalidExponentError,
    ParserMaxIterationError,
)


def _add_to_dict(dictionary: dict, unit: str, exponent: float):
    """Supporting function for ``parse_unit()`` that adds a unit
    to the output dictionary

    Used by ``parse_unit()`` to add a unit to the output dictionary,
    combining units with the same key by adding exponents (since these
    units are multiplied, so they can be described equivalently by a unit
    with the sum of their exponents)

    Parameters
    ----------
    dictionary : dict
        Output dictionary to which to add units
    unit : str
        Key of unit to add to ``dictionary``
    exponent : float
        Exponent corresponding to ``key``
    """
    if unit in dictionary:
        dictionary[unit] += exponent
    else:
        dictionary[unit] = exponent


def _check_dict_keys(dictionary: dict, special_chars: str):
    """Verifies that all keys a dictionary have do not have certain characters

    Checks each key in a given input dictionary to see whether it contains
    prohibited characters and returns the result.  This is useful when parsing
    unit strings, since iterating until this function returns ``True`` ensures
    that all compound units have been simplified

    Parameters
    ----------
    dictionary : dict
        Dictionary whose keys are to be analyzed
    special_chars : str
        Characters which, if found in any dictionary keys, should result in
        the function returning ``False``

    Returns
    -------
    bool
        Returns ``True`` if none of the characters in ``special_chars`` are
        found in the keys of ``dictionary`` and ``False`` otherwise
    """
    for key in dictionary.keys():
        if not(_is_unit(key, special_chars)):
            return False

    return True


def _is_unit(value: str, special_chars: str):
    """Checks whether a string is a fully-simplified unit with no compound
    unit operators

    Checks whether a string is a fully-simplified unit by analyzing whether
    it contains any user-specified special characters (such as ``*`` or ``^``)
    that are used to form compound units.  If these characters are found, the
    string is determined to not be a unit

    Parameters
    ----------
    value : str
        String to analyze
    special_chars : str
        Characters which, if found in ``value``, indicate that ``value``
        is a compound unit

    Returns
    -------
    bool
        Returns ``True`` if ``value`` does not contain any characters in
        ``special_chars``, and ``False`` otherwise
    """
    return str_excludes_chars(value, special_chars)


def parse_unit(unit: str, max_iterations: int = 10000):
    """Parses a string of simple or compound units, separating it into
    fully-simplified compoent units

    Iteratively parses a string containing a set of multiplied and/or
    divided units, identifying each fully-simplified component unit and the
    power to which it is raised, and returning these data in a dictionary.
    For instance, the unit ``'kg*m/s^2'`` should be parsed and result in
    the dictionary: ``{'kg': 1.0, 's': -2.0, 'm': 1.0}``.  Standard order
    of operations are followed when parsing units (parentheses evaluated
    first, followed by exponents, then multiplication and division)

    Parameters
    ----------
    unit : str
        String containing a simple or compound unit to parse
    max_iterations : int, optional
        Iteration limit for iteratively parsing the unit (default is 10000)

    Returns
    -------
    dict
        Returns a Python dictionary.  Each key represents a fully-simplified
        component unit parsed from ``unit``, and the corresponding value is
        the exponent to which the unit is raised in ``unit`` (i.e., the
        product of all keys raised to their corresponding values is equivalent
        to the original unit string ``unit``)

    Warnings
    --------
    When parsing units, the following are considered "special characters" that
    are not allowed to be used in fully-simplified units: ``0123456789.*/^()``

    A unit is considered fully-simplified if it does not contain any of these
    special characters.  **Attempting to include any of these characters in
    the simple component units may result in the compound unit being
    impossible to parse, or other unexpected behavior**
    """
    # Store original unit string
    original_unit = unit

    # Special characters in units
    operator_chars = '*/^()'             # Used to construct compound units
    number_chars = string.digits + '.'   # Characters reserved for numbers
    special_chars = operator_chars + number_chars

    # Verify that input is a string
    if not isinstance(unit, str):
        raise TypeError('Argument "unit" must be of type "str"')

    # Verify that all parentheses in the input are matched
    if not check_matched_parentheses(unit):
        raise ValueError('Parentheses in argument "unit" are not all matched')

    # Replace Python exponent characters ** with ^
    unit = unit.replace('**', '^')

    # Remove whitespace
    unit = unit.replace(' ', '').replace('\t', '')

    # Initialize output data structure
    output = {} if unit == '' else {unit: 1.0}

    # Parse unit
    n = -1
    while not(success := _check_dict_keys(output, special_chars)) \
            and (((n := n + 1) < max_iterations) or (max_iterations < 0)):

        # Iterate through each key in dictionary and simplify it
        for unit_string in copy.deepcopy(output):

            # STEP 1) Remove key from output dictionary
            exponent = output.pop(unit_string)

            # If unit string is enclosed by matched parentheses, remove
            # them, as they are unnecessary
            unit_string = strip_parentheses(unit_string)

            # STEP 2) If unit is does not contain any special characters, then
            # it is already simplified as much as possible, so move to next key
            if _is_unit(unit_string, special_chars):
                _add_to_dict(output, unit_string, exponent)
                continue

            # STEP 3) Separate units that are multiplied together (e.g., N*m)
            #   Work forward through the string, eliminating any units that are
            #   multiplied by each other
            _continue = False
            while (i := find_skip_parentheses(unit_string, target_chars='*',
                            begin=0, direction='forward')) != -1:  # noqa: E128
                _continue = True

                # Throw error if unit begins with "*"
                if i == 0:
                    raise InvalidUnitError(
                        f'Invalid unit string "{unit_string}" encountered when '
                        f' parsing unit "{original_unit}" (unit strings '
                        'cannot begin with "*")')

                # Split `unit_string` at the "*" character
                x1, x2 = split_at_index(unit_string, i)

                # Store the first part of the split string, and repeat loop to
                # check whether there are any other multiplied units in the
                # second part of the split string
                _add_to_dict(output, strip_parentheses(x1), exponent)
                unit_string = strip_parentheses(x2)

            if _continue:
                _add_to_dict(output, strip_parentheses(unit_string), exponent)
                continue

            # STEP 4) Separate units that are divided (e.g., m/s)
            #   Work backward through the string, eliminating any units that are
            #   divided by each other
            while (i := find_skip_parentheses(unit_string, target_chars='/',
                            begin=-1, direction='reverse')) != -1:  # noqa: E128
                _continue = True

                # Throw error if unit ends with "/"
                if i == len(unit_string) - 1:
                    raise InvalidUnitError(
                        f'Invalid unit string "{unit_string}" encountered when '
                        f' parsing unit "{original_unit}" (unit strings '
                        'cannot end with "/")')

                # Split `unit_string` at the "/" character
                x1, x2 = split_at_index(unit_string, i)

                # Store the second part of the split string with a negative
                # exponent, and repeat loop to check whether there are any
                # other divided units in the first part of the split string
                _add_to_dict(output, strip_parentheses(x2), -exponent)
                unit_string = strip_parentheses(x1)

            if _continue:
                _add_to_dict(output, strip_parentheses(unit_string), exponent)
                continue

            # STEP 5) Simplify units that are raised to a power (e.g., m^2)
            if (i := find_skip_parentheses(unit_string, target_chars='^',
                         begin=-1, direction='reverse')) != -1:  # noqa: E128
                # Throw error if unit begins or ends with "^"
                if not(1 <= i  <= len(unit_string) - 2):
                    raise InvalidUnitError(
                        f'Invalid unit string "{unit_string}" encountered when '
                        f' parsing unit "{original_unit}" (unit strings '
                        'cannot begin or end with "^")')

                # Split unit string at last "^" character
                base, exp = split_at_index(unit_string, i)

                # Verify that exponent is a number
                try:
                    exp = float(strip_parentheses(exp))
                except (ValueError, TypeError):
                    raise InvalidExponentError(
                        f'Invalid exponent "{exp}" encountered when '
                        f' parsing unit "{original_unit}"')

                # Verify that base is either a unit or enclosed in
                # matched parentheses
                if not(_is_unit(base, special_chars)
                        or (base != strip_parentheses(base))):
                    raise InvalidUnitError(
                        f'Invalid base "{base}" encountered when parsing '
                        f'unit "{original_unit}" (base must either be a unit '
                        'or enclosed in parentheses')

                # Store unit
                _add_to_dict(output, strip_parentheses(base), exponent*exp)
                continue

            # STEP 6) Fallback step
            #   If none of the previous steps could simplify the unit,
            #   store it back inside the unit dictionary to be processed
            #   again on the next iteration
            _add_to_dict(output, unit_string, exponent)

    if not success:
        raise ParserMaxIterationError(
            f'Unable to parse unit string "{original_unit}" after '
            f'{max_iterations} iterations')

    # Remove any units with an exponent of zero
    output = {key: value for key, value in output.items() if value != 0}

    return output
