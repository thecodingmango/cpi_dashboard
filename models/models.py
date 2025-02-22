# - Stationarity test
#  - Do few different models like
#       - STL, ARMA, AR models, ARIMA, SARIMA, linear regression on CPI
#       - ARIMA with XGBoost on the residuals
#    - crude price, oil production, oil consumption, food
#   - ACF PLOT
#   - Forecast CPI using different price point of the crude oil
# CPI values second diff is stationary, everything else is first diff stationary
from statistics import linear_regression
# Maybe detrend data

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, root_mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.vector_ar.var_model import forecast
from statsmodels.tsa.seasonal import STL


class Model:

    def __init__(self, df, y):

        self.data = df
        self.data['year_month'] = pd.to_datetime(self.data['year_month']).dt.strftime('%Y-%m')
        self.data = self.data.sort_values(by='year_month', ascending=True, inplace=False)
        self.target = y
        self.y = self.data.loc[:, [self.target, 'year_month']]


    def check_stationarity(self, new_df):

        threshold = 0.05
        p_value = 1
        max_diff = 3
        current_diff = 0

        while p_value > threshold and current_diff < max_diff:

            for column in new_df.columns[1:-1]:
                stationary = adfuller(new_df[column].dropna())
                print('Column:' + column)
                print('-----------------------------------------')
                print(f"ADF Statistic: {stationary[0]:.2f}")
                print(f"p-value: {stationary[1]:.2f}")
                print("Series is NOT stationary\n") if stationary[1] > 0.05 else print("Series is stationary\n")
                p_value = stationary[1]

                if p_value > threshold:
                    current_diff += 1
                    print(f"Number of Difference: {current_diff:.2f}\n")
                    new_df.iloc[:, 1:-1] = new_df.iloc[:, 1:-1].diff()
                    new_df = new_df.dropna()

        new_df.iloc[:, 1:-1] = abs(new_df.iloc[:, 1:-1])

        return new_df

    def min_max_transform(self, columns):

        for item in columns:
            self.data[item] = ((self.data[item] - self.data[item].min())/
                               (self.data[item].max() - self.data[item].min()))

        return self.data

    def train_test_split(self, test_prop):

        train_size = int(len(self.y) * (1 - test_prop))

        # Use iloc for position-based slicing
        x_train = self.y.iloc[:train_size, self.y.columns != self.target]
        x_test = self.y.iloc[train_size:, self.y.columns != self.target]
        y_train = self.y.iloc[:train_size][self.target]
        y_test = self.y.iloc[train_size:][self.target]

        return x_train, x_test, y_train, y_test

    def acf(self, column, lag):

        df = self.data.copy()
        df.set_index('year_month', inplace=True)
        ts = df[column]
        ts_diff = df[column].diff(1)
        ts_diff = ts_diff.dropna()

        plot_acf(ts, lags=lag)
        plt.savefig('acf.png')

        plot_acf(ts_diff, lags=lag)
        plt.savefig('acf_diff.png')

        plot_pacf(ts_diff, lags=lag)
        plt.savefig('pacf_diff.png')

        plt.plot(ts_diff)
        plt.savefig('ts_diff.png')

    def metric(self, y_true, y_pred):

        mse = mean_squared_error(y_true=y_true, y_pred=y_pred)
        rmse = root_mean_squared_error(y_true=y_true, y_pred=y_pred)

        return {'mse': mse, 'rmse': rmse}


    def lag_features(self, new_df, lag, remove_original=None):

        for col in new_df.columns:
            for num in lag:
                new_df[col + '_' +str(num)] = new_df[col].shift(num)

            if remove_original:
                new_df = new_df.drop(col, axis=1)

        return new_df.dropna()

    def linear_regression(self, x_train, y_train):

        lr = LinearRegression()
        lr.fit(x_train, y_train)

        return lr

    def stl(self, new_df):

        stl = STL(new_df, period=12)
        stl = stl.fit()
        result = pd.DataFrame(
            {'trend': stl.trend,
             'seasonal': stl.seasonal,
             'residuals': stl.resid
            }
        )

        return result


    def sarimax(self, y_train,p, d, q, s,exog=None): # Use p=1, d=1, q=1

        sarima = SARIMAX(
            endog=y_train,
            order=(p, d, q),
            seasonal_order=s,
            exog=exog,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        results = sarima.fit(disp=False)

        return results

    def xgboost(self):
        pass

    def var(self):
        pass

    def xgarimax(self): # XGBoost + ARIMA
        pass

    def iterative_forecast(self, ts_model, df_history, horizon):

        last_row = df_history.iloc[-1].copy()
        forecast_list = []
        feat= {}

        for column in df_history.columns:
            feat[column] = last_row[column]

        #last_date = df_history.index[-1]
        #future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq="MS")[1:]
        # The above line: we get freq="MS" (month start) from T up to T+5, skip the first to avoid duplication
        x_future = pd.DataFrame([feat])

        for i in range(horizon):

            pred = ts_model.predict(x_future)[0]

            forecast_list.append({
                x_future.columns[0] + "_forecast": pred
            })

            n_cols = x_future.shape[1]

            # Shift columns in descending order:
            for j in range(n_cols - 1, 0, -1):
                x_future.iloc[0, j] = x_future.iloc[0, j - 1]

            # Now put the new prediction into the first column
            x_future.iloc[0, 0] = pred

        df_forecast = pd.DataFrame(forecast_list)
        return df_forecast

    def year_month_index(self, df):
        print(df)
        df['year_month'] = pd.date_range(
            df['year_month'].min(),
            df['year_month'].max(),
            freq='MS').strftime('%Y-%m')
        df.reset_index()
        df.set_index('year_month', inplace=True)

        return df

    def model_building(self):

        lag = list(range(1, 13))
        self.y = self.lag_features(self.y.iloc[:, :-1], lag, False)
        self.y['year_month'] = self.data['year_month'].copy()
        print(self.y)
        self.y = self.year_month_index(self.y)
        # pd.date_range(
        #     self.y['year_month'].min(),
        #     self.y['year_month'].max(),
        #     freq='MS').strftime('%Y-%m')
        # self.y.reset_index()
        # self.y.set_index('year_month', inplace=True)
        x_train, x_test, y_train, y_test = self.train_test_split(test_prop=0.2)

        # Linear Regression Model
        lr_model = self.linear_regression(x_train.iloc[:, :-1], y_train)
        lr_pred = lr_model.predict(x_test.iloc[:, :-1])
        lr_metrics = self.metric(y_test, lr_pred)
        lr_metrics['r2'] = r2_score(y_true=y_test, y_pred=lr_pred)
        lr_forecast = self.iterative_forecast(lr_model, x_test.iloc[:, :-1],12)
        print(lr_pred, '\n', lr_metrics)
        print(lr_forecast)

        self.y = self.data.copy()
        self.y = self.year_month_index(self.y)
        x_train, x_test, y_train, y_test = self.train_test_split(test_prop=0.1)
        arima = self.sarimax(y_train, 12 ,0, 12, (0,0,0,12))
        arima_pred = arima.predict(start=y_test.index[0], end=y_test.index[-1])
        arima_train_metrics = self.metric(y_train, arima.predict(start=y_train.index[0], end=y_train.index[-1]))
        arima_test_metrics = self.metric(y_test, arima_pred)
        arima_forecast = arima.forecast(steps=12)
        print(arima_forecast)
        print(arima_train_metrics,'\n',arima_test_metrics)

        # STL
        stl_result = self.stl(self.y.loc[:, self.target])
        print(stl_result)



data = pd.read_csv('./data/bls_food.csv')
#model = Model(df=data, y='Cpi Values')
model = Model(df=data, y='PPI Values')
#stl_1 = model.stl(data)
#stl_1.to_csv('stl.csv')
#model.acf('Cpi Values', lag=100)
#model.check_stationarity(data)
#test_diff = model.check_stationarity(model.data)
#model = model.min_max_transform(['Cpi Values', 'PPI Values'])
#x_train, x_test, y_train, y_test = model.train_test_split(test_prop=0.2)
#test_lag = model.lag_features(data,[1, 3, 6, 12], True)
model.model_building()



