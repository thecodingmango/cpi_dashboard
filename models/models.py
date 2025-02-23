# - Stationarity test
#  - Do few different models like
#       - STL, ARMA, AR models, ARIMA, SARIMA, linear regression on CPI
#       - ARIMA with XGBoost on the residuals
#    - crude price, oil production, oil consumption, food
#   - ACF PLOT
#   - Forecast CPI using different price point of the crude oil
# Maybe detrend data

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, root_mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from statsmodels.tsa.seasonal import STL
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV


def stl(new_df):

    stl = STL(new_df, period=12)
    stl = stl.fit()
    result = pd.DataFrame(
        {'trend': stl.trend,
         'seasonal': stl.seasonal,
         'residuals': stl.resid
         }
    )

    return result


class Model:

    def __init__(self, df, y, order, seasonal_order):

        self.data = df
        self.data['year_month'] = pd.to_datetime(self.data['year_month']).dt.strftime('%Y-%m')
        self.data = self.data.sort_values(by='year_month', ascending=True, inplace=False)
        self.target = y
        self.y = self.data.loc[:, [self.target, 'year_month']]
        self.order = order
        self.s_order = seasonal_order

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

    def min_max_transform(self, df, reverse=False):

        if not reverse:
            for col in df.columns:
                df[col] = ((df[col] - df[col].min()) / (df[col].max() - df[col].min()))
        else:
            for col in df.columns:
                df[col] = (df[col].max() - df[col].min()) / (df[col] - df[col].min())

        return df

    def train_test_split(self, target_col, test_prop):

        train_size = int(len(self.y) * (1 - test_prop))

        # Use iloc for position-based slicing
        x_train = self.y.iloc[:train_size, self.y.columns != target_col]
        x_test = self.y.iloc[train_size:, self.y.columns != target_col]
        y_train = self.y.iloc[:train_size][target_col]
        y_test = self.y.iloc[train_size:][target_col]

        return x_train, x_test, y_train, y_test

    def metric(self, y_true, y_pred):

        mse = mean_squared_error(y_true=y_true, y_pred=y_pred)
        rmse = root_mean_squared_error(y_true=y_true, y_pred=y_pred)

        return {'mse': mse, 'rmse': rmse}

    def lag_features(self, new_df, lag, remove_original=None):

        for col in new_df.columns:
            for num in lag:
                try:
                    new_df[col + '_' + str(num)] = new_df[col].shift(num)
                except AttributeError as e:
                    new_df[col + '_' + str(num)] = new_df.shift(num)
                    print(e)
            if remove_original:
                new_df = new_df.drop(col, axis=1)

        return new_df.dropna()

    def seasonal_naives(self, steps):

        new_df = self.y.iloc[-steps:][self.target].copy()
        future_dates = pd.date_range(start=new_df.index[-1][:4] + '-2',
                                     periods=steps, freq='MS').strftime('%Y-%m')
        new_df = pd.DataFrame({self.target: new_df.values}, index=future_dates)

        return new_df

    def linear_regression(self, x_train, y_train):

        lr = LinearRegression()
        lr.fit(x_train, y_train)

        return lr

    def sarimax(self, y_train, p, d, q, s, trend=None, exog=None):  # Use p=1, d=1, q=1

        sarima = SARIMAX(
            endog=y_train,
            order=(p, d, q),
            trend=trend,
            seasonal_order=s,
            exog=exog,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        results = sarima.fit(disp=False)

        return results

    def xgboost(self, x_train, y_train, x_test=None, y_test=None):

        param_grid = {
            'learning_rate': [0.1, 0.3, 0.5, 0.75],
            'max_depth': [3, 5, 7],
            'lambda': [10, 30, 50, 100, 1000, 5000],
            'alpha': [1, 3, 5, 10]
        }

        grid_serach = GridSearchCV(
            estimator=XGBRegressor(objective="reg:squarederror"),
            param_grid=param_grid,
            scoring='neg_mean_squared_error',
            cv=TimeSeriesSplit(n_splits=2)
        )

        best_param = grid_serach.fit(x_train, y_train).best_params_
        print(best_param)

        param = {
            'objective': "reg:squarederror",
            'eval_metric': 'rmse',
            'n_estimators': 200,
            'learning_rate': best_param['learning_rate'],
            'max_depth': best_param['max_depth'],
            'lambda': best_param['lambda'],
            'alpha': best_param['alpha']
        }

        if x_test is not None and y_test is not None:
            xgb_model = XGBRegressor(**param, early_stopping_rounds=5)
            xgb_model.fit(x_train, y_train, eval_set=[(x_train, y_train), (x_test, y_test)], verbose=149)
        else:
            xgb_model = XGBRegressor(**param, early_stopping_rounds=5)
            xgb_model.fit(x_train, y_train, eval_set=[(x_train, y_train)], verbose=149)

        return xgb_model

    def iterative_forecast(self, ts_model, df_history, horizon):

        last_row = df_history.iloc[-1].copy()
        forecast_list = []
        feat = {}

        for column in df_history.columns:
            feat[column] = last_row[column]

        x_future = pd.DataFrame([feat])

        for i in range(horizon):

            pred = ts_model.predict(x_future)[0]

            forecast_list.append({
                x_future.columns[0] + "_forecast": pred
            })

            n_cols = x_future.shape[1]

            for j in range(n_cols - 1, 0, -1):
                x_future.iloc[0, j] = x_future.iloc[0, j - 1]

            x_future.iloc[0, 0] = pred

        df_forecast = pd.DataFrame(forecast_list)

        return df_forecast

    def year_month_index(self, df):

        df['year_month'] = pd.date_range(
            df['year_month'].min(),
            df['year_month'].max(),
            freq='MS').strftime('%Y-%m')
        df.reset_index()
        df.set_index('year_month', inplace=True)

        return df

    def model_building(self):

        s_t = stl(self.y.copy()[self.target])
        lag = list(range(1, 13))
        self.y.iloc[:, 0] = self.y.iloc[:, 0] - s_t['seasonal'] - s_t['residuals']
        self.y['year_month'] = self.data['year_month'].copy()
        self.y = self.lag_features(self.y.iloc[:, :-1], lag, False)
        self.y['year_month'] = self.data['year_month'].copy()
        self.y = self.year_month_index(self.y)
        x_train, x_test, y_train, y_test = self.train_test_split(self.target, test_prop=0.1)

        # Linear Regression Model
        lr_model = self.linear_regression(x_train, y_train)
        lr_pred = lr_model.predict(x_test)
        lr_trend = lr_pred[-12:]
        lr_metrics = self.metric(y_test, lr_pred)
        lr_metrics['r2'] = r2_score(y_true=y_test, y_pred=lr_pred)
        lr_forecast = pd.DataFrame(self.iterative_forecast(
            lr_model, x_test, 12).reset_index().iloc[-12:, 1].values +
                                   s_t['residuals'].reset_index().iloc[-12:, 1].values +
                                   s_t['seasonal'].reset_index().iloc[-12:, 1].values)

        # Seasonal Naives
        s_naives = self.seasonal_naives(max(lag))

        # XGBoost
        self.y = pd.DataFrame(s_t['residuals'])
        self.y = self.lag_features(self.y, lag, False)
        x_train, x_test, y_train, y_test = self.train_test_split('residuals', test_prop=0.1)
        xgb_model = self.xgboost(x_train, y_train, x_test, y_test)
        xgb_metrics = self.metric(y_test, xgb_model.predict(x_test))
        print(xgb_metrics)
        xgb_forecast = self.iterative_forecast(xgb_model, x_test, 12)
        xgb_forecast = (pd.DataFrame(xgb_forecast.reset_index()).iloc[:, 1].values +
                        lr_trend +
                        s_t['seasonal'].reset_index().iloc[-12:, 1].values)
        xgb_forecast = pd.DataFrame(xgb_forecast)

        # SARIMA
        self.y = self.data.copy()
        self.y = self.year_month_index(self.y)
        x_train, x_test, y_train, y_test = self.train_test_split(self.target, test_prop=0.1)

        # Final SARIMA model
        sarima = self.sarimax(pd.concat([y_train, y_test], axis=0),
                              self.order[0], self.order[1], self.order[2], self.s_order, trend='ct')
        sarima_forecast = sarima.forecast(steps=12)


        # XGBoost + SARIMA
        self.y = self.data.copy()
        self.y = self.year_month_index(self.y)
        self.y = pd.concat([sarima.resid, self.y.copy()[self.target], sarima.fittedvalues], axis=1)
        self.y.columns = ['arima_resid', self.target, 'arima_fitted_values']
        self.y = self.lag_features(self.y, lag, False)
        self.y = self.y.drop(columns=[self.target, 'arima_fitted_values'], axis=1)

        x_train, x_test, y_train, y_test = self.train_test_split('arima_resid', test_prop=0.1)
        xgb_sarima = self.xgboost(x_train, y_train, x_test, y_test)
        resid_forecast = self.iterative_forecast(xgb_sarima, x_test, 12)
        final_xgb_arima = (sarima.get_forecast(steps=12).predicted_mean.reset_index().iloc[:, 1] +
                           resid_forecast.reset_index().iloc[:, 1])


        final_df = pd.DataFrame()
        final_df['year_month'] = pd.date_range(start=self.y.index[-1][:4] + '-2',
                                               periods=max(lag), freq='MS').strftime('%Y-%m')
        final_df = pd.concat([
            final_df,
            lr_forecast.reset_index().iloc[:, 1],
            s_naives.reset_index().iloc[:, 1],
            xgb_forecast.reset_index().iloc[:, 1],
            sarima_forecast.reset_index().iloc[:, 1],
            final_xgb_arima.reset_index().iloc[:, 1],
        ], axis=1)
        final_df.columns = [
            'year_month',
            self.target + ' Linear Regression Forecast',
            self.target + ' Seasonal Naives Forecast',
            self.target + ' XGBoost Forecast',
            self.target + ' SARIMA Forecast',
            self.target + ' SARIMA' + ' & XGBoost Forecast'
        ]

        return final_df

# Testing purposes
#data = pd.read_csv('./data/bls_food.csv')
#model = Model(df=data, y='PPI Values', order=(1, 1, 0), seasonal_order=(1, 0, 0, 12))
# #stl_1 = model.stl(data)
# #stl_1.to_csv('stl.csv')
# #model.acf('Cpi Values', lag=100)
# #model.check_stationarity(data)
# #test_diff = model.check_stationarity(model.data)
# #model = model.min_max_transform(['Cpi Values', 'PPI Values'])
# #x_train, x_test, y_train, y_test = model.train_test_split(test_prop=0.1)
# #test_lag = model.lag_features(data,[1, 3, 6, 12], True)
#test_model = model.model_building()

# Commented out to conserve computational power
dataset = [
    './data/bls_food.csv',
    './data/bls_gas_price.csv',
    './data/eia_crude_price.csv'
]

# Found using auto.arima in R
sarima_order = {
    'Cpi Values' : [(1, 2, 2), (2, 0, 0, 12)],
    'PPI Values': [(1, 1, 0), (1, 0, 0, 12)],
    'Unemployment': [(0,1,0), (0, 0, 0, 0)],
    'Unleaded Gasoline': [(0, 1, 1), (0, 0, 0, 0)],
    'UK Brent Prices': [(1, 1, 0), (0, 0, 0, 0)],
    'WTI Prices': [(1, 1, 0), (0, 0, 0, 0)]
}

result = pd.DataFrame()

for path in dataset:
    data = pd.read_csv(path)
    for column in data.columns[1:-1]:
        if column in sarima_order:
            print(f'Currently Modeling: {column}')
            model = Model(data, y=column, order=sarima_order[column][0],
                          seasonal_order=sarima_order[column][1])
            output = model.model_building()
            result = pd.concat([result, output], axis=1)

result.to_csv('./data/forecast_data.csv')
