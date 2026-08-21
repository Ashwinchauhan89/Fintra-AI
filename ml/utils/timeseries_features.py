"""
Time-Series Feature Engineering Utilities for Fintra-AI.

Provides lag extraction, rolling window statistics, cyclical date transforms,
and category proportion encoders for financial time-series forecasting.
"""

import numpy as np
import pandas as pd

ROADMAP_CATEGORIES = [
    "food",
    "shopping",
    "transport",
    "entertainment",
    "bills",
    "healthcare",
    "education",
]

LAGS = [1, 2, 3, 7, 14, 21, 30]
ROLLING_WINDOWS = [7, 14, 30]


def add_calendar_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Extracts calendar and cyclical features from a date column.
    """
    out = df.copy()
    dates = pd.to_datetime(out[date_col])

    out["day_of_week"] = dates.dt.dayofweek
    out["day_of_month"] = dates.dt.day
    out["month"] = dates.dt.month
    out["quarter"] = dates.dt.quarter
    out["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)
    out["is_month_start"] = (dates.dt.day <= 5).astype(int)
    out["is_month_end"] = (dates.dt.day >= 25).astype(int)

    # Cyclical sin/cos encodings
    out["sin_dow"] = np.sin(2 * np.pi * out["day_of_week"] / 7.0)
    out["cos_dow"] = np.cos(2 * np.pi * out["day_of_week"] / 7.0)
    out["sin_month"] = np.sin(2 * np.pi * out["month"] / 12.0)
    out["cos_month"] = np.cos(2 * np.pi * out["month"] / 12.0)
    out["sin_dom"] = np.sin(2 * np.pi * out["day_of_month"] / 31.0)
    out["cos_dom"] = np.cos(2 * np.pi * out["day_of_month"] / 31.0)

    # Payday proximity: distance in days to the 1st or 30th of the month
    dom = out["day_of_month"]
    out["days_to_payday"] = np.minimum(dom - 1, 30 - dom).clip(lower=0)

    return out


def add_lag_features(
    df: pd.DataFrame,
    target_col: str = "total_spend",
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """
    Generates historical lag features for the target column.
    """
    if lags is None:
        lags = LAGS
    out = df.copy()
    for lag in lags:
        out[f"lag_{lag}"] = out[target_col].shift(lag)
    return out


def add_rolling_features(
    df: pd.DataFrame,
    target_col: str = "total_spend",
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """
    Generates rolling window statistics (mean, std, min, max, ewm)
    shifted by 1 to prevent target data leakage.
    """
    if windows is None:
        windows = ROLLING_WINDOWS
    out = df.copy()
    shifted = out[target_col].shift(1)

    for w in windows:
        out[f"rolling_mean_{w}"] = shifted.rolling(window=w, min_periods=1).mean()
        out[f"rolling_std_{w}"] = shifted.rolling(window=w, min_periods=1).std().fillna(0.0)
        out[f"rolling_min_{w}"] = shifted.rolling(window=w, min_periods=1).min()
        out[f"rolling_max_{w}"] = shifted.rolling(window=w, min_periods=1).max()

    out["ewm_mean_7"] = shifted.ewm(span=7, min_periods=1).mean()
    out["ewm_mean_30"] = shifted.ewm(span=30, min_periods=1).mean()
    return out


def extract_forecasting_feature_names() -> list[str]:
    """
    Returns the complete list of engineered feature column names.
    """
    features = [
        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "is_weekend",
        "is_month_start",
        "is_month_end",
        "sin_dow",
        "cos_dow",
        "sin_month",
        "cos_month",
        "sin_dom",
        "cos_dom",
        "days_to_payday",
    ]
    for lag in LAGS:
        features.append(f"lag_{lag}")
    for w in ROLLING_WINDOWS:
        features.extend([
            f"rolling_mean_{w}",
            f"rolling_std_{w}",
            f"rolling_min_{w}",
            f"rolling_max_{w}",
        ])
    features.extend(["ewm_mean_7", "ewm_mean_30"])
    return features
