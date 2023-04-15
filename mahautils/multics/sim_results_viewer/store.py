"""Data structures for storing program data in the browser.
"""

from typing import Any, Dict

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore


def file_metadata_store():
    """Creates browser session storage for metadata about uploaded simulation
    results files

    Format
    ------
    ```
    {
        'sim_results_file_name_1': {
            'enabled': True,
        },
        'sim_results_file_name_2': {
            'enabled': False,
        },
    }
    ```
    """
    return dash.dcc.Store(
        id='data-file-store',
        storage_type='session',
    )


default_plot_config_general: Dict[str, Any] = {
    'title': None,
    'background_color': '#ffffff',
    'grid_x': True,
    'grid_y': True,
    'append_units': False,
    'width_per_y_axis': 0.1,
    'hovermode': 'closest',
    'freeze_uirevision': False,
    'image_export_type': 'png',
    'image_export_width': None,
    'image_export_height': None,
    'image_export_scale': 1,
}

default_plot_config_x: Dict[str, Any] = {
    'axis_title': None,
    'variable': None,
    'units': None,
    'xmin': None,
    'xmax': None,
    'tick_spacing': None,
}

default_plot_config_y: Dict[str, Any] = {
    'axes': [],
}

default_y_axis_settings: Dict[str, Any] = {
    'axis_title': None,
    'enabled': True,
    'color': '#000000',
    'ymin': None,
    'ymax': None,
    'tick_spacing': None,
    'traces': [],
}

default_trace_settings: Dict[str, Any] = {
    'name': None,
    'enabled': True,
    'file': None,
    'variable': None,
    'units': None,
    'style': {
        'color': '#1f77b4',
        'width': 2,
        'dash': 'solid',
    },
}


def plot_config_general_store():
    """Creates browser session storage for general plot settings
    """
    return dash.dcc.Store(
        id='plot-config-general-store',
        storage_type='session',
        data=default_plot_config_general,
    )


def plot_config_x_store():
    """Creates browser session storage for x-axis plot settings
    """
    return dash.dcc.Store(
        id='plot-config-x-store',
        storage_type='session',
        data=default_plot_config_x,
    )


def plot_config_y_store():
    """Creates browser session storage for y-axes plot settings
    """
    return dash.dcc.Store(
        id='plot-config-y-store',
        storage_type='session',
        data=default_plot_config_y,
    )
