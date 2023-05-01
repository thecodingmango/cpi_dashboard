# Import libraries required for building the dashboard
import pandas as pd
import datetime
from dash import html
from dash import dcc
from dash.dependencies import Input, Output


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

    range_picker = html.Div(
        children=[
            dcc.DatePickerRange(
                id='date_range',
                className='date_picker_container',
                min_date_allowed=data['year_month'].min(),
                max_date_allowed=data['year_month'].max(),
                start_date=data['year_month'].min(),
                end_date=data['year_month'].max()
            )
        ]
    )

    return range_picker


def drop_down():

    menu = dcc.Dropdown(
        id='drop_down_menu',
        className='drop_down_menu',
        options=[
            {'label': 'Commodity Prices', 'value': 'Commodity Prices'},
            {'label': 'Crude Oil Spot Price', 'value': 'Crude Oil Spot Price'},
            {'label': 'Crude Oil Production', 'value': 'Crude Oil Production'},
            {'label': 'Crude Oil Consumption', 'value': 'Crude Oil Consumption'}
        ],
        value='Commodity Prices'
    )

    return menu


def cpi_line_graph():

    line_graph = dcc.Graph(
        id='cpi_chart',
        className='card',
        config={'displayModeBar': True},
    )

    return line_graph


def line_graph():

    line_graph = dcc.Graph(
        id='line_chart',
        className='card',
        config={'displayModeBar': True}
    )

    return line_graph

