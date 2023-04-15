"""Panel tab for configuring x-axis plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import (
    SIM_RESULTS_DICT_T,
    SIM_VAR_DROPDOWN_OPTION_HEIGHT,
    TAB_BAR_PADDING,
    UI_DESCRIPTION_MARGIN_BELOW,
)
from mahautils.multics.sim_results_viewer.store import default_plot_config_x
from mahautils.multics.sim_results_viewer.ui_elements import tick_range_step


def plot_settings_x():
    """Creates the configuration panel tab with settings for the x-axis"""
    return [
        dash.html.Div(
            render_x_settings(default_plot_config_x, {}),
            id='plot-config-x-settings',
            style={'marginTop': TAB_BAR_PADDING},
        ),
    ]


def render_x_settings(config_x: dict, sim_results_files: SIM_RESULTS_DICT_T):
    """Generates the UI elements that allow the user to configure x-axis
    plot settings"""
    # Identify list of simulation results variables that are present and have
    # the same description in all loaded simulation results files
    variable_options = {}

    for i, (file_name, sim_results) in enumerate(sim_results_files.items()):
        if i == 0:
            key0 = file_name
            variable_options = {
                var: {
                    'label': f'{var} — {sim_results.get_description(var)}',
                    'value': var,
                }
                for var in sim_results.variables
            }
        else:
            for var in list(variable_options.keys()):
                # If a given variable is not present in all simulation results
                # files or it has different descriptions, remove it from the
                # list of valid options
                if var not in sim_results.variables:
                    del variable_options[var]
                elif (
                    sim_results_files[key0].get_description(var)
                    != sim_results.get_description(var)
                ):
                    del variable_options[var]

    return [
        dash.html.H4('Data'),
        dash.html.Hr(),
        dash.html.H5('Simulation Results Variable'),
        dash.html.P(
            ('Sets the simulation results variable to be plotted '
             'on the horizontal axis for all simulation results'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dash.html.Div(dbc.Row([
            dbc.Col(
                dash.html.H6('Variable'),
                width=2,
            ),
            dbc.Col(
                dash.dcc.Dropdown(
                    options=list(variable_options.values()),
                    value=config_x['variable'],
                    id={'component': 'plot-config', 'tab': 'x',
                        'field': 'variable'},
                    clearable=True,
                    multi=False,
                    optionHeight=SIM_VAR_DROPDOWN_OPTION_HEIGHT,
                ),
                width=10,
            ),
        ]), style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW}),
        dbc.Row([
            dbc.Col(
                dash.html.H6('Units'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(
                    debounce=True,
                    value=config_x['units'],
                    id={'component': 'plot-config', 'tab': 'x',
                        'field': 'units'},
                    style={'width': 150},
                    disabled=(config_x['variable'] is None),
                ),
                width=10,
            ),
        ]),
        dbc.Alert(
            [
                dash.html.H5([
                    dash.html.I(className='fa fa-exclamation-triangle'),
                    ' WARNING',
                ]),
                dash.html.Hr(),
                dash.html.P('The plot will not be updated until you have '
                            'selected both a simulation results variable AND '
                            'units for the x-axis'),
            ],
            color='danger',
            style={
                'width': '95%',
                'marginTop': '10px',
                'marginLeft': '10px',
                'marginRight': '10px',
            },
            is_open=(
                config_x['variable'] in (None, '')
                or config_x['units'] in (None, '')
            ),
            dismissable=False,
        ),
        dash.html.Br(),
        dash.html.Br(),
        dash.html.H4('Formatting'),
        dash.html.Hr(),
        dash.html.H5('Axis Title'),
        dbc.Input(
            debounce=True,
            id={'component': 'plot-config', 'tab': 'x',
                'field': 'title'},
            placeholder='Enter a title for the x-axis...',
            value=config_x['axis_title'],
        ),
        dash.html.Br(),
        tick_range_step(
            range_min_id={'component': 'plot-config', 'tab': 'x',
                          'field': 'xmin'},
            range_max_id={'component': 'plot-config', 'tab': 'x',
                          'field': 'xmax'},
            tick_spacing_id={'component': 'plot-config', 'tab': 'x',
                             'field': 'tick_spacing'},
            range_min_val=config_x['xmin'],
            range_max_val=config_x['xmax'],
            tick_spacing_val=config_x['tick_spacing'],
        ),
    ]
