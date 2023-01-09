"""Utilities for capturing text printed to the terminal when running Python
code.
"""

import io
import os
import sys
import tempfile


class CaptureStderr:
    """Captures ``stderr`` text printed to the terminal when running commands

    Redirects output sent to ``stderr``, including output from C-level
    streams.  This approach is adapted from:

    Bendersky (2015). "Redirecting all kinds of stdout in Python." Retrieved from
    https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python.

    Warnings
    --------
    This class modifies the ``stderr`` file descriptor, including redirecting
    ``stderr`` to a temporary file, so it can cause problems for other code
    that relies on streams (for instance, it may cause ``unittest`` tests to
    fail in some cases).
    """

    def __init__(self, stream: io.BytesIO) -> None:
        # Store stream to which to output captured text
        self._stream = stream

        # Store the original `stderr` file descriptor
        self._current_stderr_fd = sys.stderr.fileno()

        # Create a saved copy of the original `stderr` file descriptor
        self._original_stderr_fd = os.dup(self._current_stderr_fd)

        # Create temporary file to which to redirect `stderr`
        self._temp_file = tempfile.TemporaryFile(mode='w+b')

    def __redirect_stderr(self, file_descriptor: int):
        """Directs ``stderr`` to a given file descriptor"""
        # Flush and close `sys.stderr`
        sys.stderr.close()

        # Direct `stderr` to the given file descriptor
        os.dup2(file_descriptor, self._current_stderr_fd)
        sys.stderr = io.TextIOWrapper(os.fdopen(self._current_stderr_fd, 'wb'))

    def __enter__(self):
        # Redirect `stderr` to a temporary file
        self.__redirect_stderr(self._temp_file.fileno())

    def __exit__(self, *args, **kwargs):
        # Redirect `stderr` back to original file descriptor
        self.__redirect_stderr(self._original_stderr_fd)

        # Write captured `stderr` content to stream
        self._temp_file.flush()
        self._temp_file.seek(0, io.SEEK_SET)
        self._stream.write(self._temp_file.read())

        # Delete temporary file
        self._temp_file.close()

        # Restore original `stderr`
        os.close(self._original_stderr_fd)
