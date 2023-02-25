"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
import requests
import json
import pandas as pd
import api_keys
import config


class Updator:

    def __init__(self):
        self.bls_series = config.series
        self.bls_url = config.url_bls
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
        :return: numpy array
        """

        list_array = []

        for key in keys:

            list_item = [item.get(key) for item in dicts]

            list_array.append(list_item)

        return list_array

    @staticmethod
    # Function for the retrieve data function that converts list of dict into a Pandas dataframe
    def list_to_df(list_dict, key, column_name):
        """
        Takes in a list of dict and converts it into pandas dataframe
        :param key: Key must be a list of key to search through
        :param list_dict: List of dict
        :return: Pandas dataframe
        """

        temp_list = []

        for series in list_dict:

            temp_list += Updator.dict_to_list(series[key[0]], [key[1]])

        data_df = pd.DataFrame(temp_list).transpose()

        data_df.columns = ['column1', 'column2']

        return data_df

    # Function to retrieve data from the US BLS website
    def retrieve_data_bls(self):
        """
        Takes in a list of series id and retrieve their data values from the website
        :param: List of series id in strings
        :return: Pandas Dataframe
        """

        headers = {'Content-type': 'application/json'}
        data = json.dumps({'seriesid': self.bls_series,
                           'startyear': str(self.start_year),
                           'endyear': str(self.end_year),
                           "registrationkey": api_keys.bls_api_key})

        p = requests.post(self.bls_url, data=data, headers=headers)
        json_data = json.loads(p.text)

        print(json_data)

        return json_data


data = Updator()
retrieved_data = data.retrieve_data_bls()
retrieved_data_2 = data.retrieve_data_bls()
test = data.dict_to_list(['year', 'periodName', 'value'], retrieved_data['Results']['series'][1]['data'])

data.list_to_df(retrieved_data['Results']['series'], ['data', 'value'])

test = []
for series in retrieved_data['Results']['series']:

    test += data.dict_to_list(series['data'], ['value'])
pd.DataFrame(test).transpose()
