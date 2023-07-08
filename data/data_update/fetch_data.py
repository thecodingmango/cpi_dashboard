"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
import requests
import json
import api_keys
import config
from data.data_processing.data_checking import *
import data.misc_func as misc_func


class Updater:

    def __init__(self):
        self.bls_url = config.url_bls
        self.eia_url = config.url_eia
        self.start_year = config.start_year
        self.end_year = config.end_year

    # API to retrieve data from the US BLS website
    def retrieve_data_bls(self, bls_series, bls_series_name):
        """
        Takes in a list of series id and retrieve their data values from the website
        :param: List of series id in strings
        :return: Pandas Dataframe
        """

        # Requesting data through API
        headers = {'Content-type': 'application/json'}
        data = json.dumps({'seriesid': bls_series,
                           'startyear': self.start_year,
                           'endyear': self.end_year,
                           "registrationkey": api_keys.bls_api_key})

        p = requests.post(self.bls_url, data=data, headers=headers)
        json_data = json.loads(p.text)

        # Get the data from a list of dictionaries into a nested list
        # Then the nested list is put into a dataframe
        bls_df = misc_func.dict_to_df(json_data['Results']['series'], ['data', 'value'])
        bls_df.columns = bls_series_name

        # Check the data before returning the dataframe
        bls_df = data_check(bls_df)

        # Extract the value date from the series and put it as a new column into the bls df
        bls_df['year_month'] = misc_func.bls_parse_date(json_data['Results']['series'][0]['data'])

        return bls_df

    # API to retrieve data from the US Energy Information Administration
    def retrieve_data_eia(self, eia_series, eia_series_name):
        """
        Used to retrieve data from the US EIA website using an API key
        :return:
        """

        # Setting for the EIA API
        sort_value = '&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000'  # Sort by descending order
        frequency = '&frequency=monthly'  # Pull data in monthly interval
        start_date = '&start=' + str(self.start_year) + '-01'
        api_key = '&api_key=' + api_keys.eia_api_key  # API key

        # Temporary list to store all the values
        temp_list = []

        # Loops through all the series needed, and request the data for each series separately
        for series in eia_series:

            api_request = self.eia_url + series + sort_value + frequency + start_date + api_key
            r = requests.get(api_request)
            json_data = r.json()

            temp_list += misc_func.dict_to_list(json_data['response']['data'], 'value')

        # Converts the list of values into Pandas Dataframe
        eia_df = pd.DataFrame(temp_list).transpose()

        # Setting column name for the dataframe
        eia_df.columns = eia_series_name

        # Check the data before returning the dataframe
        eia_df = data_check(eia_df)

        # Get the date period for all the values in the list
        eia_df['year_month'] = pd.DataFrame(misc_func.dict_to_list(json_data['response']['data'], 'period')).transpose()

        return eia_df


# data = Updater()
# bls_api = data.retrieve_data_bls(config.bls_series, config.bls_series_name)
# eia_api = data.retrieve_data_eia(config.eia_petroleum_price, config.eia_petroleum_name)
#eia = pd.DataFrame(eia_api).transpose()
