"""
Customized exceptions for the ``mahautils.utils`` module
"""


class UnmatchedParenthesesError(ValueError):
    """Error thrown if unmatched parentheses are found in an
    unexpected context"""
