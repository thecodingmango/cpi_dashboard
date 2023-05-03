import dash
from layout_functions.layout_functions import *
from data.data_update.fetch_data import *

# Using apis to import data
'''
data_api = Updater()

bls_data = data_api.retrieve_data_bls(config.bls_series, config.bls_series_name)

eia_petroleum_spot = data_api.retrieve_data_eia(config.eia_petroleum_price,
                                                config.eia_petroleum_name,
                                                ['value'])

eia_api_crude_production = data_api.retrieve_data_eia(config.eia_crude_production,
                                                      config.eia_crude_production_name,
                                                      ['value'])
eia_api_crude_consumption = data_api.retrieve_data_eia(config.eia_crude_consumption,
                                                       config.eia_crude_consumption_name,
                                                       ['value'])
'''

bls_data = pd.read_csv('./data/bls_data.csv')
eia_petroleum_spot = pd.read_csv('./data/eia_crude_price.csv')
eia_api_crude_production = pd.read_csv('./data/eia_crude_production.csv')
eia_api_crude_consumption = pd.read_csv('./data/eia_crude_consumption.csv')

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
app.title = 'CPI Dashboard'

app.layout = html.Div(
    children=[
        html.Div(
            header()
        ),
        html.Div(
            children=[
                html.Div(
                    id='sidebar',
                    className='sidebar',
                    children=[
                        dcc.Markdown('''
                        ## About this Project
                        This project is a dashboard for visualizing the CPI levels and different
                        prices. 
                        
                        Full Code: [Github](https://github.com/thecodingmango/cpi_dashboard)
                        
                        Website: [TheCodingMango](https://thecodingmango.com/)
                    ''')
                    ]
                ),
                html.Div(
                    id='main',
                    className='card',
                    children=[
                        # Date picker section
                        html.Div(
                            className='main_top',
                            children=[
                                date_picker(bls_data),
                                drop_down()
                            ]
                        ),

                        # CPI chart
                        html.Div(
                            className='cpi_chart_container',
                            children=[cpi_line_graph()]

                        ),

                        # Other Charts
                        html.Div(
                            className='line_chart_container',
                            children=[line_graph()]

                        )
                    ]
                )
            ],
            className='content_wrapper'
        )
    ],
    className='wrapper'
)

@app.callback(
    [Output('cpi_chart', 'figure'),
     Output('line_chart', 'figure')],
    [Input('date_range', 'start_date'),
     Input('date_range', 'end_date'),
     Input('drop_down_menu', 'value')]
)
def update_chart(start_date, end_date, value):
    temp_list = []
    filters_date_bls = ((bls_data['year_month'] >= start_date) & (bls_data['year_month'] <= end_date))
    filtered_data_bls = bls_data.loc[filters_date_bls, :]

    cpi_chart = {
        'data': [
            {
                'x': filtered_data_bls['year_month'],
                'y': filtered_data_bls['cpi_values'],
                'type': 'lines',
                'name': 'CPI_Values'
            }
        ],
        'layout': {
            'title': {
                'text': 'CPI Values Since' + ' ' + start_date,
                'x': 'center'
            },
            'xaxis': {
                'title': 'Year',
            },
            'yaxis': {
                'title': {'text': 'CPI Values',
                          'font-size': 'bold'
                          },
                'ticksuffix': '%',
                'font': 'bold'
            },
            'height': 400
        }
    }

    if value == 'Commodity Prices':

        for series in filtered_data_bls.columns[1:-2]:
            temp_list += [
                {'x': filtered_data_bls['year_month'], 'y': filtered_data_bls[series],
                 'type': 'lines',
                 'name': series
                 }
            ]

        line_chart = {
            'data':
                temp_list
            ,
            'layout': {
                'title': {
                    'text': 'Comparison of Different Commodity Prices' + ' Since ' + start_date,
                    'x': 'center'
                },
                'xaxis': {
                    'title': ' Year'
                },
                'yaxis': {
                    'title': ' Prices in USD'
                },
                'height': 400
            }
        }

        return [cpi_chart, line_chart]

    elif value == 'Crude Oil Spot Price':
        eia_filter = ((eia_petroleum_spot['year_month'] >= start_date) &
                      (eia_petroleum_spot['year_month'] <= end_date))

        eia_petro_price = eia_petroleum_spot.loc[eia_filter, :]

        for series in eia_petro_price.columns[1:-1]:
            temp_list += [
                {
                    'x': eia_petro_price['year_month'],
                    'y': eia_petro_price[series],
                    'type': 'lines',
                    'name': series
                }
            ]

        line_chart = {
            'data':
                temp_list,
            'layout': {
                'title': {
                    'text': 'Comparison of Crude Oil Spot Prices' + ' Since ' + start_date,
                    'x': 'center'
                },
                'xaxis': {
                    'title': ' Year'
                },
                'yaxis': {
                    'title': ' Prices USD'
                },
                'height': 400
            }
        }

        return [cpi_chart, line_chart]

    elif value == 'Crude Oil Production':
        eia_filter_production = ((eia_api_crude_production['year_month'] >= start_date) &
                                 (eia_api_crude_production['year_month'] <= end_date))

        eia_oil_production = eia_api_crude_production.loc[eia_filter_production, :]

        for series in eia_oil_production.columns[1:-1]:
            temp_list += [
                {
                    'x': eia_oil_production['year_month'],
                    'y': eia_oil_production[series],
                    'type': 'lines',
                    'name': series
                }
            ]

        line_chart = {
            'data':
                temp_list,
            'layout': {
                'title': {
                    'text': 'Comparison of Different Oil Production Level by Country' + ' Since ' + start_date,
                    'x': 'center'
                },
                'xaxis': {
                    'title': ' Year'
                },
                'yaxis': {
                    'title': ' Million of Barrel (s)'
                },
                'height': 400
            }
        }

        return [cpi_chart, line_chart]

    elif value == 'Crude Oil Consumption':

        eia_filter_consumption = ((eia_api_crude_consumption['year_month'] >= start_date) &

                                  (eia_api_crude_consumption['year_month'] <= end_date))

        eia_oil_consumption = eia_api_crude_production.loc[eia_filter_consumption, :]

        for series in eia_oil_consumption.columns[1:-1]:
            temp_list += [
                {
                    'x': eia_oil_consumption['year_month'],
                    'y': eia_oil_consumption[series],
                    'type': 'lines',
                    'name': series
                }
            ]

        line_chart = {
            'data':
                temp_list,
            'layout': {
                'title': {
                    'text': 'Comparison of Different Oil Consumption Level by Country' + ' Since ' + start_date,
                    'x': 'center'
                },
                'xaxis': {
                    'title': ' Year'
                },
                'yaxis': {
                    'title': ' Million of Barrel (s)'
                },
                'height': 400
            }
        }

        return [cpi_chart, line_chart]
