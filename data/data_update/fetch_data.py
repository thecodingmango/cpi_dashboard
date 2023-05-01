"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
from sys import api_version

import requests
import json
import api_keys
import config
from data.data_processing.data_checking import *


class Updater:

    def __init__(self):
        self.bls_url = config.url_bls
        self.eia_url = config.url_eia
        self.start_year = config.start_year
        self.end_year = config.end_year

    @staticmethod
    # Function that converts dictionaries to list
    def dict_to_list(dicts, keys):
        """
        Function that takes in list of dictionaries and return the values in each of the dictionaries with the specified
        key
        :param keys: List of keys
        :param dicts: List of Dict
        :return: Nested list of items
        """

        list_array = []

        for key in keys:

            list_item = [item.get(key) for item in dicts]

            list_array.append(list_item)

        return list_array

    @staticmethod
    # Function for the retrieve data function that converts list of dict into a Pandas dataframe for the BLS data
    def dict_to_df(list_dict, key):
        """
        Takes in a list of dict and converts it into pandas dataframe
        :param key: Key must be a list of key to search through
        :param list_dict: List of dict
        :return: Pandas dataframe
        """

        temp_list = []

        for item in list_dict:

            temp_list += Updater.dict_to_list(item[key[0]], [key[1]])

        data_df = pd.DataFrame(temp_list).transpose()

        return data_df

    @staticmethod
    # Function to parse year and month in yyyy-mm-01 format for the BLS data
    def bls_parse_date(list_dict):
        """
        The function is to parse date for the BLS data from year and month to YYYY-mm-01. It takes in a list of dicts,
        and will parse data according to the given keys
        :param list_dict: List of dictionaries that contains the year and period
        :return: Panda dataframe with the first day of the month
        """

        # Parse the dictionaries into a list
        year = Updater.dict_to_list(list_dict, ['year'])
        month = Updater.dict_to_list(list_dict, ['period'])

        year_month = []

        for date in list(zip(*year, *month)):

            # Join year and month together and set the date to first day of the month
            year_month += ['-'.join(date)]

        # Remove letter m in period
        year_month = [str(item).replace('M', '') for item in year_month]

        return pd.DataFrame(year_month)

    # Function to retrieve data from the US BLS website
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
        bls_df = Updater.dict_to_df(json_data['Results']['series'], ['data', 'value'])
        bls_df.columns = bls_series_name

        # Check the data before returning the dataframe
        bls_df = data_check(bls_df)

        # Extract the value date from the series and put it as a new column into the bls df
        bls_df['year_month'] = Updater.bls_parse_date(json_data['Results']['series'][0]['data'])

        return bls_df

    # Function to retrieve data from the US Energy Information Administration
    def retrieve_data_eia(self, eia_series, eia_series_name, values):
        """
        Used to retrieve data from the US EIA website using an API key
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
            temp_list += Updater.dict_to_list(json_data['response']['data'], values)

        # Converts the list of values into Pandas Dataframe
        eia_df = pd.DataFrame(temp_list).transpose()

        # Setting column name for the dataframe
        eia_df.columns = eia_series_name

        # Check the data before returning the dataframe
        eia_df = data_check(eia_df)

        # Get the date period for all the values in the list
        eia_df['year_month'] = pd.DataFrame(Updater.dict_to_list(json_data['response']['data'], ['period'])).transpose()

        return eia_df


# data = Updater()
# bls_api = data.retrieve_data_bls(config.bls_series, config.bls_series_name)
# eia_api_petroleum = data.retrieve_data_eia(config.eia_petroleum_price,
#                                            config.eia_petroleum_name,
#                                            ['value'])
# eia_api_crude = data.retrieve_data_eia(config.eia_crude_import,
#                                    config.eia_crude_import_name,
#                                    ['originName', 'destinationName', 'quantity', 'gradeName'])
# #eia = pd.DataFrame(eia_api).transpose()
# r = requests.get('https://api.eia.gov/v2/crude-oil-imports/data/?data[0]=quantity&'
#                     'facets[originId][]=OPN_N&'
#                     'facets[originId][]=REG_AF&'
#                     'facets[originId][]=REG_AP&'
#                     'facets[originId][]=REG_CA&'
#                     'facets[originId][]=REG_EU&'
#                     'facets[originId][]=REG_ME&'
#                     'facets[destinationType][]=US' + '&api_key='+'yUUgEB17VpR6y6wLao6DCg44YSAtbz0G9vtpfEot')
# test = r.json()
