"""Configuration panel tab for changing plot settings and selecting which
data to plot.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash_bootstrap_components as dbc  # type: ignore

from .settings_general import plot_settings_general
from .settings_x import plot_settings_x
from .settings_y import plot_settings_y


def plot_settings_tab():
    """Creates the configuration panel tab (including sub-tabs) where display
    options can be configured"""
    tabs = [
        dbc.Tab(
            plot_settings_general(),
            label='General',
            active_tab_class_name='fw-bold',
        ),
        dbc.Tab(
            plot_settings_x(),
            label='X-Axis',
            active_tab_class_name='fw-bold',
        ),
        dbc.Tab(
            plot_settings_y(),
            label='Y-Axes',
            active_tab_class_name='fw-bold',
        ),
    ]

    return dbc.Tabs(tabs, style={'marginTop': '5px'})
