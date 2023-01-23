"""This module provides a base class intended to aid in reading, parsing, and
writing Maha Multics configuration files.
"""

import pathlib
import re
from typing import List, Optional, Tuple, Union

import pyxx

from .exceptions import MahaMulticsFileFormatError


class MahaMulticsConfigFile(pyxx.files.TextFile):
    """A generic class for processing Maha Multics configuration files

    This class is intended to represent a range of Maha Multics configuration
    files, and configures settings (such as the character used for comments)
    that are applicable to all Maha Multics configuration files, as well as
    providing general methods for processing such files.  Subclasses should
    generally be created and customized to specific types of Maha Multics
    files.
    """

    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None
                 ) -> None:
        """Creates an object to represent Maha Multics configuration files

        Creates an instance of the :py:class:`MahaMulticsConfigFile` class,
        including configuring file comments to be represented by the ``#``
        character.

        Parameters
        ----------
        path : str or pathlib.Path, optional
            Location of the text file in the file system  (default is ``None``)
        """
        super().__init__(path=path, comment_chars='#')

    def _extract_section_by_keyword(self, section_label: str,
                                    begin_regex: str, end_regex: str,
                                    section_line_regex: str = r'(.*)',
                                    max_sections: Optional[int] = None,
                                    begin_idx: int = 0
                                    ) -> Tuple[List[re.Match], int, int]:
        """Extracts a section from the :py:attr:`contents` list of file lines

        Many Maha Multics configuration files contain sections with certain
        types of data, where the section begins following a formatted section
        marker and ends at another marker (both with unique, identifiable
        regex patterns).  This method extracts the data from such a section.
        If multiple sections are found, the data in all sections is merged,
        unless specified otherwise by setting ``max_sections``.

        Parameters
        ----------
        section_label : str
            A descriptive name identifying the section.  This is not used in
            parsing the file; it is only used to customize error messages and
            make them more descriptive
        begin_regex : str
            The regex pattern which marks the beginning of the section
        end_regex : str
            The regex pattern which marks the end of the section
        section_line_regex : str, optional
            If provided, this regex pattern must be matched by all lines
            inside the section (default is ``'(.*)'``, which matches any text)
        max_sections : int, optional
            The maximum number of sections to extract; that is, only the first
            ``max_sections`` encountered will be extracted and returned
            (default is ``None``, which extracts all sections)
        begin_idx : int, optional
            The index (in the :py:attr:`contents` list) at which to begin to
            search for and extract data from sections (default is ``0``)

        Returns
        -------
        list
            A list of :py:class:`re.Match` objects containing the matches for
            the regex pattern ``section_line_regex`` for all lines in the
            section(s)
        int
            The index of :py:attr:`contents` of the next line immediately
            following the line on which ``end_regex`` was found
        int
            The number of sections that were extracted from the
            :py:attr:`contents` list
        """
        # Validate inputs
        if (max_sections is not None) \
                and (max_sections := int(max_sections)) <= 0:
            raise ValueError('Argument "max_sections" must be a positive integer')

        # Counter to track how many sections have been found
        num_sections = 0

        # List to store all regex groups in the section
        section_groups = []

        # Iterate through file and extract section contents
        i = begin_idx
        while i < len(self.contents):
            if (max_sections is not None) and (num_sections >= max_sections):
                break

            line = self.contents[i]

            # Identify lines beginning with a given regex pattern, and
            # extract all lines matching a particular regex pattern until
            # another specified regex pattern is encountered
            if (groups := re.search(begin_regex + r'(.*)', line)) is not None:
                num_sections += 1

                # Check to see whether there are data to be extracted on the
                # same line as the beginning section identifier (and if not,
                # advance to next line)
                if (line := groups.groups()[-1]) == '':
                    i += 1
                    line = self.contents[i]

                while not re.match(end_regex, line):
                    groups = re.search(section_line_regex, line)

                    if groups is None:
                        raise MahaMulticsFileFormatError(
                            f'Line "{line}" in section "{section_label}" does '
                            'not match expected pattern')

                    section_groups.append(groups)

                    i += 1

                    if i >= len(self.contents):
                        raise MahaMulticsFileFormatError(
                            f'Unable to locate end of "{section_label}" section')

                    line = self.contents[i]

            i += 1

        return (section_groups, i, num_sections)
