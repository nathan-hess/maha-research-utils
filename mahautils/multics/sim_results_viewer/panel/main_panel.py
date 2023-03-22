"""Code for the components of the simulation results viewer that configure
data and settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import (
    GUI_SHORT_NAME,
)
from .tab_data import data_files_tab
from .tab_plot_settings import plot_settings_tab


def simviewer_config_panel():
    """Creates the slide-in panel where users can configure SimViewer settings
    """
    default_width_percent = 45
    default_open = True

    contents = dbc.Tabs([
        dbc.Tab(
            data_files_tab(),
            label='Data Files',
            active_tab_class_name='fw-bold',
        ),
        dbc.Tab(
            plot_settings_tab(),
            label='Plot Settings',
            active_tab_class_name='fw-bold',
        ),
    ])

    return dbc.Offcanvas(
        contents,
        id='plot-config-panel',
        title=f'{GUI_SHORT_NAME} Configuration',
        placement='end',
        is_open=default_open,
        style={
            'width': f'{default_width_percent}vw',
        },
    )
