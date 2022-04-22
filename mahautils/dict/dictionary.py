from mahautils.utils.vartools import max_list_item_len

class Dictionary:
    def __init__(self) -> None:
        self._contents = {}

    def __str__(self) -> str:
        _padding = 2
        _max_key_len = max_list_item_len(self.keys())

        return '\n'.join([(f'{key:{_max_key_len+_padding}s}:'
                           f'{" "*_padding}{self._contents[key]}') \
                         for key in self.keys()])
    
    def __len__(self) -> int:
        return len(self._contents)

    @property
    def contents(self):
        return self._contents

    def clean(self):
        self._contents = {}

    def keys(self):
        return self._contents.keys()
