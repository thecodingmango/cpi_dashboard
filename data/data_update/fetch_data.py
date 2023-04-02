"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
import requests
import json
import pandas as pd
import api_keys
import config


class Updater:

    def __init__(self):
        self.bls_series = config.bls_series
        self.eia_series = config.eia_series
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
        :param keys: List of keys, m
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
            year_month += ['-'.join(date) + '-01']

            # Remove letter m in period
            year_month = [str(item).replace('M', '') for item in year_month]

        return pd.DataFrame(year_month)

    # Function to retrieve data from the US BLS website
    def retrieve_data_bls(self):
        """
        Takes in a list of series id and retrieve their data values from the website
        :param: List of series id in strings
        :return: Pandas Dataframe
        """

        headers = {'Content-type': 'application/json'}
        data = json.dumps({'seriesid': self.bls_series,
                           'startyear': self.start_year,
                           'endyear': self.end_year,
                           "registrationkey": api_keys.bls_api_key})

        p = requests.post(self.bls_url, data=data, headers=headers)
        json_data = json.loads(p.text)

        print(json_data)

        bls_df = Updater.dict_to_df(json_data['Results']['series'], ['data', 'value'])
        bls_df.columns = config.bls_series_name
        bls_df['year_month'] = Updater.bls_parse_date(json_data['Results']['series'][0]['data'])

        return bls_df

    # Function to retrieve data from the US Energy Information Administration
    def retrieve_data_eia(self):
        """
        Used to retrieve data from the US EIA website using an API key
        :return:
        """

        #
        sort_value = '&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000'
        frequency = '&frequency=monthly'
        api_key = '&api_key=' + api_keys.eia_api_key

        temp_list = []

        for series in self.eia_series:

            api_request = self.eia_url + series + sort_value + frequency + api_key
            r = requests.get(api_request)
            json_data = r.json()

            temp_list += Updater.dict_to_list(json_data['response']['data'], ['value'])

        return temp_list


data = Updater()
retrieved_data = data.retrieve_data_bls()
eia_api = data.retrieve_data_eia()
eia = pd.DataFrame(eia_api).transpose()
