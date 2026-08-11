import re
import string


def clean_text(text: str) -> str:
    """
    Lowercase, strip punctuation/extra whitespace from a text field.

    Used on both `merchant` and `description` before combining them.
    """
    if text is None:
        return ""
    text = str(text).lower().strip()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_text_feature(merchant: str, description: str) -> str:
    """
    Combine merchant + description into the single text field the
    vectorizer operates on. Merchant is repeated once extra — in
    practice it's often the single strongest signal (e.g. "Swiggy"
    almost always means Food), so giving it slightly more weight in
    the bag-of-words tends to help on small/noisy datasets.
    """
    merchant_clean = clean_text(merchant)
    description_clean = clean_text(description)
    return f"{merchant_clean} {merchant_clean} {description_clean}".strip()


# Note: amount bucketing now lives in utils/amount_bucketizer.py
# (AmountBucketizer) — fixed thresholds broke once we combined
# datasets with amounts ranging from ~2 to ~150,000. See that module
# for the quantile-based replacement, fit on the training set only.
