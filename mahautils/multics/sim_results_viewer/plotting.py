"""Code for the components of the simulation results viewer that generate
the data graph.
"""

import itertools
from typing import Any, Dict, List

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                        # type: ignore
import plotly.graph_objects as go  # type: ignore

from mahautils.multics.sim_results_viewer.constants import SIM_RESULTS_DICT_T

uirevision_counter = itertools.count(2)


def graph():
    """Creates the main plot where simulation results are displayed"""
    default_height_percent = 90

    contents = dash.dcc.Loading(
        dash.dcc.Graph(
            id='plotly-graph',
            figure={},
            style={
                'height': f'{default_height_percent}vh',
            },
        ),
    )

    return contents


def update_graph(config_general: dict, config_x: dict, config_y: dict,
                 sim_results_files: SIM_RESULTS_DICT_T):
    """Generates the plot of simulation results based on the current
    user-specified configuration options"""
    figure = go.Figure()
    append_units = bool(config_general['append_units'])

    ## Plot simulation results data ##
    y_axes: List[Dict[str, Any]] = config_y['axes']
    num_active_axes = sum(x['enabled'] for x in y_axes)
    width_per_axis = float(config_y['width_per_axis'])

    if (
        len(y_axes) > 0
        and (None not in (config_x['variable'], config_x['units']))
    ):
        # Settings for x-axis
        if (axis_title := config_x['axis_title']) not in (None, ''):
            if append_units:
                axis_title += f' [{config_x["units"]}]'

            figure.update_layout(xaxis={'title': axis_title, 'color': 'black'})

        figure.update_layout(
            xaxis={'domain': [width_per_axis*(num_active_axes-1), 1]})

        if (dtick := config_x['tick_spacing']) != 'auto':
            figure.update_xaxes(dtick=dtick)

        # Settings for y-axes
        y_axis_data: Dict[str, Any]
        i = 0
        for y_axis_data in y_axes:
            if not y_axis_data['enabled']:
                continue

            plot_data = {'yaxis': f'y{i+1 if i > 0 else ""}'}

            for trace in y_axis_data['traces']:
                try:
                    sim_results = sim_results_files[trace['file']]
                except KeyError as exception:
                    exception.args = (
                        'Unable to find simulation results file named '
                        f'"{exception.args[0]}" -- have you uploaded this file '
                        'on the "Data Files" tab?',)
                    raise

                plot_data['name'] = (
                    f'{trace["name"]}'
                    + (f' [{trace["units"]}]' if append_units else '')
                )

                plot_data['x'] = sim_results.get_data(config_x['variable'],
                                                      config_x['units'])
                plot_data['y'] = sim_results.get_data(trace['variable'],
                                                      trace['units'])
                plot_data['line'] = trace['style']

                figure.add_trace(go.Scatter(**plot_data))

            if i == 0:
                figure.update_layout(
                    yaxis={
                        'title': str(y_axis_data['axis_title']),
                        'color': str(y_axis_data.get('color', 'black')),
                    },
                )
            else:
                figure.update_layout(**{
                    f'yaxis{i+1}': {
                        'title': str(y_axis_data['axis_title']),
                        'anchor': 'free',
                        'overlaying': 'y',
                        'side': 'left',
                        'position': (width_per_axis * i) - width_per_axis,
                        'color': str(y_axis_data.get('color', 'black')),
                    }
                })

            i += 1

    ## Plot formatting settings ##
    figure.update_layout(margin={'t': 7.5, 'r': 10})

    default_axes_settings = {
        # Border around plot
        'showline': True, 'linewidth': 1, 'linecolor': 'black', 'mirror': True,

        # Settings for x=0 and y=0 axes
        'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': 'black',

        # Settings for gridlines
        'showgrid': True, 'gridwidth': 1, 'gridcolor': '#d2d2d2',
    }
    figure.update_xaxes(**default_axes_settings)
    figure.update_yaxes(**default_axes_settings)

    # Remove y=0 zero line (can be easily confused with simulation results data)
    figure.update_yaxes(zeroline=False)

    figure.update_layout(
        plot_bgcolor=config_general['background_color'])

    # Plot title
    if config_general['title'] not in (None, ''):
        figure.update_layout(
            title={
                'text': f'<b>{config_general["title"]}</b>',
                'x': 0.5,
                'xanchor': 'center',
            },
            title_font_color='black',
            margin={'t': 40},
        )

    # Gridlines
    figure.update_xaxes(showgrid=bool(config_general['grid_x']))
    figure.update_yaxes(showgrid=bool(config_general['grid_y']))

    # Cursor hover settings
    figure.update_layout(
        hovermode=config_general['hovermode'],
        hoverlabel={'namelength': -1},  # prevents truncating hover text
    )

    # Whether to change settings like zoom and which legend entries are active
    # when figure is updated by Dash
    if config_general['freeze_uirevision']:
        # For the plot UI state not to be updated, "uirevision" must be set to
        # a constant, nonzero value (plotly/graphing-library-docs#116)
        figure.update_layout(uirevision=1)
    else:
        figure.update_layout(uirevision=next(uirevision_counter))

    return figure
