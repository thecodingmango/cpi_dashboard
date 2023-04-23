import dash
import config
from layout_functions.layout_functions import *
from data.data_update.fetch_data import *

# Using apis to import data
data_api = Updater()
bls_data = data_api.retrieve_data_bls(config.bls_series, config.bls_series_name)
eia_petroleum_spot = data_api.retrieve_data_eia(config.eia_petroleum_price, config.eia_petroleum_name, ['value'])
eia_api_crude = data_api.retrieve_data_eia(config.eia_crude_import,
                                           config.eia_crude_import_name,
                                           ['originName', 'destinationName', 'quantity', 'gradeName'])
eia_api_crude_production = data_api.retrieve_data_eia(config.eia_crude_production,
                                                      config.eia_crude_production_name,
                                                      ['value'])
eia_api_crude_consumption = data_api.retrieve_data_eia(config.eia_crude_consumption,
                                                       config.eia_crude_consumption_name,
                                                       ['value'])

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

# builing app layout
app.layout = html.Div(
    header()
)


