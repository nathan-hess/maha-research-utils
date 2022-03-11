from .exceptions import InvalidFileFormat
from .files import File

class SimResults(File):
    def __init__(self, file: str, comment_char: str = '#',
                 autorefresh: bool = False):
        super().__init__()
        
        # Declare variables
        self.__filelines: list = None
        self.__title: str = None
        self.__simdata: dict = None

        # Store inputs
        self.__comment_char = comment_char
        self.autorefresh = autorefresh
        self.file = file

        # Read data file
        self.refresh()

    @property
    def title(self):
        if self.autorefresh:
            self.refresh()

        return self.__title

    @property
    def simdata(self):
        if self.autorefresh:
            self.refresh()

        return self.__simdata

    @property
    def printvars(self):
        return self.simdata.keys()

    @property
    def units(self):
        if self.autorefresh:
            self.refresh()

        return [self.__simdata[key]['units'] for key in self.__simdata]

    @property
    def descriptions(self):
        if self.autorefresh:
            self.refresh()

        return [self.__simdata[key]['description'] for key in self.__simdata]

    def __remove_blank_filelines(self):
        self.__filelines = [line for line in self.__filelines if len(line) > 0]

    def __remove_comment_filelines(self, comment_char: str = '#'):
        self.__filelines = [line.split(comment_char, maxsplit=1)[0] \
                            for line in self.__filelines]
        self.__remove_blank_filelines()

    def __get_max_list_str_len(self, input_list: list):
        max_len = 0

        for item in input_list:
            if (len(item) > max_len):
                max_len = len(item)

        return max_len

    def __print_var(self, key: str, indent: int = 0):
        if key not in self.__simdata.keys():
            raise KeyError(f'Unknown print variable "{key}"')

        _len_var = self.__get_max_list_str_len(self.printvars)
        _len_units = self.__get_max_list_str_len(self.units)

        _print_unit = f"[{self.__simdata[key]['units']}]"
        _print_desc = self.__simdata[key]['description']

        print(' ' * indent, end='')
        print(f"""{key:{_len_var+4}s} {_print_unit:{_len_units+4}s} {_print_desc}""")

    def __list_search_case_insensitive(self, name: str, search_list: list):
        matches = [item for item in search_list if name.lower() in item.lower()]
        return matches

    def refresh(self, read_file: bool = True, remove_newlines: bool = True):
        if read_file:
            # Read raw file contents
            with open(self.file, 'r') as fileID:
                self.__filelines = fileID.readlines()

            # Optionally remove newlines
            if remove_newlines:
                self.__filelines = [line.strip() for line in self.__filelines]

        # Remove blank lines
        self.__remove_blank_filelines()

        # Extract title
        _possible_titles = [line for line in self.__filelines \
                            if line.startswith((self.__comment_char + 'Title:',
                                                self.__comment_char + ' Title:'))]

        self.__title = _possible_titles[0].split('Title:', maxsplit=1)[1].strip()

        # Remove all comment lines
        self.__remove_comment_filelines(self.__comment_char)

        # Extract simulation results
        for i, line in enumerate(self.__filelines):
            if line.startswith('$'):
                _sim_vars = line.split('$')[1:]
                n = i + 1

        _sim_data = list(zip(*[[float(x) for x in line.split()] for line in self.__filelines[n:]]))

        if (len(_sim_vars) != len(_sim_data)):
            raise InvalidFileFormat(('Number of print variables and '
                                     'data columns are different'))

        self.__simdata = {}
        for i, var in enumerate(_sim_vars):
            _var = var.split(':')

            if (len(_var) != 3):
                raise InvalidFileFormat('Print variable format is incorrect')

            self.__simdata[_var[0]] = {
                'units': _var[1],
                'description': _var[2],
                'data': _sim_data[i],
            }

    def get(self, var: str, refresh: bool = False):
        if (refresh or self.autorefresh):
            self.refresh()

        return self.__simdata[var]

    def get_printvar(self, description: str):
        matches = [key for key in self.printvars \
                   if self.get(key)['description'] == description]

        if (len(matches) != 1):
            raise KeyError(f'Unable to find unique print variable for '
                           f'description "{description}"')

        return matches[0]

    def search(self, name: str):
        # Get lists of variable names and descriptions
        _printvars = self.printvars
        _descriptions = self.descriptions

        # Check list of print variables
        if (name in _printvars):
            print(f'Found print variable "{name}":')
            self.__print_var(name, indent=4)

        # Check list of print variable descriptions
        elif (name in _descriptions):
            print(f'Found description "{name}":')
            self.__print_var(self.get_printvar(name), indent=4)

        # Print variables and descriptions that contain `name`
        else:
            print(f'Unable to find "{name}"')

            # Display similar print variables
            _matches = self.__list_search_case_insensitive(name, _printvars)
            if (len(_matches) > 0):
                print(f'\nThe following print variables contain "{name}":')
                for var in _matches:
                    self.__print_var(var, indent=4)

            # Display similar print variable descriptions
            _matches = self.__list_search_case_insensitive(name, _descriptions)
            if (len(_matches) > 0):
                print(f'\nThe following descriptions contain "{name}":')
                for desc in _matches:
                    self.__print_var(self.get_printvar(desc), indent=4)
