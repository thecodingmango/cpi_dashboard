"""
Helper function for both the EIA and BLS API
"""

import pandas as pd


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
        temp_list += dict_to_list(item[key[0]], [key[1]])

    data_df = pd.DataFrame(temp_list).transpose()

    return data_df


# Function to parse year and month in yyyy-mm-01 format for the BLS data
def bls_parse_date(list_dict):
    """
    The function is to parse date for the BLS data from year and month to YYYY-mm-01. It takes in a list of dicts,
    and will parse data according to the given keys
    :param list_dict: List of dictionaries that contains the year and period
    :return: Panda dataframe with the first day of the month
    """

    # Parse the dictionaries into a list
    year = dict_to_list(list_dict, ['year'])
    month = dict_to_list(list_dict, ['period'])

    year_month = []

    for date in list(zip(*year, *month)):
        # Join year and month together and set the date to first day of the month
        year_month += ['-'.join(date) + '-01']

        # Remove letter m in period
        year_month = [str(item).replace('M', '') for item in year_month]

    return pd.DataFrame(year_month)
