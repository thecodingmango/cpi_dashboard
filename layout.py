import pandas as pd
import dash
from dash import dash_table
from layout_functions.layout_functions import *
from data.data_update.fetch_data import *
from datetime import datetime, timedelta

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

# Building the layout here
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
                        
                        Retrieving Data using EIA API: [How to Retrieve Data from the EIA Website](https://thecodingmango.com/updating-data-for-cpi-dashboard-part-2/)
                        
                        Retrieving Data using BLS API: [How to Retrieve Data from the BLS Website](https://thecodingmango.com/updating-data-for-cpi-dashboard-part-1/)
                    '''),
                        html.Hr(),
                        # Table for Descriptive Statistics
                        dash_table.DataTable(
                            id='descriptive_stats_table',
                            columns=[
                                {"name": "Metric", "id": "metric"},
                                {"name": "This Month", "id": "this_month"},
                                {"name": "Last Month", "id": "last_month"},
                                {"name": "1 Year Ago", "id": "one_year"},
                                {"name": "5 Years Ago", "id": "five_years"}
                            ],
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': '#444', 'fontWeight': 'bold', 'color': 'white'},
                            style_cell={'textAlign': 'center', 'padding': '5px', 'backgroundColor': '#333', 'color': 'white'},
                        )

                    ]
                ),
                html.Div(
                    id='main',
                    className='main',
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
                            id = 'charts_container',
                            className='cpi_chart_container'
                        )
                    ]
                )
            ],
            className='content_wrapper'
        )
    ],
    className='wrapper'
)


# App callback used for updating the values in the function
@app.callback(
    [
        Output('charts_container', 'children'),
        Output('descriptive_stats_table', 'data')
    ],
    [
        Input('start_month', 'value'),
        Input('end_month', 'value'),
        Input('drop_down_menu', 'value')
    ]
)
def update_chart(start_date, end_date, value):

    filters_date_bls = ((bls_data['year_month'] >= start_date) & (bls_data['year_month'] <= end_date))
    filtered_data_bls = bls_data.loc[filters_date_bls, :]

    eia_filter = ((eia_petroleum_spot['year_month'] >= start_date) &
                   (eia_petroleum_spot['year_month'] <= end_date))
    eia_petro_price = eia_petroleum_spot.loc[eia_filter, :]

    eia_filter_consumption = ((eia_api_crude_consumption['year_month'] >= start_date) &
                              (eia_api_crude_consumption['year_month'] <= end_date))
    eia_oil_consumption = eia_api_crude_consumption.loc[eia_filter_consumption, :]

    eia_filter_production = ((eia_api_crude_production['year_month'] >= start_date) &
                                 (eia_api_crude_production['year_month'] <= end_date))
    eia_oil_production = eia_api_crude_production.loc[eia_filter_production, :]



    def get_summary(df, column):
        if column not in df:
            return None

        end = bls_data['year_month'].max()
        end = datetime.strptime(end, '%Y-%m')

        df = df.sort_values(by='year_month')

        # Calculates the value for present and past
        curr_month = df[column].iloc[-1] if not df.empty else None
        prev_month = df[column].iloc[-2] if len(df) > 1 else None
        one_year = df[df['year_month'] == (end - timedelta(days=365)).strftime('%Y-%m')][column].values
        one_year = one_year[0] if len(one_year) > 0 else None
        five_year = df[df['year_month'] == (end - timedelta(days=365*5)).strftime('%Y-%m')][column].values
        five_year = five_year[0] if len(five_year) > 0 else None

        return {
            'this_month': f"{curr_month:.2f}",
            'last_month': f"{prev_month:.2f}",
            'one_year': f"{one_year:.2f}",
            'five_years': f"{five_year:.2f}"
        }

    table_data = [
        {'metric': 'CPI Values', **get_summary(bls_data, 'cpi_values')},
        *[{'metric': item, **get_summary(bls_data, item)} for item in filtered_data_bls.columns[1:-2]],
        *[{'metric': item, **get_summary(eia_petroleum_spot, item)} for item in eia_petro_price.columns[1:-1]]
    ]

    if value == 'Commodity Prices':

        fig_cpi = go.Figure()
        fig_cpi = line_graph(fig_cpi, filtered_data_bls, 'year_month', 'cpi_values',
                             'CPI Values Since ' + start_date, 'Year', 'CPI Values')

        fig_commodity = go.Figure()
        for item in filtered_data_bls.columns[1:-2]:
            line_graph(fig_commodity, filtered_data_bls, 'year_month', item,
                       'Commodity Price Since ' + start_date, 'Year', 'Price in USD')

        fig_crude_price = go.Figure()
        for item in eia_petro_price.columns[1:-1]:
            line_graph(fig_crude_price, eia_petro_price, 'year_month', item, 'Crude Oil Spot Price Since ' + start_date,
                       'Year','Price in USD')

        fig_crude_production = go.Figure()
        for item in eia_oil_production.columns[1:-1]:
            line_graph(fig_crude_production, eia_oil_production, 'year_month', item,
                       'Annual Crude Oil Produced by Country','Year',
                       'Million(s) Barrel')

        fig_crude_consumption = go.Figure()
        for item in eia_oil_consumption.columns[1:-1]:
            line_graph(fig_crude_consumption, eia_oil_consumption, 'year_month', item,
                       'Annual Crude Oil Consumed by Country','Year',
                       'Million(s) Barrel')

        chart_layout = [
            html.Div(dcc.Graph(figure=fig_cpi, className='full_card')),
            html.Div(children=[dcc.Graph(figure=fig_commodity, className='half_card'),
                       dcc.Graph(figure=fig_crude_price, className='half_card')]),
            html.Div(children=[dcc.Graph(figure=fig_crude_production, className='half_card'),
                               dcc.Graph(figure=fig_crude_consumption, className='half_card')]),

        ]

        return [chart_layout, table_data]


    elif value == 'Crude Oil Spot Price':
        pass

    elif value == 'Crude Oil Production':
        pass

    elif value == 'Crude Oil Consumption':
        pass

