"""Utilities to support other SimViewer code.
"""

import base64

from mahautils.multics.simresults import SimResults


def load_simresults(dash_base64_contents: str) -> SimResults:
    """Loads a simulation results file uploaded by Dash a :py:class:`dcc.Upload`
    object"""
    content_data = dash_base64_contents.split(',', maxsplit=1)[1]
    decoded_data = base64.b64decode(content_data).decode('utf_8')

    sim_results = SimResults()
    sim_results.set_contents(decoded_data.split('\n'), trailing_newline=True)
    sim_results.parse()

    return sim_results
