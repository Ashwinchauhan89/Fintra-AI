import argparse
import os
import sys
from functools import lru_cache

import joblib
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.text_utils import build_text_feature  # noqa: E402
from utils.amount_bucketizer import AmountBucketizer  # noqa: E402

DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Below this confidence, the app should treat the prediction as a
# suggestion rather than auto-filling silently — surface it to the
# user as "we think this is Food — confirm?" instead of committing
# it outright. Tune this once you have real usage data.
LOW_CONFIDENCE_THRESHOLD = 0.45


@lru_cache(maxsize=1)
def _load_artifacts(model_dir: str = DEFAULT_MODEL_DIR):
    """
    Loads the model + label encoder once per process and caches them.
    Avoids re-reading from disk on every single prediction, which
    matters once this sits behind an API endpoint taking real traffic.
    """
    model_path = os.path.join(model_dir, "best_model.pkl")
    encoder_path = os.path.join(model_dir, "label_encoder.pkl")
    bucketizer_path = os.path.join(model_dir, "amount_bucketizer.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model at {model_path}. Run training/train.py first."
        )
    pipeline = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
    bucketizer = AmountBucketizer.load(bucketizer_path)
    is_text_only = list(pipeline.named_steps.keys())[0] == "tfidf"
    return pipeline, label_encoder, bucketizer, is_text_only


def predict_category(
    merchant: str,
    description: str,
    amount: float,
    date: str | None = None,
    model_dir: str = DEFAULT_MODEL_DIR,
) -> dict:
    """
    Predicts an expense category for a single transaction.

    Args:
        merchant: e.g. "Swiggy"
        description: e.g. "dinner order"
        amount: e.g. 450.0
        date: optional ISO date string, e.g. "2026-08-10" — only used
            if the model was trained with a date/day_of_week feature.
        model_dir: override for where models are loaded from
            (mainly for testing).

    Returns:
        {"category": str, "confidence": float}
        confidence is None if the underlying model doesn't support
        predict_proba.
    """
    pipeline, label_encoder, bucketizer, is_text_only = _load_artifacts(model_dir)

    text_feature = build_text_feature(merchant, description)
    bucket = bucketizer.transform([float(amount)])[0]

    day_of_week = -1
    if date:
        parsed = pd.to_datetime(date, errors="coerce")
        if pd.notna(parsed):
            day_of_week = int(parsed.dayofweek)

    if is_text_only:
        X = pd.Series([text_feature])
    else:
        X = pd.DataFrame([{
            "text_feature": text_feature,
            "amount_bucket": bucket,
            "day_of_week": day_of_week,
        }])

    pred_encoded = pipeline.predict(X)[0]
    category = label_encoder.inverse_transform([pred_encoded])[0]

    confidence = None
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)[0]
        confidence = float(proba.max())

    result = {"category": category, "confidence": confidence}
    if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
        result["low_confidence"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description="Predict an expense category")
    parser.add_argument("--merchant", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--amount", required=True, type=float)
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    result = predict_category(
        args.merchant, args.description, args.amount, args.date
    )
    print(result)


if __name__ == "__main__":
    main()
