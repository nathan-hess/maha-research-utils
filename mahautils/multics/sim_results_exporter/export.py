"""Page elements for saving simulation results data to a CSV file."""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore


def export_area():
    """Page elements to save simulation results data to a CSV file"""
    return dash.html.Div(
        [
            dash.html.H3('Step 2: Export CSV File',
                         style={'marginBottom': '10px'}),
            dash.html.P(
                'Click the button below to save your simulation results '
                'data to a CSV file'
            ),
            dbc.Button('Export CSV', id='export-button'),
            dash.dcc.Download(id='csv-download'),
            dash.html.H5(
                'Customize Export',
                style={'marginTop': '20px'},
            ),
            dash.html.Div(id='export-options-section'),
        ],
        hidden=True,
        id='export-section',
        style={
            'marginTop': '30px',
        },
    )
