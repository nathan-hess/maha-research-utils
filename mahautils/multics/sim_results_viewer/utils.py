"""Utilities to support other SimViewer code.
"""

import base64
import json
from typing import Tuple

from mahautils.multics.simresults import SimResults
from .constants import VERSION


def decode_base64(base64_str: str) -> str:
    """Decodes Base64 binary data with UTF-8 encoding"""
    content_data = base64_str.split(',', maxsplit=1)[1]
    return base64.b64decode(content_data).decode('utf_8')


## SIMULATION RESULTS FILES ##

def load_simresults(dash_base64_contents: str) -> SimResults:
    """Loads a simulation results file uploaded by Dash a :py:class:`dcc.Upload`
    object"""
    sim_results = SimResults()
    sim_results.set_contents(decode_base64(dash_base64_contents).split('\n'),
                             trailing_newline=True)
    sim_results.parse()

    return sim_results


## PLOT CONFIGURATION FILES ##

def plot_config_to_str(config_general: dict, config_x: dict, config_y: dict):
    """Combines plot configuration settings (general, x-axis, y-axes) into a
    single dictionary and exports it as a string"""
    combined_data = {
        'version': VERSION,
        'general': config_general,
        'x': config_x,
        'y': config_y,
    }

    return json.dumps(combined_data)


def load_plot_config(dash_base64_contents: str) -> Tuple[dict, dict, dict]:
    """Loads plot configuration settings (general, x-axis, y-axes) from a file
    uploaded by Dash a :py:class:`dcc.Upload` object"""
    combined_data = json.loads(decode_base64(dash_base64_contents))

    config_general = combined_data['general']
    config_x = combined_data['x']
    config_y = combined_data['y']

    return config_general, config_x, config_y
