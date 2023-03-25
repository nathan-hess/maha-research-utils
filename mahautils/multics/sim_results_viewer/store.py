"""Data structures for storing program data in the browser.
"""

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
    contents = dash.dcc.Store(
        id='data-file-store',
        storage_type='session',
    )

    return contents


def plot_config_general_store():
    """Creates browser session storage for general plot settings
    """
    contents = dash.dcc.Store(
        id='plot-config-general-store',
        storage_type='session',
        data={},
    )

    return contents


def plot_config_x_store():
    """Creates browser session storage for x-axis plot settings
    """
    contents = dash.dcc.Store(
        id='plot-config-x-store',
        storage_type='session',
        data={},
    )

    return contents


def plot_config_y_store():
    """Creates browser session storage for y-axes plot settings
    """
    contents = dash.dcc.Store(
        id='plot-config-y-store',
        storage_type='session',
        data={},
    )

    return contents
