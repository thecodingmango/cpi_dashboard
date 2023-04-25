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
        className='menu',
        children=[
            html.Div(
                children='Date Range',
                className='menu-title'),
            dcc.DatePickerRange(
                id='date_range',
                min_date_allowed=data['year_month'].min(),
                max_date_allowed=data['year_month'].max(),
                start_date=data['year_month'].min(),
                end_date=data['year_month'].max()
            )
        ]
    )

    return range_picker


def line_chart():

    line_graph = dcc.Graph(
        id='cpi_graph',
        className='card',
        config={'displayModeBar': True}
    )

    return line_graph

