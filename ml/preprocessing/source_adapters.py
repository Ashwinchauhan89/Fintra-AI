import os

import pandas as pd

UNIFIED_COLUMNS = ["merchant", "description", "amount", "category", "date", "source"]


# ---------------------------------------------------------------------------
# Adapter 1: the original small toy file
# (expense_id, amount, merchant, description, category)
# ---------------------------------------------------------------------------
TOY_CATEGORY_MAP = {
    "food": "food",
    "shopping": "shopping",
    "technology": "shopping",  # not a roadmap category; folded into shopping
    "transport": "transport",
    "entertainment": "entertainment",
}


def adapt_toy(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "merchant": df["merchant"],
        "description": df["description"],
        "amount": pd.to_numeric(df["amount"], errors="coerce"),
        "category": df["category"].str.lower().str.strip().map(TOY_CATEGORY_MAP),
        "date": pd.NaT,
        "source": "toy",
    })
    return out


# ---------------------------------------------------------------------------
# Adapter 2: personal_finance_dataset_8000_extended.csv
# (Date, Description, Amount, Category, PaymentMethod, ..., MerchantType, ...)
# Description looks like "Transaction at Amazon" — merchant is embedded.
# ---------------------------------------------------------------------------
FINANCE_8000_CATEGORY_MAP = {
    "online shopping": "shopping",
    "electronics": "shopping",
    "clothing": "shopping",
    "entertainment": "entertainment",
    "food": "food",
    "grocery": "food",
    "healthcare": "healthcare",
    "travel": "transport",
    "bills": "bills",
    "transport": "transport",
}


def adapt_finance_8000(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Only genuine spending; a Credit row here would be a refund/income.
    if "TransactionType" in df.columns:
        df = df[df["TransactionType"].str.lower() == "debit"]

    merchant = (
        df["Description"]
        .str.replace(r"^Transaction at\s*", "", regex=True)
        .str.strip()
    )
    # MerchantType (Retail / Online Store / Service ...) is a second,
    # genuinely independent text signal — not just the merchant name again.
    description = df.get("MerchantType", pd.Series("", index=df.index))

    out = pd.DataFrame({
        "merchant": merchant,
        "description": description,
        "amount": pd.to_numeric(df["Amount"], errors="coerce"),
        "category": df["Category"].str.lower().str.strip().map(FINANCE_8000_CATEGORY_MAP),
        "date": pd.to_datetime(df["Date"], errors="coerce"),
        "source": "finance_8000",
    })
    return out


# ---------------------------------------------------------------------------
# Adapter 3: Daily_Household_Transactions.csv
# (Date, Mode, Category, Subcategory, Note, Amount, Income/Expense, Currency)
# No merchant column at all — real ledger data, not brand transactions.
# ---------------------------------------------------------------------------
HOUSEHOLD_CATEGORY_MAP = {
    "food": "food",
    "transportation": "transport",
    "household": "bills",
    "subscription": "entertainment",
    "health": "healthcare",
    "apparel": "shopping",
    "gift": "shopping",
    "beauty": "shopping",
    "grooming": "shopping",
    "education": "education",
    "self-development": "education",
    "maid": "bills",
    "festivals": "entertainment",
    "culture": "entertainment",
    "tourism": "transport",
    "rent": "bills",
    "cook": "bills",
    "water (jar /tanker)": "bills",
    "documents": "bills",
    "garbage disposal": "bills",
    "social life": "entertainment",
    # Explicitly NOT spending categories — dropped, not defaulted:
    # "other", "investment", "family", "money transfer",
    # "recurring deposit", "public provident fund"
}


def adapt_household(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["Income/Expense"].str.strip().str.lower() == "expense"]

    merchant = df["Subcategory"].fillna(df["Category"])
    description = df["Note"].fillna(df["Subcategory"]).fillna(df["Category"])

    out = pd.DataFrame({
        "merchant": merchant,
        "description": description,
        "amount": pd.to_numeric(df["Amount"], errors="coerce"),
        "category": df["Category"].str.lower().str.strip().map(HOUSEHOLD_CATEGORY_MAP),
        "date": pd.to_datetime(df["Date"], errors="coerce", dayfirst=True),
        "source": "household",
    })
    return out


# ---------------------------------------------------------------------------
# Detection: which adapter applies to a given raw file, by column signature
# ---------------------------------------------------------------------------
SOURCE_ADAPTERS = [
    # (required columns to identify this schema, adapter function, name)
    ({"expense_id", "merchant", "description", "category"}, adapt_toy, "toy"),
    ({"Description", "MerchantType", "TransactionType"}, adapt_finance_8000, "finance_8000"),
    ({"Mode", "Subcategory", "Income/Expense"}, adapt_household, "household"),
]


def detect_adapter(columns: set):
    for required_cols, adapter_fn, name in SOURCE_ADAPTERS:
        if required_cols.issubset(columns):
            return adapter_fn, name
    return None, None


def load_and_unify(raw_dir: str) -> pd.DataFrame:
    """
    Reads every CSV in raw_dir, applies the matching adapter, drops
    rows whose category didn't map to the canonical set, and
    concatenates everything into one unified DataFrame.
    """
    csv_paths = sorted(
        os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(".csv")
    )
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    frames = []
    for path in csv_paths:
        raw = pd.read_csv(path)
        adapter_fn, name = detect_adapter(set(raw.columns))
        if adapter_fn is None:
            print(f"[warn] Skipping {os.path.basename(path)} — "
                  f"no matching adapter for its columns: {list(raw.columns)}")
            continue

        unified = adapter_fn(raw)
        before = len(unified)
        unmapped = unified["category"].isna().sum()
        unified = unified.dropna(subset=["category", "merchant", "amount"])
        print(f"[info] {os.path.basename(path)} ({name}): "
              f"{before} rows -> {len(unified)} kept, "
              f"{unmapped} dropped (unmapped/invalid category)")
        frames.append(unified[UNIFIED_COLUMNS])

    combined = pd.concat(frames, ignore_index=True)
    print(f"[info] Combined total: {len(combined)} rows from {len(frames)} source(s)")
    print(f"[info] Category counts:\n{combined['category'].value_counts()}")
    print(f"[info] Rows per source:\n{combined['source'].value_counts()}")
    return combined
