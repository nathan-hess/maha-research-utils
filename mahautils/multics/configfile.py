import pathlib
import re
from typing import List, Optional, Tuple, Union

import pyxx

from .exceptions import MahaMulticsFileFormatError


class MahaMulticsConfigFile(pyxx.files.TextFile):
    def __init__(self, path: Optional[Union[str, pathlib.Path]] = None
                 ) -> None:
        super().__init__(path=path, comment_chars='#')

    def _extract_section_by_keyword(self, section_label: str,
                                    begin_regex: str, end_regex: str,
                                    section_line_regex: Optional[str] = None,
                                    max_sections: Optional[int] = None,
                                    begin_idx: int = 0
                                    ) -> Tuple[List[re.Match], int, int]:
        # Validate inputs
        if (max_sections is not None) \
                and (max_sections := int(max_sections)) <= 0:
            raise ValueError('Argument "max_sections" must be a positive integer')

        # Counter to track how many sections have been found
        num_sections = 0

        # List to store all regex groups in the section
        section_groups = []

        # If no regex is provided for the lines within the section, match and
        # return any text
        if section_line_regex is None:
            section_line_regex = r'(.*)'

        i = begin_idx
        while i < len(self.contents):
            if (max_sections is not None) and (num_sections >= max_sections):
                break

            line = self.contents[i]

            # Identify lines beginning with a given regex pattern, and
            # extract all lines matching a particular regex pattern until
            # another specified regex pattern is encountered
            if (groups := re.search(begin_regex + '(.*)', line)) is not None:
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
