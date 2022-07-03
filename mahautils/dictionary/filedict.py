"""
This module provides a data structure in which a collection of relative
and/or absolute paths can be stored, each with a unique identifier
"""

import pathlib
from typing import List, Union, Tuple

from mahautils.utils.vartools import check_len_equal
from .dictionary import Dictionary
from .exceptions import FileDictionaryPathExistsError


class FileDictionary(Dictionary):
    """Dictionary for storing paths, each with a unique identifier

    This dictionary is intended to store a collection of relative and/or
    absolute paths.  This class inherits from the
    ``mahautils.dictionary.Dictionary`` class, so all attributes and
    methods of this general dictionary, as well as Python's built-in
    dictionaries, should be applicable to ``FileDictionary`` instances

    Attributes
    ----------
    base_dir : pathlib.Path
        Base directory relative to which relative paths stored in the
        ``FileDictionary`` are referenced (stored as an absolute path)

    Methods
    -------
    add():
        Adds a file or path to the file dictionary
    add_batch():
        Adds a set of keys and paths to the file dictionary
    get_abs():
        Retrieves a path and/or filename from the dictionary,
        converted to an absolute path
    get_raw():
        Retrieves a path and/or filename from the dictionary
    validate_paths():
        Checks whether all paths in the dictionary exist
    """

    def __init__(self, base_dir: Union[str, pathlib.Path], **kwargs):
        """Defines a file dictionary object

        Creates a new ``FileDictionary`` object, intended to store a set of
        paths, each associated with a unique key.  Paths can be relative or
        absolute; relative paths are resolved relative to a given base
        directory

        Parameters
        ----------
        base_dir : str or pathlib.Path
            Base directory from which relative paths stored in the dictionary
            are referenced
        """
        # Prevent users from passing the "content" keyword argument (this
        # way, they have to use the file dictionary's customized methods
        # to add content to the dictionary)
        if 'contents' in kwargs:
            del kwargs['contents']

        # Pass any remaining keyword arguments to parent class
        super().__init__(**kwargs)

        # Verify that `base_dir` exists and can be converted
        # to an absolute path
        self._base_dir = self.__to_abs(pathlib.Path(base_dir))

        if not self._base_dir.is_absolute():
            raise ValueError(
                f'Unable to convert `base_dir` argument "{base_dir}" to '
                'an absolute path')

        if not self._base_dir.is_dir():
            raise NotADirectoryError(
                f'Base directory "{base_dir}" does not exist, or it '
                'is not a directory')

    def __setitem__(self, key: str, value: Union[str, pathlib.Path]):
        super().__setitem__(key, pathlib.Path(value))

    def __to_abs(self, path: pathlib.Path):
        """Converts a ``pathlib.Path`` object to an absolute path"""
        return path.expanduser().resolve().absolute()

    @property
    def base_dir(self):
        """Returns the absolute path to the base directory relative to which
        relative paths stored in the dictionary are defined"""
        return self._base_dir

    def add(self, key: str, path: Union[str, pathlib.Path],
            overwrite: bool = False):
        """Adds a file or path to the file dictionary

        Parameters
        ----------
        key : str
            Key to identify path/filename in the dictionary
        path : str or pathlib.Path
            Path and/or filename to store in the dictionary
        overwrite : bool, optional
            Whether to modify the existing path in the dictionary if the
            key given by ``key`` already exists (default is ``False``)
        """
        if key not in self.keys() or overwrite:
            self[key] = path
        else:
            raise FileDictionaryPathExistsError(
                f'Key "{key}" already exists. It is currently associated '
                f'with path "{self[key]}" but can be overridden by calling '
                '`.add()` with `overwrite=True`')

    def add_batch(self, keys: Union[Tuple[str, ...], List[str]],
                  paths: Union[Tuple[Union[str, pathlib.Path], ...],
                               List[Union[str, pathlib.Path]]],
                  overwrite: bool = False):
        """Adds a set of keys and paths to the file dictionary

        Adds multiple keys and paths to the file dictionary simultaneously.
        Note that the lengths of ``keys`` and ``paths`` must be the same

        Parameters
        ----------
        keys : tuple or list of str
            Keys to identify paths/filenames in the dictionary
        paths : tuple or list of str or pathlib.Path
            Paths and/or filenames to store in the dictionary
        overwrite : bool, optional
            Whether to modify existing paths in the dictionary if the
            a key given by ``keys`` already exists (default is ``False``)
        """
        # Check that inputs are lists or tuples
        if not(isinstance(keys, (list, tuple))):
            raise TypeError('Input "keys" must be a list or tuple')

        if not(isinstance(paths, (list, tuple))):
            raise TypeError('Input "paths" must be a list or tuple')

        # Verify that inputs have equal lengths
        len_equal, lengths = check_len_equal(keys, paths)

        # Store keys and paths
        if len_equal:
            for key, path in zip(keys, paths):
                self.add(key, path, overwrite)
        else:
            raise ValueError(
                'Arguments "keys" and "paths" must have equal lengths, but '
                f'lengths provided were {lengths}')

    def get_abs(self, name: str):
        """Retrieves a path and/or filename from the dictionary,
        converted to an absolute path

        Returns a path from the file dictionary, converted to an
        absolute path.  Relative paths are resolved relative to
        ``self.base_dir``

        Parameters
        ----------
        name : str
            String specifying the path and/or filename to retrieve

        Returns
        -------
        pathlib.Path
            Path and/or filename corresponding to the ``name`` key,
            as an absolute path
        """
        path = self.get_raw(name)

        if path.is_absolute():
            return path
        else:
            return self.__to_abs(self.base_dir / path)

    def get_raw(self, name: str) -> pathlib.Path:
        """Retrieves a path and/or filename from the dictionary

        Returns the unmodified path from the file dictionary.  The path
        returned is an unmodified version of the original path stored in
        the dictionary, with the exception of possible conversion to a
        ``pathlib.Path`` object

        Parameters
        ----------
        name : str
            String specifying the path and/or filename to retrieve

        Returns
        -------
        pathlib.Path
            Path and/or filename corresponding to the ``name`` key
        """
        if name in self:
            return self[name]
        else:
            raise KeyError(
                f'Path and/or file with key "{name}" was not found')

    def validate_paths(self, print_results: bool = True):
        """Checks whether all paths in the dictionary exist

        Checks and returns whether all files and/or paths in the file
        dictionary exist, optionally printing all existing and non-
        existent paths

        Parameters
        ----------
        print_results : bool, optional
            Whether to print existing and non-existent paths

        Returns
        -------
        bool
            Whether all paths in the file dictionary exist
        int
            Number of items in file dictionary that exist
        int
            Number of items in file dictionary that do not exist
        """
        existing_paths = Dictionary()
        nonexistent_paths = Dictionary()

        # Check whether each path exists
        key: str
        path: pathlib.Path
        for key, path in self.items():
            if (self.base_dir / path).exists():
                existing_paths[key] = path
            else:
                nonexistent_paths[key] = path

        num_existing = len(existing_paths)
        num_nonexistent = len(nonexistent_paths)
        num_paths = num_existing + num_nonexistent

        # Display results
        if print_results:
            print(f'Checked {num_paths} path(s)')

            if num_existing > 0:
                print(f'\nThe following {num_existing} path(s) exist:')
                print(existing_paths)

            if num_nonexistent > 0:
                print(f'\nThe following {num_nonexistent} path(s) do NOT exist:')
                print(nonexistent_paths)

            if num_nonexistent == 0:
                print('\nAll path(s) in dictionary exist')

        # Return results
        return (num_nonexistent == 0, num_existing, num_nonexistent)
