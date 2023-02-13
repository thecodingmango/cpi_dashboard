"""This file is used to retrieve data from the US BLS and US EIA website using their public API"""

# Importing libraries
import requests
import json


class Updator:

    def __init__(self, bls_series, bls_url, start_year, end_year):
        self.bls_series = bls_series
        self.bls_url = bls_url
        self.start_year = str(start_year)
        self.end_year = str(end_year)

    # Function to retrieve data from the US BLS website
    def retrieve_data_bls(self):

        """
        Takes in a list of series id and retrieve their data values from the website
        :param series_id: List of series id in strings
        """

        headers = {'Content-type': 'application/json'}
        data = json.dumps({'seriesid': self.bls_series, 'startyear': self.start_year, 'endyear': self.end_year})

        p = requests.post(self.bls_url, data=data, headers=headers)
        json_data = json.loads(p.text)

        return json_data


series = ['CUUR0000SA0', 'SUUR0000SA0']
data = Updator(series, 'https://api.bls.gov/publicAPI/v1/timeseries/data/', 2010, 2020)
retrieved_data = data.retrieve_data_bls()

