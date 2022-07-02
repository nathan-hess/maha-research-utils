"""
Customized exceptions for the ``mahautils.dictionary`` module
"""


class FileDictionaryPathExistsError(ValueError):
    """Error thrown if attempting to add a path to a
    ``mahautils.dictionary.FileDictionary`` object and
    the path already exists"""
