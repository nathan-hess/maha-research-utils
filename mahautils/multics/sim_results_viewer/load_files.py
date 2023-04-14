"""Utilities for loading simulation results and SimViewer configuration files.
"""

import base64
import json
from typing import Tuple

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore
from packaging.version import Version

from mahautils.multics.simresults import SimResults
from .constants import GUI_SHORT_NAME, PROJECT_NAME, VERSION


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

    return json.dumps(combined_data, indent=4)


def load_plot_config(dash_base64_contents: str) -> Tuple[dict, dict, dict]:
    """Loads plot configuration settings (general, x-axis, y-axes) from a file
    uploaded by Dash a :py:class:`dcc.Upload` object"""
    try:
        combined_data = json.loads(decode_base64(dash_base64_contents))
    except json.JSONDecodeError as exception:
        exception.args = ('Plot configuration file is not a valid JSON file',)
        raise

    try:
        version = combined_data['version']
        config_general = combined_data['general']
        config_x = combined_data['x']
        config_y = combined_data['y']
    except KeyError as exception:
        exception.args = (
            'Invalid plot configuration JSON file. The file does not contain '
            f'required key "{exception.args[0]}"',)
        raise

    minimum_version = '0.1.0'
    if Version(version) < Version(minimum_version):
        raise ValueError(
            'The plot configuration file you uploaded was generated with '
            f'{PROJECT_NAME} v{version}, but the minimum required version '
            f'that can be read is v{minimum_version}')

    maximum_version = VERSION
    if Version(version) > Version(maximum_version):
        raise ValueError(
            'The plot configuration file you uploaded was generated with '
            f'{PROJECT_NAME} v{version}, but the maximum permitted version '
            f'that can be read is v{maximum_version}')

    return config_general, config_x, config_y


load_plot_config_error_message = dash.html.Div([
    dash.html.P(
        'The plot configuration file you uploaded is not valid.  This typically '
        'occurs either because the file does not have the required format or '
        'the simulation results files it specifies have not been uploaded.'
    ),
    dash.html.Br(),
    dash.html.P(
        'To avoid issues, is generally recommended that you generate the plot '
        f'configuration file using the "Export" button in the {GUI_SHORT_NAME} '
        'GUI and do not manually edit it to avoid formatting issues.  Also, it '
        'is advisable to upload your simulation results files BEFORE importing '
        'a plot configuration file.'
    ),
])
