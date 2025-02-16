# Import libraries required for building the dashboard
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go


def header():
    header_layout = html.Div(
        id='header',
        className='header',
        children=[
            html.Div(
                children=[
                    html.H1(
                        children='CPI DashBoard',
                        className='header-title'
                    ),
                    html.H2(children='Visualizing CPI and Different Commodity',
                            className='header-description')
                ],
            )
        ]
    )

    return header_layout

def date_picker(data):
    # Convert 'year_month' to a unique sorted list for dropdown
    month_options = [{'label': ym, 'value': ym} for ym in sorted(data['year_month'].unique())]

    range_picker = html.Div(
        children=[
            html.Label("Select Start Month:"),
            dcc.Dropdown(
                id='start_month',
                options=month_options,
                value=data['year_month'].min(),  # Default to earliest available month
                clearable=False,
            ),

            html.Label("Select End Month:"),
            dcc.Dropdown(
                id='end_month',
                options=month_options,
                value=data['year_month'].max(),  # Default to latest available month
                clearable=False,
            ),
        ],
        className='date_picker_container'
    )

    return range_picker


def drop_down():
    menu = dcc.Dropdown(
        id='drop_down_menu',
        className='drop_down_menu',
        options=[
            {'label': 'Commodity Trends', 'value': 'Commodity Prices'},
            {'label': 'Crude Oil Spot Price', 'value': 'Crude Oil Spot Price'},
            {'label': 'Crude Oil Production', 'value': 'Crude Oil Production'},
            {'label': 'Crude Oil Consumption', 'value': 'Crude Oil Consumption'}
        ],
        value='Commodity Prices',
        clearable=False
    )

    return menu

def line_graph(fig, data,x, y, title = None, x_axis=None, y_axis=None):

    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y],
        mode='lines',
        name=y
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        showlegend=True,
        legend=dict(title="Legend"),
        plot_bgcolor = '#252a3b',  # Dark background
        paper_bgcolor = '#1E1E2F',  # Dark paper background
        font = dict(color='white')
    )

    return fig



