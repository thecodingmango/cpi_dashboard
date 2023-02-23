"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
import requests
import json
from datetime import datetime
import pandas as pd
import numpy as np

# Settings for global variables
start_year = 2000
end_year = datetime.now().year
series = ['CUUR0000SA0', 'SUUR0000SA0']
url_bls = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'


class Updator:

    def __init__(self, bls_series, bls_url, start_year, end_year):
        self.bls_series = bls_series
        self.bls_url = bls_url
        self.start_year = start_year
        self.end_year = end_year

    # Function to retrieve data from the US BLS website
    def retrieve_data_bls(self):

        """
        Takes in a list of series id and retrieve their data values from the website
        :param series_id: List of series id in strings
        """

        headers = {'Content-type': 'application/json'}
        data = json.dumps({'seriesid': self.bls_series,
                           'startyear': str(self.start_year),
                           'endyear': str(self.end_year),
                           "registrationkey": "064c315c02b84896aaa929d9a38510ac"})

        p = requests.post(self.bls_url, data=data, headers=headers)
        json_data = json.loads(p.text)

        print(json_data)

        return json_data

    # Function that converts dictionaries to list
    def dict_to_list(self, keys, dicts):

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

        return np.array(list_array)



data = Updator(series, url_bls, 2000, 2020)
retrieved_data = data.retrieve_data_bls()
retrieved_data_2 = data.retrieve_data_bls()
data.dict_to_list(['year', 'periodName', 'value'], retrieved_data['Results']['series'][0]['data'])[2]

