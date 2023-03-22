"""Panel tab for configuring y-axis plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore

from mahautils.multics.sim_results_viewer.constants import TAB_BAR_PADDING


def plot_settings_y():
    """Creates the configuration panel tab with settings for the y-axes"""
    return dash.html.H2(
        'y-axis settings',
        style={'marginTop': TAB_BAR_PADDING},
    )
