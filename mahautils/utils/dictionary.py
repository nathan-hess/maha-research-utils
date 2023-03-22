"""This module provides a customized dictionary which can be used to store
data in a key-value format.
"""

from typing import List, Optional, OrderedDict, Tuple, Type, TypeVar, Union

from pyxx.arrays import max_list_item_len

K = TypeVar('K')
V = TypeVar('V')


class Dictionary(OrderedDict[K, V]):
    """Customized Python dictionary

    This class is a modified version of Python's built-in :py:class:`OrderedDict`
    dictionary.  Most typical dictionary methods function as they do in a
    :py:class:`dict`.  However, additional functionality has been added, such as
    being able to insert items at any position in the dictionary and
    customizations for printing content in the dictionary.
    """

    def __init__(self, contents: Optional[dict] = None,
                 required_key_type: Optional[
                     Union[Type[K], List[Type[K]], Tuple[Type[K], ...]]] = None,
                 required_value_type: Optional[
                     Union[Type[V], List[Type[V]], Tuple[Type[V], ...]]] = None,
                 multiline_print: bool = False,
                 str_indent: int = 0,
                 str_pad_left: int = 1, str_pad_right: int = 2,
                 custom_except_class: Type[Exception] = KeyError,
                 custom_except_msg: str = '%s',
                 ) -> None:
        """Defines a :py:class:`Dictionary` instance

        Defines a new :py:class:`Dictionary` object, providing options to
        populate the dictionary's contents and define parameters controlling
        how the dictionary is formatted when converting to a string.

        Parameters
        ----------
        contents : dict, optional
            Python ``dict`` which, if provided, will immediately populate the
            data in the dictionary upon creation (default is ``None``)
        required_key_type : type or list or tuple, optional
            One or more required type(s) of which all keys in the dictionary
            must be a subclass.  Set to ``None`` to allow any type (default is
            ``None``)
        required_value_type : type or list or tuple, optional
            One or more required type(s) of which all values in the dictionary
            must be a subclass.  Set to ``None`` to allow any type (default is
            ``None``)
        multiline_print : bool, optional
            Whether to print each entry of the dictionary on its own line when
            converting to a printable string representation (default is
            ``False``)
        str_indent : int, optional
            Sets the dictionary's :py:attr:`str_indent` attribute
            (default is ``0``).  Only applicable if ``multiline_print`` is
            ``True``
        str_pad_left : int, optional
            Sets the dictionary's :py:attr:`str_pad_left` attribute (default
            is ``0``).  Only applicable if ``multiline_print`` is ``True``
        str_pad_right : int, optional
            Sets the dictionary's :py:attr:`str_pad_right` attribute (default
            is ``0``).  Only applicable if ``multiline_print`` is ``True``
        custom_except_class : class, optional
            An :py:class:`Exception` subclass to raise if a given key is not
            found in the dictionary (default is :py:class:`KeyError`)
        custom_except_msg : str, optional
            Only applicable if ``custom_except_class`` is not ``None``.
            Specifies an error message to throw if a key is not found in the
            dictionary.  Must contain a single ``%s`` occurrence, which will
            be replaced by the name of the key which was not found (default
            is ``'%s'``)
        """
        super().__init__()

        # Store required key and value types
        self._required_key_type = required_key_type
        self._required_value_type = required_value_type

        # Store parameters for representing dictionary as string
        self.multiline_print = multiline_print
        self.str_indent = str_indent
        self.str_pad_left = str_pad_left
        self.str_pad_right = str_pad_right

        # Store customized exception information
        self.custom_except_class = custom_except_class
        self.custom_except_msg = custom_except_msg

        # Store dictionary contents if provided
        if contents is not None:
            self.update(contents)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise self.custom_except_class(  # pylint: disable=W0707
                self.custom_except_msg % key)

    def __repr__(self) -> str:
        if not self._multiline_print:
            return super().__repr__()

        return str(self)

    def __setitem__(self, key, value):
        if (
            self._required_key_type is not None
            and not isinstance(key, self._required_key_type)
        ):
            raise TypeError(
                'Dictionary keys must be of one of the following '
                f'types: {self._required_key_type}')

        if (
            self._required_value_type is not None
            and not isinstance(value, self._required_value_type)
        ):
            raise TypeError(
                'Dictionary values must be of one of the following '
                f'types: {self._required_value_type}')

        super().__setitem__(key, value)

    def __str__(self) -> str:
        if not self._multiline_print:
            return super().__str__()

        if len(self) > 0:
            # Determine maximum string length of keys in dictionary
            _max_key_len = max_list_item_len(self.keys())

            # Create dictionary string representation
            representation = '\n'.join(
                [(f'{" "*self.str_indent}{key:{_max_key_len+self.str_pad_left}s}'
                  f':{" "*self.str_pad_right}{value}')
                 for key, value in self.items()])
        else:
            representation = ''

        return representation

    @property
    def custom_except_class(self) -> Type[Exception]:
        """The exception to raise if a key does not exist in the dictionary"""
        return self._custom_except_class

    @custom_except_class.setter
    def custom_except_class(self, custom_except_class: Type[Exception]) -> None:
        if not issubclass(custom_except_class, Exception):
            raise TypeError(
                'Custom exceptions must be a subclass of `Exception`')

        self._custom_except_class = custom_except_class

    @property
    def custom_except_msg(self) -> str:
        """A custom error message if a key was not found in the dictionary

        The message must contain a single ``%s`` occurrence, which will
        be replaced by the name of the key which was not found.
        """
        return self._custom_except_msg

    @custom_except_msg.setter
    def custom_except_msg(self, custom_except_msg: str) -> None:
        if not (
            custom_except_msg.find('%s')
            == custom_except_msg.rfind('%s')
            != -1
        ):
            raise ValueError('Custom error message must contain exactly one '
                             'occurrence of "%s"')

        self._custom_except_msg = str(custom_except_msg)

    @property
    def multiline_print(self) -> bool:
        """Whether to print each entry of the dictionary on its own line when
        converting to a printable string representation"""
        return self._multiline_print

    @multiline_print.setter
    def multiline_print(self, multiline_print: bool) -> None:
        self._multiline_print = bool(multiline_print)

    @property
    def str_indent(self) -> int:
        """The number of spaces of indentation at the beginning of each line
        when converting a :py:class:`Dictionary` object to a printable
        string representation.  Only applicable if :py:attr:`multiline_print`
        is ``True``"""
        return self._str_indent

    @str_indent.setter
    def str_indent(self, str_indent: int):
        self._str_indent = int(str_indent)

    @property
    def str_pad_left(self) -> int:
        """The number of spaces between the printed key and the separator when
        converting a :py:class:`Dictionary` object to a printable string
        representation.  Only applicable if :py:attr:`multiline_print` is
        ``True``"""
        return self._str_pad_left

    @str_pad_left.setter
    def str_pad_left(self, str_pad_left: int):
        self._str_pad_left = int(str_pad_left)

    @property
    def str_pad_right(self) -> int:
        """The number of spaces between the separator and printed value when
        converting a :py:class:`Dictionary` object to a printable string
        representation.  Only applicable if :py:attr:`multiline_print` is
        ``True``"""
        return self._str_pad_right

    @str_pad_right.setter
    def str_pad_right(self, str_pad_right: int):
        self._str_pad_right = int(str_pad_right)

    def delete_index(self, index: int) -> None:
        """Removes an item from the dictionary based on its index

        Items can easily be removed from the dictionary by key (example: to
        remove an item with key ``'myKey'`` from a dictionary, simply call
        ``del dictionary['myKey']``).  This method extends this functionality
        and allows items to be removed based on their position in the
        dictionary.

        Parameters
        ----------
        index : int
            The index of the item to remove from the dictionary
        """
        del self[list(self.keys())[index]]

    def index(self, key: K) -> int:
        """Returns the index of a key in the dictionary

        Parameters
        ----------
        key : Any
            A key in the dictionary

        Returns
        -------
        int
            The location (beginning from 0) of ``key`` in the dictionary
        """
        if key not in self:
            raise KeyError(f'Key "{key}" not present in dictionary')

        return list(self.keys()).index(key)

    def insert(self, index: int, key: K, value: V) -> None:
        """Adds a new item to the dictionary at a specified position

        Parameters
        ----------
        index : int
            The position in the dictionary at which to insert the new key
        key : Any
            The key for the new item to insert int the dictionary
        value : Any
            The value for the new item to insert in the dictionary
        """
        if key in self:
            raise KeyError(f'Key "{key}" already exists, unable to overwrite')

        keys = list(self.keys())

        # Insert at beginning of dictionary
        self[key] = value

        # Rearrange items in dictionary so that new item is in the
        # correct position
        if index < len(self) / 2:
            self.move_to_end(key, last=False)

            for k in reversed(keys[0:index]):
                self.move_to_end(k, last=False)
        else:
            for k in reversed(keys[index:]):
                self.move_to_end(k, last=True)

        # It is not optimal to rearrange items iteratively, but the parent
        # `OrderedDict` class is written in C so we don't have access to
        # internal attributes and pointers that would make it faster (it would
        # be possible to rewrite the MahaUtils `Dictionary` for improved
        # efficiency, but the intended applications of the package
        # don't necessitate fast performance)

    def insert_after(self, existing_key: K, key: K, value: V) -> None:
        """Adds a new item to the dictionary at after another existing item
        in the dictionary

        Parameters
        ----------
        existing_key : Any
            The existing key in the dictionary after which ``key`` should
            be inserted
        key : Any
            The key for the new item to insert int the dictionary
        value : Any
            The value for the new item to insert in the dictionary
        """
        self.insert(self.index(existing_key) + 1, key, value)

    def insert_before(self, existing_key: K, key: K, value: V) -> None:
        """Adds a new item to the dictionary at before another existing item
        in the dictionary

        Parameters
        ----------
        existing_key : Any
            The existing key in the dictionary before which ``key`` should
            be inserted
        key : Any
            The key for the new item to insert int the dictionary
        value : Any
            The value for the new item to insert in the dictionary
        """
        self.insert(self.index(existing_key), key, value)
