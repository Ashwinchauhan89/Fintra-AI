"""
Inference Pipeline for Financial Time-Series & Cash Flow Forecasting (Phases 4 & 18).

Provides multi-day expense trajectory projections, granular category breakdown,
and net cash flow balance simulations with confidence intervals.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.baseline_forecaster import SeasonalBaselineRegressor  # noqa: F401, E402
from utils.timeseries_features import (  # noqa: E402
    ROADMAP_CATEGORIES,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    extract_forecasting_feature_names,
)

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
DEFAULT_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")


@lru_cache(maxsize=1)
def load_forecasting_artifacts(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads and caches trained forecasting models, category forecasters, and metadata.
    """
    best_model_path = os.path.join(model_dir, "forecasting_best_model.pkl")
    cat_models_path = os.path.join(model_dir, "forecasting_categories.pkl")
    meta_path = os.path.join(model_dir, "forecasting_train_metrics.json")

    if not os.path.exists(best_model_path):
        raise FileNotFoundError(
            f"Forecasting model not found at {best_model_path}. Run training/train_forecasting.py first."
        )

    model = joblib.load(best_model_path)
    category_models = joblib.load(cat_models_path) if os.path.exists(cat_models_path) else {}

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)

    return model, category_models, meta


def get_recent_history(
    lookback_days: int = 60,
    processed_dir: str = DEFAULT_PROCESSED_DIR,
) -> pd.DataFrame:
    """
    Loads recent historical continuous daily series needed to bootstrap lags & rolling features.
    """
    test_path = os.path.join(processed_dir, "forecasting_test.csv")
    train_path = os.path.join(processed_dir, "forecasting_train.csv")

    if os.path.exists(test_path):
        df = pd.read_csv(test_path)
    elif os.path.exists(train_path):
        df = pd.read_csv(train_path)
    else:
        raise FileNotFoundError(
            f"No processed forecasting history found in {processed_dir}. "
            "Run preprocessing/preprocess_forecasting.py first."
        )

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").tail(lookback_days).copy()
    return df


