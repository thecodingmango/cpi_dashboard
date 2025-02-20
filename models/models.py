# - Stationarity test
#  - Do few different models like
#       - STL, ARMA, AR models, ARIMA, SARIMA, linear regression on CPI
#       - ARIMA with XGBoost on the residuals
#    - crude price, oil production, oil consumption, food
#   - ACF PLOT
#   - Forecast CPI using different price point of the crude oil
import pandas as pd
import numpy as np
import datetime as dt
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


class Model:

    def __init__(self, df):

        self.data = df
        self.data['year_month'] = pd.to_datetime(self.data['year_month']).dt.strftime('%Y-%m')
        self.data = self.data.sort_values(by='year_month', ascending=True, inplace=False)

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

    def min_max_transform(self, columns):

        for item in columns:
            self.data[item] = ((self.data[item] - self.data[item].min())/
                               (self.data[item].max() - self.data[item].min()))

        return self.data

    def train_test_split(self, x, y, test_prop):

        train_size = int(len(y) * (1 - test_prop))
        test_size = len(y) - train_size
        print(test_size)

        x_train = x.iloc[:train_size, :]
        x_test = x.iloc[train_size:, :]
        y_train = y.iloc[:train_size]
        y_test = y.iloc[train_size:]

        return x_train, x_test, y_train, y_test

    def acf(self, column, lag):

        df = self.data.copy()
        df.set_index('year_month', inplace=True)
        ts = df[column]
        ts_diff = df[column].diff(1)
        ts_diff = ts_diff.dropna()

        plt.Figure(figsize=(10, 5))
        plot_acf(ts, lags=lag)
        plt.savefig('acf.png')

        plot_acf(ts_diff, lags=lag)
        plt.savefig('acf_2.png')

        plot_pacf(ts_diff, lags=lag)
        plt.savefig('pacf_2.png')

        plt.plot(ts_diff)
        plt.savefig('ts_diff.png')

    def lag_features(self, lag):
        pass

    def linear_regression(self):
        pass

    def stl(self):
        pass

    def arimax(self, p, d, q):
        pass

    def sarimax(self):
        pass

    def xgboost(self):
        pass

    def var(self):
        pass

    def xgarimax(self): # XGBoost + ARIMA
        pass

data = pd.read_csv('./data/bls_food.csv')
model = Model(df=data)
model.check_stationarity()
#model = model.min_max_transform(['Cpi Values', 'PPI Values'])
x_train, x_test, y_train, y_test = model.train_test_split(data.iloc[:, 1:], data.iloc[:, -3], test_prop=0.2)
model.acf('Cpi Values', 100)



