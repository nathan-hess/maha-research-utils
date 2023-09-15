"""Utility functions for reading and writing files."""

import base64
from typing import Dict, List, Union

import numpy as np

from mahautils.multics.simresults import SimResults


def decode_base64(base64_str: str) -> str:
    """Decodes Base64 binary data with UTF-8 encoding"""
    content_data = base64_str.split(',', maxsplit=1)[1]
    return base64.b64decode(content_data).decode('utf_8')


def load_simresults(dash_base64_contents: str, sim_results: SimResults) -> None:
    """Loads a simulation results file uploaded by Dash a :py:class:`dcc.Upload`
    object"""
    sim_results.clear()
    sim_results.set_contents(decode_base64(dash_base64_contents).split('\n'),
                             trailing_newline=True)
    sim_results.parse()


def sim_results_to_csv(sim_results: SimResults,
                       config: Dict[str, Dict[str, Union[bool, str]]]) -> str:
    """Saves simulation results data to a CSV file"""
    output_keys: List[str] = []
    output_units: List[str] = []
    output_data: List[np.ndarray] = []
    for key in config:
        export_settings = config.get(key, {'export': False})
        if not export_settings['export']:
            continue

        units = str(export_settings['units'])

        output_keys.append(key)
        output_units.append(units)

        if sim_results.num_time_steps > 0:
            output_data.append(sim_results.get_data(key, units))

    output_data_np = np.array(output_data).T

    # Create CSV file
    csv = ','.join(output_keys) + '\n'
    csv += ','.join(output_units) + '\n'

    if sim_results.num_time_steps > 0:
        for i in range(sim_results.num_time_steps):
            csv += ','.join([str(x) for x in output_data_np[i]]) + '\n'

    return csv
