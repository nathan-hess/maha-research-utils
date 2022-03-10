class InvalidFileFormat(Exception):
    def __init__(self, message='Error in file format'):
        super().__init__(message)
