"""
This module provides a customized dictionary which can be used to store
data in a key-value format.
"""

from typing import Optional

from mahautils.utils.vartools import max_list_item_len


class Dictionary(dict):
    """Python dictionary with project-specific customizations

    This class is a modified version of Python's built-in dictionaries.  Most
    typical dictionary methods function as they do in a ``dict`` object, with
    the exception of some customizations such as altering how the dictionary
    is converted to a string

    Attributes
    ----------
    str_indent : int
        The number of spaces of indentation at the beginning of each line
        when converting a ``Dictionary`` object to a string
    str_pad_left : int
        The number of spaces between the printed key and the separator when
        converting a ``Dictionary`` object to a string
    str_pad_right : int
        The number of spaces between the separator and printed value when
        converting a ``Dictionary`` object to a string
    """

    def __init__(self, contents: Optional[dict] = None, str_indent: int = 0,
                 str_pad_left: int = 1, str_pad_right: int = 2):
        """Defines a ``Dictionary`` instance

        Defines a new ``Dictionary`` object, providing options to populate
        the dictionary's contents and define parameters controlling how the
        dictionary is formatted when converting to a string

        Parameters
        ----------
        contents : dict, optional
            Python ``dict`` which, if provided, will immediately populate the
            data in the dictionary upon creation (default is ``None``)
        str_indent : int, optional
            Sets the dictionary's ``str_indent`` attribute (default is ``0``)
        str_pad_left : int, optional
            Sets the dictionary's ``str_pad_left`` attribute (default
            is ``0``)
        str_pad_right : int, optional
            Sets the dictionary's ``str_pad_right`` attribute (default
            is ``0``)
        """
        super().__init__()

        # Store parameters for representing dictionary as string
        self.str_indent = str_indent
        self.str_pad_left = str_pad_left
        self.str_pad_right = str_pad_right

        # Store dictionary contents if provided
        if contents is not None:
            self.update(contents)

    def __repr__(self):
        return str(self)

    def __str__(self):
        # Determine maximum string length of keys in dictionary
        _max_key_len = max_list_item_len(self.keys())

        # Create dictionary string representation
        representation = '\n'.join(
            [(f'{" "*self.str_indent}{key:{_max_key_len+self.str_pad_left}s}'
              f':{" "*self.str_pad_right}{value}')
             for key, value in self.items()])

        return representation
