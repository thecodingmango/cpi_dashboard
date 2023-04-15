# Settings for global variables
from datetime import datetime

# Start year is current year - 19 years
start_year = datetime.now().year - 19

# End year is current year
end_year = datetime.now().year

# Series ID used by the BLS API to pull data
bls_series = ['APU0000708111', 'APU000072610', 'APU0000709112', 'APU0000702111', 'APU0000704111', 'APU0000FF1101',
              'APU0000706111', 'APU0000711211', 'APU0000701312', 'APU0000717311', 'APU0000703111', 'APU0000702421',
              'APU0000711311', 'APU0000712311', 'CUUR0000SA0']

# Series name corresponding the each series ID
bls_series_name = ['eggs', 'electricity', 'milk', 'bread', 'bacon', 'chicken_breast', 'chicken_whole', 'bananas',
                   'rice', 'coffee', 'ground_chuck', 'cookies', 'oranges', 'tomatoes', 'cpi_values']

# EIA series ID
eia_petroleum_price = ['/petroleum/pri/spt/data/?&data[0]=value&facets[product][]=EPCBRENT',
                       '/petroleum/pri/spt/data/?&data[0]=value&facets[product][]=EPCWTI']

# EIA series name
eia_petroleum_name = ['uk_brent_prices', 'wti_prices']


# Url for BLS and EIA website
url_bls = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
url_eia = 'https://api.eia.gov/v2'

