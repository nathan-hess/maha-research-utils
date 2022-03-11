class File:
    def __init__(self, comment_char) -> None:
        self.__contents: list = None
        self.__comment_char: str = comment_char

    @property
    def contents(self):
        return self.__contents
    
    def set_contents(self, data: list):
        if not(isinstance(data, list)):
            raise ValueError('Input data must be a list')
        self.__contents = data
    
    def readlines(self, file: str):
        with open(file, 'r') as fileID:
            self.__contents = fileID.readlines()

    def clean_contents(self, remove_comments: bool = True, strip: bool = True,
                       concat_lines: bool = True,
                       remove_blank_lines: bool = True):
        # Store original file contents
        __orig_contents = self.__contents

        # Clean file line-by-line
        self.__contents = []
        i = 0
        while (i < len(__orig_contents)):
            line = __orig_contents[i]

            # If line is blank and blank lines are not to be removed, store it
            # and proceed to the next line of the file
            if (not(remove_blank_lines) and (len(line.strip()) == 0)):
                if strip:
                    line = line.strip()
                self.__contents.append(line)
                i += 1
                continue
            
            # If line ends with "\", concatenate with next line
            if concat_lines:
                while (line.strip().endswith('\\') and (i < len(__orig_contents))):
                    line = line.rsplit('\\', maxsplit=1)[0] + __orig_contents[i+1]
                    i += 1
            
            # Remove comments
            if remove_comments:
                line = line.split(self.__comment_char, maxsplit=1)[0]
            
            # Strip whitespace from beginning and end of line
            if strip:
                line = line.strip()
            
            # Store cleaned line and proceed to next iteration
            if (len(line.strip()) > 0):
                self.__contents.append(line)
            i += 1
