import dash
import config
from layout_functions.layout_functions import *
from data.data_update.fetch_data import *

# Using apis to import data
'''
data_api = Updater()

bls_data = data_api.retrieve_data_bls(config.bls_series, config.bls_series_name)

eia_petroleum_spot = data_api.retrieve_data_eia(config.eia_petroleum_price, config.eia_petroleum_name, ['value'])

eia_api_crude_production = data_api.retrieve_data_eia(config.eia_crude_production,
                                                      config.eia_crude_production_name,
                                                      ['value'])
eia_api_crude_consumption = data_api.retrieve_data_eia(config.eia_crude_consumption,
                                                       config.eia_crude_consumption_name,
                                                       ['value'])

'''
bls_data = pd.read_csv('./data/bls_data.csv')
eia_petroleum_spot = pd.read_csv('./data/eia_crude_consumption.csv')
eia_api_crude_production = pd.read_csv('./data/eia_crude_price.csv')
eia_api_crude_consumption = pd.read_csv('./data/eia_crude_production.csv')


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
            id='header',
            className='header',
            children=[html.H1('Header')]
        ),
        html.Div(
            children=[
                html.Div(
                    id='sidebar',
                    className='sidebar',
                    children=['this is a side bar']
                ),
                html.Div(
                    id='main',
                    className='card',
                    children=['this is the third div']
                )
            ],
            className='content_wrapper'
        )
    ],
    className='wrapper'
)



"""
# builing app layout
app.layout = html.Div(
    children=[
        header(),
        html.Div(
            date_picker(bls_data)
        ),
        html.Div(
            children=[
                dcc.Graph(
                    id='cpi_chart',
                    className='card',
                    config={'displayModeBar': True}
                )
            ]
        )
    ]
)


@app.callback(
    [Output('cpi_chart', 'figure')],
    [Input('date_range', 'start_date'),
     Input('date_range', 'end_date')]
)
def update_chart_range_bls(start_date, end_date):

    filters = ((bls_data['year_month'] >= start_date) & (bls_data['year_month'] <= end_date))
    filtered_data = bls_data.loc[filters, :]

    cpi_chart = {
        'data': [
            {
                'x': filtered_data['year_month'],
                'y': filtered_data['cpi_values'],
                'type': 'lines'
            }
        ],
        'layout': {
            'title':
                {'text': 'CPI Values Since' + ' ' + start_date,
                 'x': 0.05},
            'width': 500,
            'height': 500,
        }
    }

    return [cpi_chart]
"""