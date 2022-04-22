##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import os

# Custom package and module imports
from mahautils.dict import FileDict, UnitDict, BASE_UNITS
from .exceptions import VarExists, VarDoesNotExist
from .files import File


##############################################################################
# --- INPUT DICTIONARY FILE READER/WRITER ---------------------------------- #
##############################################################################
class InputDict(File):
    def __init__(self, comment_char: str = '#'):
        super().__init__(comment_char)

        # Declare variables
        self._filedict: FileDict = None
        self._vars = {}
        self._unitdict: UnitDict = None
        self._mode: str = None

    def __extract_contents_dict_by_keyword(self, keyword: str, i: int,
                                           line_list: list):
        if self._contents[i].lower().startswith(keyword.lower() + '{'):
            # Extract any lines on the first line (after the dictionary
            # keyword identifier)
            line_no_identifier = self._contents[i][(len(keyword)+1):]
            if (len(line_no_identifier.strip()) > 0):
                line_list.append(line_no_identifier)
            i += 1

            # Extract all remaining lines in dictionary
            while not((line := self._contents[i]).strip().startswith('}')):
                line_list.append(line)
                i += 1
            
            i += 1

        return i

    def read(self, file: str, clean: bool = True,
             base_unit_names: list = BASE_UNITS['MKS']):
        self._mode = 'read'
        self._file = file

        # Read from file and clean input
        super().read(file)

        super()._clean_contents(
            remove_comments=True,
            strip=True,
            concat_lines=True,
            remove_blank_lines=True
        )

        # Separate into file dictionary, variables list, and unit dictionary
        _lines_filedict = []
        _lines_vars = []
        _lines_unitdict = []

        i = 0
        while (i < len(self._contents)):
            # Extract lines in file dictionary
            if (i != (i := self.__extract_contents_dict_by_keyword(
                               'fileDict', i, _lines_filedict))):
                # If `i` has changed, re-evaluate the while loop condition
                # (to verify the end of the file has not yet been reached)
                continue

            # Extract lines in unit dictionary
            if (i != (i := self.__extract_contents_dict_by_keyword(
                               'unitDict', i, _lines_unitdict))):
                # If `i` has changed, re-evaluate the while loop condition
                # (to verify the end of the file has not yet been reached)
                continue

            # Any lines not in the file dictionary or unit dictionary should
            # be variable definitions
            _lines_vars.append(self._contents[i])
            
            i += 1

        # Store file dictionary
        if ((self._filedict is None) or clean):
            self._filedict = FileDict(base_dir=os.path.dirname(file))
        
        for line in _lines_filedict:
            _split_line = line.split(maxsplit=1)
            self._filedict.add_file(_split_line[0], _split_line[1])

        # Store variables
        for line in _lines_vars:
            _key, _unit, _val = line.split(maxsplit=2)

            if _key in self._vars:
                raise VarExists(f'Variable "{_key}" is already defined '
                                f'in the variables list')
            
            try:
                _val = float(_val)
                _type = 'number'
            except ValueError:
                _type = 'formula'
            
            self._vars[_key] = {
                'unit': _unit,
                'value': _val,
                'type': _type,
            }

        # Store unit dictionary
        if ((self._unitdict is None) or clean):
            self._unitdict = UnitDict(base_unit_names)

        _first_unit = False
        for line in _lines_unitdict:
            if line.strip().startswith('['):
                _base_exps = [float(i) for i in \
                    line.replace('[', '').replace(']', '').strip().split()]
                _first_unit = True
            else:
                if not(_first_unit):
                    continue
                else:
                    _unit, _m, _b = line.strip().split()
                    self._unitdict.add_unit(
                        unit=_unit,
                        base_exps=_base_exps,
                        m=float(_m),
                        b=float(_b)
                    )

    def get_file(self, name: str, abspath: bool = False):
        _path = self._filedict.get(name)
        
        if abspath:
            return os.path.abspath(os.path.join(self._filedict.base_dir, _path))
        else:
            return _path

    def get_var(self, name: str, units: str = None):
        if not(name in self._vars):
            raise VarDoesNotExist(f'Variable "{name}" is not defined '
                                  f'in the variables list')
        
        # Retrieve variable data from variables dictionary
        _var_data = self._vars[name]

        # Convert units if requested by user
        if units is not None:
            if not(_var_data['type'] == 'number'):
                raise ValueError('Only type "number" variables can '
                                 'undergo unit conversions')

            _var_data['value'] \
                = self._unitdict.convert_unit(_var_data['value'],
                                              from_unit=_var_data['unit'],
                                              to_unit=units)
            _var_data['unit'] = units

        return _var_data
