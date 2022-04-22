import os

from .dictionary import Dictionary

class FileDict(Dictionary):
    def __init__(self, base_dir: str):
        super().__init__()

        # Store inputs
        self.base_dir = base_dir
    
    @property
    def base_dir(self):
        return self._base_dir
    
    @base_dir.setter
    def base_dir(self, path: str):
        self._base_dir = os.path.abspath(path)

    @property
    def names(self):
        return self._contents.keys()
    
    def add_file(self, name: str, path: str):
        if name in self._contents:
            raise KeyError(f'Key "{name}" is already defined in file dictionary')
        
        self._contents[name] = path
    
    def get(self, name: str):
        if name in self._contents:
            return self._contents[name]
        else:
            raise KeyError(f'Key "{name}" has not been defined')
    
    def getabs(self, name: str):
        return os.path.abspath(os.path.join(self._base_dir, self.get(name)))
