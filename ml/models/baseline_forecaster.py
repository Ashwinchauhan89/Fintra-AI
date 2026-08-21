"""
Seasonal Baseline Regressor for Financial Time-Series Forecasting.

Provides a robust moving average baseline with day-of-week seasonality multipliers.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin


class SeasonalBaselineRegressor(BaseEstimator, RegressorMixin):
    """
    Seasonal Moving Average baseline estimator.
    Uses rolling 7-day average combined with day-of-week historical multipliers.
    """

    def __init__(self, window: int = 7):
        self.window = window
        self.dow_multipliers_ = {}
        self.global_mean_ = 0.0

    def fit(self, X, y):
        y_arr = np.asarray(y, dtype=float)
        self.global_mean_ = float(np.mean(y_arr)) if len(y_arr) > 0 else 0.0

        if isinstance(X, pd.DataFrame) and "day_of_week" in X.columns:
            dow_series = X["day_of_week"]
            grouped = pd.Series(y_arr).groupby(dow_series.values).mean()
            for dow in range(7):
                dow_mean = grouped.get(dow, self.global_mean_)
                self.dow_multipliers_[dow] = float(dow_mean / (self.global_mean_ + 1e-6))
        else:
            self.dow_multipliers_ = {i: 1.0 for i in range(7)}
        return self

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            if "rolling_mean_7" in X.columns:
                base = X["rolling_mean_7"].fillna(self.global_mean_).values
            elif "lag_1" in X.columns:
                base = X["lag_1"].fillna(self.global_mean_).values
            else:
                base = np.full(len(X), self.global_mean_)

            if "day_of_week" in X.columns:
                mults = np.array([self.dow_multipliers_.get(int(d), 1.0) for d in X["day_of_week"]])
                return np.maximum(0.0, base * mults)
            return np.maximum(0.0, base)
        return np.full(len(X), self.global_mean_)
