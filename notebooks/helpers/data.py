import pandas as pd
import numpy as np

from statsmodels.stats.weightstats import _tconfint_generic
from sklearn.neighbors import KNeighborsRegressor


def fix_predicted_price(data, features, target_name, tresh_hold):
    knn = KNeighborsRegressor(n_neighbors=3)

    good_price = data[data[target_name] > tresh_hold]
    low_price = data[data[target_name] < tresh_hold]

    knn.fit(good_price[features], good_price[target_name])
    low_price[target_name] = knn.predict(low_price[features])

    return pd.concat([good_price, low_price])


def confidence_interval(actual_price, predicted_price):
    reg_error = (actual_price - predicted_price)

    # доверительный интервал для ошибок модели
    err_mean = reg_error.mean()
    err_mean_std = reg_error.std(ddof=1) / np.sqrt(len(reg_error))

    return _tconfint_generic(err_mean, err_mean_std, len(reg_error) - 1, 0.05, 'two-sided')