# Import libraries required for building the dashboard
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
