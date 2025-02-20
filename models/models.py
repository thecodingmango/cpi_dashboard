# - Stationarity test
#  - Do few different models like
#       - STL, ARMA, AR models, ARIMA, SARIMA, linear regression on CPI
#       - ARIMA with XGBoost on the residuals
#    - crude price, oil production, oil consumption, food
#   - ACF PLOT
#   - Forecast CPI using different price point of the crude oil
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

class Model:

    def __init__(self, df):

        self.data = df

    def check_stationarity(self):

        if self.data.shape[1] > 3:
            for column in self.data.columns[1:-1]:
                stationarity = adfuller(self.data[column])
                print('Column:' + column)
                print('-----------------------------------------')
                print(f"ADF Statistic: {stationarity[0]:.2f}")
                print(f"p-value: {stationarity[1]:.2f}")
                print("Series is NOT stationary\n") if stationarity[1] > 0.05 else print("Series is stationary\n")

        else:
            stationarity = adfuller(adfuller(self.data.iloc[:, 1:-1]))
            print('Column:' + self.data.columns[1:-1])
            print('-----------------------------------------')
            print(f"ADF Statistic: {stationarity[0]:.2f}")
            print(f"p-value: {stationarity[1]:.2f}\n")
            print("Series is NOT stationary\n") if stationarity[1] > 0.05 else print("Series is stationary\n")

    def min_max_transform(self):
        pass

    def train_test_split(self):
        pass

    def lag_features(self, lag):


    def linear_regression(self):
        pass

    def stl(self):
        pass

    def arimax(self):
        pass

    def sarimax(self):
        pass

    def xgboost(self):
        pass

    def var(self):
        pass

model = Model(pd.read_csv('data/bls_food.csv'))
model.check_stationarity()




