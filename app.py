"""
This is a module for building the dashboard inspired from:
https://realpython.com/python-dash/#get-started-with-dash-in-python
"""

# Importing libraries
import datetime
import dash
import datetime
from datetime import date
from dash import dcc
from dash import Output, Input
from dash import html
import pandas as pd

CPI = pd.read_csv('Data/CPI_data_1997_to_2022.csv')
Energy_Price = pd.read_csv('Data/Energy_Prices.csv')
Oil_Production = pd.read_csv('Data/International_PetroleumProduction_Consumption_and_Inventories.csv')

# Merge all data
all_data = CPI.merge(Energy_Price, how='left', on='DATE').merge(Oil_Production, how='left', on='DATE')
all_data['DATE'] = pd.to_datetime(all_data['DATE'], format='%Y-%m-%d')
all_data['DATE'] = [datetime.datetime.strftime(date, '%Y-%m-%d') for date in all_data['DATE']]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }
]

# Initialize the dash class
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Crude Oil to CPI Analysis'

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children='CPI Analysis',
                    className='header-title'
                ),
                html.P(children='Dash board for visualizing CPI data '
                                ' compared to oil prices',
                       className='header-description')
            ],
            className='header',
        ),
        html.Div(
            children=[
                html.Div(
                    children='Date',
                    className='menu-title'),
                dcc.DatePickerRange(
                    id='date_range',
                    min_date_allowed=all_data.DATE.min(),
                    max_date_allowed=all_data.DATE.max(),
                    start_date=all_data.DATE.min(),
                    end_date=all_data.DATE.max()
                )
            ],
            className='menu'
        ),
        html.Div(
            children=dcc.Graph(
                id='cpi_chart',
                config={'displayModeBar': True}

            ), style={'display': 'inline-block'}, className='card'
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='fuel_price',
                        config={'displayModeBar': True}
                    ),
                    style={'display': 'inline-block'}, className='card'
                ),
                html.Div(
                    children=dcc.Graph(
                        id='crude_price',
                        config={'displayModeBar': True}
                    ),
                    style={'display': 'inline-block'}, className='card'
                )
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='production',
                        config={'displayModeBar': True}

                    ), style={'display': 'inline-block'}, className='card'
                ),
                html.Div(
                    children=dcc.Graph(
                        id='consumption',
                        config={'displayModeBar': True}
                    ),
                    style={'display': 'inline-block'}, className='card'
                )
            ]
        ),
        html.Div(
            children=dcc.Graph(
                id='production_consumption',
                config={'displayModeBar': True}
            ), className='card'
        )
    ]
)


@app.callback(
    [Output('cpi_chart', 'figure'),
     Output('fuel_price', 'figure'),
     Output('crude_price', 'figure'),
     Output('production', 'figure'),
     Output('consumption', 'figure'),
     Output('production_consumption', 'figure')],
    [Input('date_range', 'start_date'),
     Input('date_range', 'end_date')]
)
def update_chart(start_date, end_date):
    filters = ((all_data.DATE >= start_date) & (all_data.DATE <= end_date))
    filtered_data = all_data.loc[filters, :]

    cpi_chart = {
        'data': [
            {
                'x': filtered_data['DATE'],
                'y': filtered_data['VALUE'],
                'type': 'lines'
            }
        ],
        'layout': {
            'title':
                {'text': 'CPI Values Since 1997',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'ticksuffix': '%', 'fixed_range': True},
            'width': 1900
        }
    }

    fuel_price = {
        'data': [
            {'x': filtered_data['DATE'], 'y': filtered_data['Gasoline_Price'], 'type': 'lines',
             'name': 'Gasoline Price'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Diesel_Fuel_Price'], 'type': 'lines',
             'name': 'Diesel Price'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Fuel_Oil_Price'], 'type': 'lines', 'name': 'Fuel Price'}
        ],
        'layout': {
            'title':
                {'text': 'Gasoline, Diesel, Fuel Prices Since 1997',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'tickprefix': '$', 'fixed_range': True},
            'width': 950
        }
    }

    crude_price = {
        'data': [
            {'x': filtered_data['DATE'], 'y': filtered_data['West_Texas_Crude_Oil_Spot_Price'], 'type': 'lines',
             'name': 'West Texas Crude Price'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Brent_Crude_Oil_Spot_Price'], 'type': 'lines',
             'name': 'Brent Crude Price'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Imported_Crude_Oil_Average_Price'], 'type': 'lines',
             'name': 'Imported Crude Price'}
        ],
        'layout': {
            'title':
                {'text': 'Comparison of Different Crude Oil Prices',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'tickprefix': '$', 'fixed_range': True},
            'width': 950
        }
    }
    production = {
        'data': [
            {'x': filtered_data['DATE'], 'y': filtered_data['US_Production'], 'type': 'lines',
             'name': 'US Oil Production'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Canada_Production'], 'type': 'lines',
             'name': 'Canada Oil Production'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Mexico_Production'], 'type': 'lines',
             'name': 'Mexico Oil Production'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Eurasia_Production'], 'type': 'lines',
             'name': 'Eurasia Oil Production'}
        ],
        'layout': {
            'title':
                {'text': 'Comparison of Different Crude Oil Prices',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'ticksuffix': ' Million Barrels', 'fixed_range': True},
            'margin': {'l': 125},
            'width': 950
        }
    }
    consumption = {
        'data': [
            {'x': filtered_data['DATE'], 'y': filtered_data['US_Consumption'], 'type': 'lines',
             'name': 'US Oil Consumption'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Canada_Consumption'], 'type': 'lines',
             'name': 'Canada Oil Consumption'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Europe_Consumption'], 'type': 'lines',
             'name': 'Mexico Oil Consumption'},
        ],
        'layout': {
            'title':
                {'text': 'Comparison of Different Crude Oil Prices',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'ticksuffix': ' Million Barrels', 'fixed_range': True},
            'margin': {'l': 125},
            'width': 950
        }
    }
    production_consumption = {
        'data': [
            {'x': filtered_data['DATE'], 'y': filtered_data['Total_World_Consumption'], 'type': 'lines',
             'name': 'Total World Consumption/Month'},
            {'x': filtered_data['DATE'], 'y': filtered_data['Total_World_Production'], 'type': 'lines',
             'name': 'Total World Production/Month'},
        ],
        'layout': {
            'title':
                {'text': 'Comparison of Total World Oil Production and Total World Oil Consumption',
                 'x': 0.05},
            'xaxis': {'fixed_range': True},
            'yaxis': {'ticksuffix': ' Million Barrels', 'fixed_range': True},
            'margin': {'l': 125}
        }
    }

    return [cpi_chart, fuel_price, crude_price, production, consumption, production_consumption]


if __name__ == "__main__":
    app.run_server()
