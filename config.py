from datetime import datetime

# Settings for global variables
start_year = datetime.now().year - 19
end_year = datetime.now().year
bls_series = ['APU0000708111', 'APU000072610', 'APU0000709112', 'APU0000702111', 'APU0000704111', 'APU0000FF1101',
              'APU0000706111', 'APU0000711211', 'APU0000701312', 'APU0000717311', 'APU0000703111', 'APU0000702421',
              'APU0000711311', 'APU0000712311', 'CUUR0000SA0']
bls_series_name = ['eggs', 'electricity', 'milk', 'bread', 'bacon', 'chicken_breast', 'chicken_whole', 'bananas',
                   'rice', 'coffee', 'ground_chuck', 'cookies', 'oranges', 'tomatoes', 'cpi_values']
url_bls = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'


