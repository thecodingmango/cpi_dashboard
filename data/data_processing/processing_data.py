"""
This file is meant to be used for checking missing value and datatypes from the data pulled using the EIA and BLS API

Things to check:

 - Checking for missing value
 - Checking for correct data type
 - Filling any missing values
"""

import pandas as pd


def check_missing_value(dataframe):
    """
    Checks for any missing values for EIA and BLS dataframe
    :param dataframe: Pandas dataframe
    :return: List with columns that have missing value
    """

    # List to track missing column name with missing value
    track_missing = []

    for column in dataframe.columns:

        if dataframe[column].isnull().any():

            track_missing += [column]

            print(f'Total Missing Value for the column {column}: {dataframe[column].isnull().sum()}')

        else:

            print('No Missing Value')

    return track_missing


def check_dtype(dataframe):
    """
    Checks if the dataframe for EIA and BLS have the correct data type
    :param dataframe: Pandas Dataframe
    Most columns should be numeric with the data type flaot64
    year_month column should be objects data type
    :return: Dataframe with the correct data type
    """

    for column in dataframe.columns:

        if column != 'year_month':

            if dataframe[column].dtypes != 'float64':

                dataframe[column] = pd.to_numeric(dataframe[column])

    return dataframe
