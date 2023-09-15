"""Code for generating the header of the simulation results exporter.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore

from .constants import GUI_LONG_NAME, PROJECT_NAME


def app_header():
    """Creates a formatted header for the application"""

    return dash.html.Div([
        dash.html.H2(
            f'{PROJECT_NAME} {GUI_LONG_NAME}',
            style={
                'fontWeight': 'bold',
                'textAlign': 'center',
                'marginTop': '20px',
                'marginBottom': '30px',
            }),
    ])
