import os

class File:
    def __init__(self) -> None:
        pass

class TextFile(File):
    def __init__(self, comment_char) -> None:
        self._contents: list = None
        self._comment_char: str = comment_char

        super().__init__()

    @property
    def contents(self):
        return self._contents

    def read(self, input_file: str):
        with open(input_file, 'r', encoding='UTF-8') as fileID:
            self._contents = fileID.readlines()
    
    def write(self, output_file: str, write_mode: str = 'w',
              prologue: str = None, epilogue: str = '\n',
              overwrite: bool = False):
        if os.path.isfile(output_file):
            if not overwrite:       # FIXME: add logger
                raise FileExistsError(f'Output file "{output_file}" '
                                      f'already exists')
        
        with open(output_file, write_mode, encoding='UTF-8') as fileID:
            fileID.write(prologue + '\n'.join(self._contents) + epilogue)

    def _clean_contents(self, remove_comments: bool = True, strip: bool = True,
                       concat_lines: bool = True,
                       remove_blank_lines: bool = True):
        # Store original file contents
        _orig_contents = self._contents

        # Clean file line-by-line
        self._contents = []
        i = 0
        while (i < len(_orig_contents)):
            line = _orig_contents[i]

            # If line is blank and blank lines are not to be removed, store it
            # and proceed to the next line of the file
            if (not(remove_blank_lines) and (len(line.strip()) == 0)):
                if strip:
                    line = line.strip()
                self._contents.append(line)
                i += 1
                continue

            # If line ends with "\", concatenate with next line
            if concat_lines:
                while (line.strip().endswith('\\') and (i < len(_orig_contents))):
                    line = line.rsplit('\\', maxsplit=1)[0] + _orig_contents[i+1]
                    i += 1

            # Remove comments
            if remove_comments:
                line = line.split(self._comment_char, maxsplit=1)[0]

            # Strip whitespace from beginning and end of line
            if strip:
                line = line.strip()

            # Store cleaned line and proceed to next iteration
            if (len(line.strip()) > 0):
                self._contents.append(line)
            i += 1

class BinaryFile(File):
    def __init__(self) -> None:
        super().__init__()

class Table(TextFile):
    def __init__(self, comment_char) -> None:
        super().__init__(comment_char)
