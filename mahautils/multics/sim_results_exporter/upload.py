"""Page elements for uploading simulation results files."""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore


def upload_section():
    """Page elements to upload simulation results file"""
    return dash.html.Div([
        dash.html.H3('Step 1: Upload Simulation Results File'),
        dbc.Spinner(
            dash.dcc.Upload(
                'Drag and Drop or Click to Browse',
                id='upload-data',
                style={
                    'width': '30%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'marginTop': '20px',
                    'marginLeft': '0px',
                    'marginRight': '0px',
                },
            ),
            delay_show=200,
        ),
        dash.html.Div(
            dash.html.P(
                'Error: Unable to load simulation results file',
                id='upload-error-message',
                style={'color': 'red'},
            ),
            hidden=True,
            id='upload-error',
            style={'marginTop': '10px'},
        )
    ])
