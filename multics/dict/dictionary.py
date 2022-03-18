class Dictionary:
    def __init__(self) -> None:
        self._contents = {}
    
    def __len__(self) -> int:
        return len(self._contents)

    @property
    def contents(self):
        return self._contents

    def clean(self):
        self._contents = {}