def predict_expense_forecast(
    horizon_days: int = 30,
    start_date: str | None = None,
    history_df: pd.DataFrame | None = None,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> dict:
    """
    Generates multi-day forward forecast of daily expenses and category distribution.

    Args:
        horizon_days: Number of days to forecast into the future (e.g. 7, 30, 90).
        start_date: ISO date string for start of forecast (defaults to day after history end).
        history_df: Optional custom historical daily DataFrame with 'date' and 'total_spend'.
        model_dir: Directory containing saved model artifacts.

    Returns:
        Structured dictionary containing total predicted spend, daily trajectory,
        category breakdown, and weekly summaries.
    """
    if not isinstance(horizon_days, int) or horizon_days <= 0:
        raise ValueError("horizon_days must be a positive integer")

    model, category_models, meta = load_forecasting_artifacts(model_dir)

    if history_df is None:
        history = get_recent_history(lookback_days=60)
    else:
        history = history_df.copy()
        required_columns = {"date", "total_spend"}
        missing_columns = required_columns - set(history.columns)
        if missing_columns:
            raise ValueError(
                f"history_df is missing required columns: {sorted(missing_columns)}"
            )
        history["date"] = pd.to_datetime(history["date"], errors="coerce")
        history["total_spend"] = pd.to_numeric(history["total_spend"], errors="coerce")
        history = history.dropna(subset=["date", "total_spend"]).sort_values("date")

    if history.empty:
        raise ValueError("At least one valid historical spending row is required")

    history_series = list(history["total_spend"].values)
    history_dates = list(history["date"].values)

    if start_date is not None:
        current_date = pd.to_datetime(start_date)
    else:
        current_date = pd.to_datetime(history_dates[-1]) + timedelta(days=1)

    daily_predictions = []
    feature_rows = []
    feature_cols = extract_forecasting_feature_names()

    # Recursive multi-step forward projection
    for step in range(horizon_days):
        step_date = current_date + timedelta(days=step)

        # Temporary frame to construct current lag/rolling features
        temp_history = pd.DataFrame({
            "date": pd.to_datetime(history_dates[-60:]),
            "total_spend": history_series[-60:],
        })

        # Append the new row to predict
        new_row = pd.DataFrame({"date": [step_date], "total_spend": [np.nan]})
        combined = pd.concat([temp_history, new_row], ignore_index=True)

        combined = add_calendar_features(combined, date_col="date")
        combined = add_lag_features(combined, target_col="total_spend")
        combined = add_rolling_features(combined, target_col="total_spend")

        pred_row = combined.iloc[[-1]]
        X_step = pred_row[[c for c in feature_cols if c in pred_row.columns]]
        if X_step.shape[1] != len(feature_cols):
            missing_features = sorted(set(feature_cols) - set(X_step.columns))
            raise ValueError(f"Forecast feature columns are missing: {missing_features}")
        feature_rows.append(X_step.copy())

        pred_val = float(np.maximum(0.0, model.predict(X_step)[0]))

        # Calculate prediction interval (approx. 80% confidence interval based on recent volatility)
        rolling_std = float(pred_row["rolling_std_7"].values[0]) if "rolling_std_7" in pred_row else pred_val * 0.25
        lower_bound = max(0.0, pred_val - 1.28 * rolling_std)
        upper_bound = pred_val + 1.28 * rolling_std

        daily_predictions.append({
            "date": step_date.strftime("%Y-%m-%d"),
            "day_name": step_date.strftime("%A"),
            "predicted_spend": round(pred_val, 2),
            "lower_bound_80": round(lower_bound, 2),
            "upper_bound_80": round(upper_bound, 2),
        })

        # Append prediction into rolling series for next step autoregression
        history_series.append(pred_val)
        history_dates.append(step_date)

    total_predicted = sum(d["predicted_spend"] for d in daily_predictions)

    # Compute category-wise breakdown across the forecast period
    category_forecast = {}
    if category_models:
        for cat, cat_model in category_models.items():
            cat_preds = []
            for X_day in feature_rows:
                cat_spend = float(np.maximum(0.0, cat_model.predict(X_day)[0]))
                cat_preds.append(cat_spend)
            cat_sum = sum(cat_preds)
            category_forecast[cat] = round(cat_sum, 2)
    else:
        # Default distribution fallback
        default_shares = {
            "food": 0.25,
            "shopping": 0.25,
            "bills": 0.20,
            "transport": 0.15,
            "entertainment": 0.08,
            "healthcare": 0.05,
            "education": 0.02,
        }
        for cat, share in default_shares.items():
            category_forecast[cat] = round(total_predicted * share, 2)

    # Normalize category totals to sum to total_predicted
    cat_total = sum(category_forecast.values())
    if cat_total > 0:
        category_breakdown = {
            cat: {
                "amount": round((amt / cat_total) * total_predicted, 2),
                "percentage": round((amt / cat_total) * 100.0, 1),
            }
            for cat, amt in category_forecast.items()
        }
    else:
        category_breakdown = {}

    # Weekly summary aggregation
    weekly_buckets = []
    for w in range(0, horizon_days, 7):
        week_chunk = daily_predictions[w : w + 7]
        week_total = sum(d["predicted_spend"] for d in week_chunk)
        weekly_buckets.append({
            "week_number": (w // 7) + 1,
            "start_date": week_chunk[0]["date"],
            "end_date": week_chunk[-1]["date"],
            "total_spend": round(week_total, 2),
        })

    return {
        "status": "success",
        "forecast_period": {
            "horizon_days": horizon_days,
            "start_date": daily_predictions[0]["date"],
            "end_date": daily_predictions[-1]["date"],
        },
        "total_predicted_expense": round(total_predicted, 2),
        "daily_average_expense": round(total_predicted / horizon_days, 2) if horizon_days else 0.0,
        "weekly_summary": weekly_buckets,
        "category_breakdown": category_breakdown,
        "daily_forecast": daily_predictions,
    }


def predict_cash_flow(
    monthly_income: float = 60000.0,
    current_balance: float = 25000.0,
    horizon_days: int = 30,
    payday_of_month: int = 1,
    history_df: pd.DataFrame | None = None,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> dict:
    """
    Simulates forward cash flow and net account balance trajectory.

    Args:
        monthly_income: User's expected monthly net income in INR.
        current_balance: Current starting balance in INR.
        horizon_days: Simulation horizon in days.
        payday_of_month: Day of the month when salary is credited.
    """
    expense_res = predict_expense_forecast(
        horizon_days=horizon_days,
        history_df=history_df,
        model_dir=model_dir,
    )
    daily_spend = expense_res["daily_forecast"]

    balance = float(current_balance)
    cash_flow_trajectory = []
    total_income_credited = 0.0
    min_projected_balance = balance
    deficit_dates = []

    for item in daily_spend:
        d = pd.to_datetime(item["date"])
        income_today = 0.0

        # Credit income on salary payday
        if d.day == payday_of_month or (payday_of_month > 28 and d.is_month_end):
            income_today = monthly_income
            total_income_credited += income_today

        spend_today = item["predicted_spend"]
        net_delta = income_today - spend_today
        balance += net_delta

        if balance < min_projected_balance:
            min_projected_balance = balance

        if balance < 0:
            deficit_dates.append(item["date"])

        cash_flow_trajectory.append({
            "date": item["date"],
            "income": income_today,
            "expense": spend_today,
            "net_flow": round(net_delta, 2),
            "projected_balance": round(balance, 2),
        })

    total_expense = expense_res["total_predicted_expense"]
    net_savings = total_income_credited - total_expense
    savings_rate = round((net_savings / total_income_credited) * 100.0, 1) if total_income_credited > 0 else 0.0

    # Generate actionable financial insight
    if len(deficit_dates) > 0:
        health_status = "Risk of Cash Deficit"
        recommendation = f"Alert: Projected balance goes negative around {deficit_dates[0]}. Consider reducing discretionary spending."
    elif savings_rate >= 20.0:
        health_status = "Healthy Surplus"
        recommendation = f"Excellent! Projected savings rate is {savings_rate}%. You have room to allocate funds towards savings or investments."
    else:
        health_status = "Tight Budget"
        recommendation = f"Moderate cash flow. Projected savings rate is {savings_rate}%. Monitor high-spend categories."

    return {
        "status": "success",
        "initial_balance": current_balance,
        "monthly_income": monthly_income,
        "projected_total_income": round(total_income_credited, 2),
        "projected_total_expense": round(total_expense, 2),
        "projected_net_savings": round(net_savings, 2),
        "savings_rate_pct": savings_rate,
        "final_projected_balance": round(balance, 2),
        "minimum_projected_balance": round(min_projected_balance, 2),
        "health_status": health_status,
        "recommendation": recommendation,
        "category_breakdown": expense_res["category_breakdown"],
        "cash_flow_trajectory": cash_flow_trajectory,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Expense & Cash Flow Forecasts")
    parser.add_argument("--horizon", type=int, default=30, help="Forecast horizon in days (default: 30)")
    parser.add_argument("--income", type=float, default=60000.0, help="Monthly income in INR (default: 60000)")
    parser.add_argument("--balance", type=float, default=25000.0, help="Current starting balance (default: 25000)")
    parser.add_argument("--payday", type=int, default=1, help="Day of month when income is credited (default: 1)")
    parser.add_argument("--mode", choices=["expense", "cashflow"], default="cashflow", help="Forecast mode")
    parser.add_argument("--json", action="store_true", help="Print raw JSON output")
    args = parser.parse_args()

    if args.mode == "expense":
        result = predict_expense_forecast(horizon_days=args.horizon)
    else:
        result = predict_cash_flow(
            monthly_income=args.income,
            current_balance=args.balance,
            horizon_days=args.horizon,
            payday_of_month=args.payday,
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 65)
        print("FINTRA-AI EXPENSE & CASH FLOW FORECAST REPORT")
        print("=" * 65)
        print(f"Horizon:                   {args.horizon} Days")
        print(f"Starting Balance:          INR {result['initial_balance']:,.2f}")
        print(f"Projected Income:          INR {result['projected_total_income']:,.2f}")
        print(f"Projected Expenses:        INR {result['projected_total_expense']:,.2f}")
        print(f"Projected Net Savings:     INR {result['projected_net_savings']:,.2f} ({result['savings_rate_pct']}%)")
        print(f"Final Projected Balance:   INR {result['final_projected_balance']:,.2f}")
        print(f"Lowest Balance Dip:        INR {result['minimum_projected_balance']:,.2f}")
        print(f"Financial Status:          {result['health_status']}")
        print(f"AI Recommendation:         {result['recommendation']}")
        print("\n" + "-" * 65)
        print("PROJECTED CATEGORY BREAKDOWN")
        print("-" * 65)
        for cat, data in result["category_breakdown"].items():
            print(f"  * {cat.capitalize():<15}: INR {data['amount']:>10,.2f} ({data['percentage']}%)")
        print("=" * 65)


if __name__ == "__main__":
    main()
