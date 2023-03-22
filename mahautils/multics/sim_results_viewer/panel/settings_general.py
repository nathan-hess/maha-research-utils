"""Panel tab for configuring general plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore

from mahautils.multics.sim_results_viewer.constants import TAB_BAR_PADDING


def plot_settings_general():
    """Creates the configuration panel tab with general plot settings"""
    return dash.html.H2(
        'General settings',
        style={'marginTop': TAB_BAR_PADDING},
    )
