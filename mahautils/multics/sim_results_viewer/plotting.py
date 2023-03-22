"""Code for the components of the simulation results viewer that generate
the data graph.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore


def graph():
    """Creates the main plot where simulation results are displayed"""
    default_height_percent = 90

    contents = dash.dcc.Graph(
        id='plotly-graph',
        style={
            'height': f'{default_height_percent}vh',
        },
    )

    return contents
