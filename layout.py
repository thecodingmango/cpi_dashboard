import dash
from dash import dash_table
from layout_functions.layout_functions import *
from datetime import datetime, timedelta
from dash.dependencies import Input, Output

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

# Reading data due to it is faster to load this than computing it everytime for Render
bls_data = pd.read_csv('./data/bls_food.csv')
bls_gas = pd.read_csv('./data/bls_gas_price.csv')
eia_petroleum_spot = pd.read_csv('./data/eia_crude_price.csv')
eia_api_crude_production = pd.read_csv('./data/eia_crude_production.csv')
eia_api_crude_consumption = pd.read_csv('./data/eia_crude_consumption.csv')
eia_emission = pd.read_csv('./data/eia_emission.csv')
eia_emission.iloc[:, 1] = eia_emission.iloc[:, 1] / 30
merged_df = bls_data.drop('Unnamed: 0', axis=1).merge(
    bls_gas.drop('Unnamed: 0', axis=1), how='left', on='year_month')
merged_df = merged_df.merge(eia_petroleum_spot.drop('Unnamed: 0', axis=1), how='left', on='year_month')
forecast_data = pd.read_csv('./data/forecast_data.csv')

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }
]

# Initialize the dash class
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
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
                        dcc.Markdown(
                            '''
                        ## About this Project
                        This project is a dashboard for visualizing the CPI levels and different
                        prices. 
                        
                        Full Code: [Github](https://github.com/thecodingmango/cpi_dashboard)
                        
                        Website: [TheCodingMango](https://thecodingmango.com/)
                        
                        Retrieving Data using EIA API: [How to Retrieve Data from the EIA Website]
                        (https://thecodingmango.com/updating-data-for-cpi-dashboard-part-2/)
                        
                        Retrieving Data using BLS API: [How to Retrieve Data from the BLS Website]
                        (https://thecodingmango.com/updating-data-for-cpi-dashboard-part-1/)
                    '''
                        ),
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
                            style_table={
                                'overflowX': 'auto',
                                'backgroundColor': '#252a3b'
                            },
                            style_header={
                                'backgroundColor': '#1E1E2F',
                                'fontWeight': 'bold',
                                'color': 'white'
                            },
                            style_cell={
                                'textAlign': 'center',
                                'padding': '12px',
                                'backgroundColor': '#252a3a',
                                'color': 'white',
                                'border': '2px solid #444'
                            }
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
                                drop_down(),
                            ]
                        ),


                        # CPI chart
                        html.Div(
                            dcc.Loading(type='circle', children=[
                                html.Div(
                                    id='charts_container',
                                    className='cpi_chart_container')
                            ])
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
        Output('descriptive_stats_table', 'data'),
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

    filtered_bls_gas = bls_gas.loc[filters_date_bls, :]

    filtered_merged_data = merged_df.loc[filters_date_bls, :]

    eia_filter = ((eia_petroleum_spot['year_month'] >= start_date) &
                  (eia_petroleum_spot['year_month'] <= end_date))
    eia_petro_price = eia_petroleum_spot.loc[eia_filter, :]

    eia_filter_consumption = ((eia_api_crude_consumption['year_month'] >= start_date) &
                              (eia_api_crude_consumption['year_month'] <= end_date))
    eia_oil_consumption = eia_api_crude_consumption.loc[eia_filter_consumption, :]

    eia_filter_production = ((eia_api_crude_production['year_month'] >= start_date) &
                             (eia_api_crude_production['year_month'] <= end_date))
    eia_oil_production = eia_api_crude_production.loc[eia_filter_production, :]

    chart_layout = []

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
        five_year = df[df['year_month'] == (end - timedelta(days=365 * 5)).strftime('%Y-%m')][column].values
        five_year = five_year[0] if len(five_year) > 0 else None

        return {
            'this_month': f"{curr_month:.2f}",
            'last_month': f"{prev_month:.2f}",
            'one_year': f"{one_year:.2f}",
            'five_years': f"{five_year:.2f}"
        }

    table_data = [
        {'metric': 'CPI Values', **get_summary(bls_data, 'Cpi Values')},
        {'metric': 'PPI Values', **get_summary(bls_data, 'PPI Values')},
        {'metric': 'Unemployment Rate', **get_summary(bls_data, 'Unemployment')},
        *[{'metric': item, **get_summary(bls_data, item)} for item in filtered_data_bls.columns[1:-4]],
        *[{'metric': item, **get_summary(eia_petroleum_spot, item)} for item in eia_petro_price.columns[1:-1]]
    ]

    if value == 'Commodity Prices':

        chart_layout = []

        fig_cpi = go.Figure()
        dual_axis_line_chart(
            fig_cpi,
            filtered_data_bls,
            x='year_month',
            y1=['Cpi Values', 'PPI Values'],
            y2=['Unemployment'],
            title='CPI & PPI Compared to Unemployment Rate Since ' + start_date,
            x_axis='Year',
            y1_axis='Values (%)',
            y2_axis='Unemployment Rate (%)'
        )

        fig_commodity = go.Figure()
        for item in filtered_data_bls.columns[1:-4]:
            line_graph(
                fig_commodity,
                filtered_data_bls,
                'year_month',
                item,
                'Average Food Price Since ' + start_date, 'Year', 'Price in USD'
            )

        fig_crude_price = go.Figure()
        dual_axis_line_chart(
            fig_crude_price,
            eia_petro_price.merge(filtered_bls_gas, how='left', on='year_month'),
            x='year_month', y1=['UK Brent Prices', 'WTI Prices'], y2=['Unleaded Gasoline'],
            title='Spot Prices for Crude Oil and Unleaded Gasoline', x_axis='Year',
            y1_axis='Crude Spot Price in USD', y2_axis='Unleaded Gasoline in USD/Gallon'
        )

        fig_crude_production = go.Figure()
        for item in eia_oil_production.columns[1:-1]:
            line_graph(
                fig_crude_production,
                eia_oil_production,
                'year_month',
                item,
                'Crude Oil Production Trend by Region', 'Year',
                'Million Barrel/Day'
            )

        fig_crude_consumption = go.Figure()
        for item in eia_oil_consumption.columns[1:-1]:
            line_graph(
                fig_crude_consumption,
                eia_oil_consumption,
                'year_month',
                item,
                'Crude Oil Consumption Trend by Region',
                'Year',
                'Million Barrels/Day')

        chart_layout = [
            html.Div(
                children=[
                    dcc.Interval(),
                    html.Div(dcc.Graph(figure=fig_cpi, className='full_card')),
                    html.Div(children=[
                        dcc.Graph(figure=fig_commodity, className='half_card'),
                        dcc.Graph(figure=fig_crude_price, className='half_card')
                    ]),
                    html.Div(children=[
                        dcc.Graph(figure=fig_crude_production, className='half_card'),
                        dcc.Graph(figure=fig_crude_consumption, className='half_card')
                    ])
                ]

            )

        ]

    elif value == 'Energy Dependence':

        chart_layout = []

        fig_production = map_graph(
            eia_api_crude_production.copy(),
            'Million Barrels/Day',
            'Global Heatmap of Crude Oil Production Over Time'
        )
        fig_consumption = map_graph(
            eia_api_crude_consumption.copy(),
            'Million Barrels/Day',
            'Global Heatmap of Crude Oil Consumption Over Time'
        )

        fig_bar_prod = horizontal_bar_chart(
            eia_api_crude_production.copy(),
            'Million Barrels/Day',
            title='Bar Chart of Crude Oil Production',
            x_axis='Crude Oil Production Million Barrels/Day',
            y_axis='Region'
        )

        fig_bar_cons = horizontal_bar_chart(
            eia_api_crude_consumption.copy(),
            'Million Barrels/Day',
            title='Bar Chart of Crude Oil Consumption',
            x_axis='Crude Oil Production Million Barrels/Day',
            y_axis='Region'
        )

        fig_stacked_area_prod = go.Figure()
        fig_stacked_area_prod = stacked_area_graph(
            fig_stacked_area_prod,
            eia_api_crude_production.copy(),
            label='Average Crude Oil Production Million Barrel/Day',
        )
        fig_stacked_area_prod = stacked_area_graph(
            fig_stacked_area_prod,
            eia_api_crude_consumption.copy(),
            label='Average Crude Oil Consumption Million Barrel/Day',
        )
        fig_stacked_area_prod = stacked_area_graph(
            fig_stacked_area_prod,
            eia_emission.copy(),
            y='CO2 Emission from Petroleum Products',
            title='Yearly Oil Production, Consumption Compared to CO2 Emission from Petroleum Products',
            label='Average CO2 Emission Million Metric Tonnes/Day',
        )

        fig_cd_consumption = cd_chart(
            eia_api_crude_consumption.copy(),
            eia_emission.copy(),
            'Consumption',
            title='Global Oil Consumption & CO₂ Emissions Over Time',
            x_axis='Oil Consumption Million Barrels/Day',
            y_axis='CO₂ Emissions Million Tons/Day'
        )

        fig_cd_production = cd_chart(
            eia_api_crude_production.copy(),
            eia_emission.copy(),
            'Production',
            title='Global Oil Production & CO₂ Emissions Over Time',
            x_axis='Oil Production Million Barrels/Day',
            y_axis='CO₂ Emissions Million Tons/Day'
        )

        chart_layout = [
            html.Div(
                children=[
                    dcc.Interval(),
                    html.Div(dcc.Markdown('''
                                # Talk about this page
                                ''')),
                    html.Div(children=[
                        dcc.Graph(figure=fig_production, className='map'),
                        dcc.Graph(figure=fig_consumption, className='map')]
                    ),
                    html.Div(children=[
                        dcc.Graph(figure=fig_bar_prod, className='half_card'),
                        dcc.Graph(figure=fig_bar_cons, className='half_card')]
                    ),
                    html.Div(dcc.Graph(figure=fig_stacked_area_prod, className='full_card')),
                    html.Div(dcc.Graph(figure=fig_cd_production, className='full_card')),
                    html.Div(dcc.Graph(figure=fig_cd_consumption, className='full_card'))
                ]
            )

        ]

    elif value == 'Forecasting':

        chart_layout = [
            html.Div(
                dcc.Dropdown(
                    id='forecasting_dropdown',
                    options=[
                        {'label': 'Consumer Price Index', 'value': 'Cpi Values'},
                        {'label': 'Producer Price Index', 'value': 'PPI Values'},
                        {'label': 'Unemployment Rate', 'value': 'Unemployment'},
                        {'label': 'Unleaded Gasoline', 'value': 'Unleaded Gasoline'},
                        {'label': 'UK Brent Prices', 'value': 'UK Brent Prices'},
                        {'label': 'WTI Prices', 'value': 'WTI Prices'}
                    ],
                    value='Cpi Values',  # Default selection
                    clearable=False
                ),
                className='drop_down_menu_2'
            ),
            html.Div(dcc.Interval()),
            html.Div(id='forecasting_graph container'),  # Line chart
        ]

    else:  # Reserved for the future

        pass

    return [chart_layout, table_data]

@app.callback(
    Output('forecasting_graph container', 'children'),
    [Input('start_month', 'value'),
     Input('end_month', 'value'),
     Input('forecasting_dropdown', 'value')],
    prevent_initial_update=True
)
def updating_forecasting_graph(start_date, end_date, value):

    filters_date_bls = ((bls_data['year_month'] >= start_date) & (bls_data['year_month'] <= end_date))
    filtered_merged_data = merged_df.loc[filters_date_bls, :]
    filtered_forecast_data = forecast_data.loc[filters_date_bls, :]
    stl_data = filtered_merged_data

    forecasting_column = [col for col in filtered_forecast_data.columns if value in col]
    forecasting_data = filtered_forecast_data[['year_month'] + forecasting_column]
    print(forecasting_data)

    fig_forecast_line = go.Figure()
    line_graph(fig_forecast_line, filtered_merged_data, 'year_month', value)

    for column in forecasting_column:

        line_graph(
            fig_forecast_line,
            data=forecasting_data,
            x='year_month',
            y=column,
            mode='line',
            title='Forecasting ' + value,
            x_axis='year',
            y_axis='Value'
        )

    return html.Div(
        children=[
            dcc.Graph(figure=fig_forecast_line, className='full_card'),
            html.Div(dcc.Graph(figure=stl_chart(stl_data, x='year_month', y='Cpi Values'), className='stl_chart')),
            html.Div(dcc.Graph(figure=acf_pacf_plot(merged_df, 'PPI Values', lag=100),
                               className='stl_chart')),  # ACF, PACF
            html.Div()
    ])



