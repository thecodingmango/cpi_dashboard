# Settings for global variables
from datetime import datetime

# Start year is current year - 19 years
start_year = datetime.now().year - 19

# End year is current year
end_year = datetime.now().year

current_month = datetime.now().month - 1

# Series ID used by the BLS API to pull data
bls_series = ['APU0000708111', 'APU000072610', 'APU0000709112', 'APU0000702111', 'APU0000704111', 'APU0000FF1101',
              'APU0000706111', 'APU0000711211', 'APU0000701312', 'APU0000717311', 'APU0000703111', 'APU0000702421',
              'APU0000711311', 'APU0000712311', 'CUUR0000SA0']

# Series name corresponding to each series ID
bls_series_name = ['eggs', 'electricity', 'milk', 'bread', 'bacon', 'chicken_breast', 'chicken_whole', 'bananas',
                   'rice', 'coffee', 'ground_chuck', 'cookies', 'oranges', 'tomatoes', 'cpi_values']

# EIA petroleum series
eia_petroleum_price = ['/petroleum/pri/spt/data/?&data[0]=value&facets[product][]=EPCBRENT',
                       '/petroleum/pri/spt/data/?&data[0]=value&facets[product][]=EPCWTI']
eia_petroleum_name = ['uk_brent_prices', 'wti_prices']

# EIA crude oil import series
eia_crude_import = ['/crude-oil-imports/data/?data[0]=quantity&'
                    '&facets[originId][]=OPN_N&'
                    '&facets[originId][]=REG_AF&'
                    '&facets[originId][]=REG_AP&'
                    '&facets[originId][]=REG_CA&'
                    '&facets[originId][]=REG_EU&'
                    '&facets[originId][]=REG_ME&'
                    '&facets[destinationType][]=US']
eia_crude_import_name = ['originName', 'destinationName', 'quantity', 'gradeName']

# EIA crude oil production
eia_crude_production = ['/steo/data/?data[0]=value&facets[seriesId][]=PAPR_US',
                        '/steo/data/?data[0]=value&facets[seriesId][]=PAPR_CA',
                        '/steo/data/?data[0]=value&facets[seriesId][]=PAPR_MX',
                        '/steo/data/?data[0]=value&facets[seriesId][]=PAPR_OPEC',
                        '/steo/data/?data[0]=value&facets[seriesId][]=PAPR_FSU',
                        '/steo/data/?data[0]=value&facets[seriesId][]=PAPR_CH']
eia_crude_production_name = ['US', 'CA', 'MX', 'OPEC', 'EURASIA', 'CHINA']

# EIA crude oil consumption
eia_crude_consumption = ['/steo/data/?data[0]=value&facets[seriesId][]=PATC_US',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_CA',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_OECD_EUROPE',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_JA',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_FSU',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_NONOECD_EUROPE',
                         '/steo/data/?data[0]=value&facets[seriesId][]=PATC_CH']
eia_crude_consumption_name = ['US', 'CA', 'OECD_EUROPE', 'JP', 'EURASIA', 'NON_OECD_EUROPE', 'CHINA']

# Url for BLS and EIA website
url_bls = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
url_eia = 'https://api.eia.gov/v2'
