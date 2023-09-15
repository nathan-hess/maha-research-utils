"""Utility functions for reading and writing files."""

import base64
from mahautils.multics import SimResults


def decode_base64(base64_str: str) -> str:
    """Decodes Base64 binary data with UTF-8 encoding"""
    content_data = base64_str.split(',', maxsplit=1)[1]
    return base64.b64decode(content_data).decode('utf_8')


def load_simresults(dash_base64_contents: str) -> SimResults:
    """Loads a simulation results file uploaded by Dash a :py:class:`dcc.Upload`
    object"""
    sim_results = SimResults()
    sim_results.set_contents(decode_base64(dash_base64_contents).split('\n'),
                             trailing_newline=True)
    sim_results.parse()

    return sim_results
