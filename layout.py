import dash
from layout_functions.layout_functions import *
import config
from data.data_update.fetch_data import *

# Using apis to import data
data_api = Updater()
bls_data = data_api.retrieve_data_bls(config.bls_series, config.bls_series_name)
crude_spot = data_api.retrieve_data_eia(config.eia_petroleum_price, config.eia_petroleum_name)
eia_api_crude = data.retrieve_data_eia(config.eia_crude_import,
                                       config.eia_crude_import_name,
                                       ['originName', 'destinationName', 'quantity', 'gradeName'])


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


