import warnings

from multics.utils.vartools import list_search, max_list_item_len
from .exceptions import InvalidFileFormat
from .files import File

class SimResults(File):
    def __init__(self, file: str, comment_char: str = '#',
                 autorefresh: bool = False):
        super().__init__(comment_char)

        # Declare variables
        self._contents: list = None
        self._title: str = None
        self._simdata: dict = None

        # Store inputs
        self.autorefresh = autorefresh
        self.file = file

        # Read data file
        self.refresh()

    @property
    def title(self):
        if self.autorefresh:
            self.refresh()

        return self._title

    @property
    def simdata(self):
        if self.autorefresh:
            self.refresh()

        return self._simdata

    @property
    def printvars(self):
        return self.simdata.keys()

    @property
    def units(self):
        if self.autorefresh:
            self.refresh()

        return [self._simdata[key]['units'] for key in self._simdata]

    @property
    def descriptions(self):
        if self.autorefresh:
            self.refresh()

        return [self._simdata[key]['description'] for key in self._simdata]
    
    def read(self, file: str):
        self.file = file
        self.refresh(read_file=True)
    
    def write(self, output_file: str):
        super().write(output_file, prologue=f'# Title: {self._title}\n')

    def __print_var(self, key: str, indent: int = 0):
        if key not in self._simdata:
            raise KeyError(f'Unknown print variable "{key}"')

        _len_var = max_list_item_len(self.printvars)
        _len_units = max_list_item_len(self.units)

        _print_unit = f"[{self._simdata[key]['units']}]"
        _print_desc = self._simdata[key]['description']

        print(' ' * indent, end='')
        print(f"""{key:{_len_var+4}s} {_print_unit:{_len_units+4}s} {_print_desc}""")

    def refresh(self, read_file: bool = True, remove_newlines: bool = True):
        # Read raw file contents
        if read_file:
            super().read(self.file)

        # Extract title
        _possible_titles = [line for line in self._contents \
                            if line.startswith((self._comment_char + 'Title:',
                                                self._comment_char + ' Title:'))]

        if len(_possible_titles) > 1:
            warnings.warn('Multiple simulation result titles found. Using first title')

        self._title = _possible_titles[0].split('Title:', maxsplit=1)[1].strip()

        # Pre-process input file
        self._clean_contents(
            remove_comments=True,
            strip=True,
            concat_lines=True,
            remove_blank_lines=remove_newlines
        )

        # Extract simulation results
        for i, line in enumerate(self._contents):
            if line.startswith('$'):
                _sim_vars = line.split('$')[1:]
                n = i + 1

        _sim_data = list(zip(*[[float(x) for x in line.split()] for line in self._contents[n:]]))

        if (len(_sim_vars) != len(_sim_data)):
            raise InvalidFileFormat(('Number of print variables and '
                                     'data columns are different'))

        self._simdata = {}
        for i, var in enumerate(_sim_vars):
            _var = var.split(':')

            if (len(_var) != 3):
                raise InvalidFileFormat('Print variable format is incorrect')

            self._simdata[_var[0]] = {
                'units': _var[1],
                'description': _var[2],
                'data': _sim_data[i],
            }

    def get(self, var: str, refresh: bool = False):
        if (refresh or self.autorefresh):
            self.refresh()

        return self._simdata[var]

    def get_data(self, var: str, refresh: bool = False):
        return self.get(var, refresh)['data']

    def get_printvar(self, description: str):
        matches = [key for key in self.printvars \
                   if self.get(key)['description'] == description]

        if (len(matches) != 1):
            raise KeyError(f'Unable to find unique print variable for '
                           f'description "{description}"')

        return matches[0]

    def search(self, name: str, case_sensitive: bool = False,
               print_results: bool = True, return_results: bool = False):
        # Get lists of variable names and descriptions
        _printvars = self.printvars
        _descriptions = self.descriptions

        # Check list of print variables
        if (name in _printvars):
            if print_results:
                print(f'Found print variable "{name}":')
                self.__print_var(name, indent=4)

            if return_results:
                return {
                    'match_found': True,
                    'match_type': 'printvar',
                    'matches_printvar': [name],
                }

        # Check list of print variable descriptions
        elif (name in _descriptions):
            if print_results:
                print(f'Found description "{name}":')
                self.__print_var(self.get_printvar(name), indent=4)

            if return_results:
                return {
                    'match_found': True,
                    'match_type': 'description',
                    'matches_description': [self.get_printvar(name)],
                }

        # Print variables and descriptions that contain `name`
        else:
            if print_results:
                print(f'Unable to find "{name}"')

            if return_results:
                output_dict = {'match_found': False}

            # Display similar print variables
            _matches = list_search(name, _printvars, case_sensitive)
            if (len(_matches) > 0):
                if print_results:
                    print(f'\nThe following print variables contain "{name}":')
                    for var in _matches:
                        self.__print_var(var, indent=4)

                if return_results:
                    output_dict['matches_printvar'] = list(_matches)

            # Display similar print variable descriptions
            _matches = list_search(name, _descriptions, case_sensitive)
            if (len(_matches) > 0):
                if print_results:
                    print(f'\nThe following descriptions contain "{name}":')
                    for desc in _matches:
                        self.__print_var(self.get_printvar(desc), indent=4)

                if return_results:
                    output_dict['matches_description'] \
                        = [self.get_printvar(desc) for desc in _matches]

            if return_results:
                return output_dict

    def search_noninteractive(self, name: str, case_sensitive: bool = False) -> dict:
        return self.search(name, case_sensitive, False, True)
