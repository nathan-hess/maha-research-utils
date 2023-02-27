"""Adds a table to the documentation containing all the units defined by
default in the :py:class:`mahautils.multics.MahaMulticsUnitConverter`
class.  This table is constructed based on the MahaUtils source code, so it
is automatically updated if units are added or removed.
"""

import pathlib

from pyxx.arrays.functions.convert import convert_to_tuple
from mahautils.multics.units import _MAHA_MULTICS_DEFAULT_UNITS


DOCS_DIR = pathlib.Path(__file__).resolve().parents[2]


def __generate_entry(unit_data: dict, key: str, literal: bool = False,
                     leading_spaces: int = 6) -> str:
    line = f'{" " * leading_spaces}-'

    if (key in unit_data) and (unit_data[key] is not None):
        items = convert_to_tuple(unit_data[key])

        quote = '``' if literal else ''

        for i, item in enumerate(items):
            leading_chars = ' ' if i == 0 else ', '
            line += f'{leading_chars}{quote}{str(item)}{quote}'

    line += '\n'
    return line


def main():
    """Generates the units list reference page

    Copies the unit converter reference page, replacing the placeholder for
    the list of units with the list of units defined in the source code.
    """
    PLAIN = '\033[0m'
    PLAIN_BOLD = '\033[1m'
    print(f'{PLAIN_BOLD}Creating unit table...{PLAIN}', end='')

    # Settings
    path_io = DOCS_DIR / 'source' / 'usage' / 'reference'
    input_file = path_io / 'unitconverter_units.rst.template'
    output_file = path_io / 'unitconverter_units.rst'

    # Read input (template) file
    with open(input_file, 'r', encoding='utf_8') as fileID:
        template_lines = fileID.readlines()

    # Copy file, replacing `[[INSERT_UNIT_TABLE]]` with the table of units
    with open(output_file, 'w', encoding='utf_8') as fileID:
        for line in template_lines:
            if line.strip() == '[[INSERT_UNIT_TABLE]]':
                for key, unit_data in _MAHA_MULTICS_DEFAULT_UNITS.items():
                    fileID.write(f'    * - ``{key}``\n')
                    fileID.write(__generate_entry(unit_data, 'name'))
                    fileID.write(__generate_entry(unit_data, 'description'))
                    fileID.write(__generate_entry(unit_data, 'tags', True))
                    fileID.write(__generate_entry(unit_data, 'aliases', True))
            else:
                fileID.write(line)

    print(' done')
