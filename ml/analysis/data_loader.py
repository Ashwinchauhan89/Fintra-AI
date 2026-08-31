"""
Fintra-AI Data Loader & Schema Adapter Module
Handles dataset ingestion, validation, column normalization, and fallback handling.
"""

import os
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

# Canonical Schema for Fintra-AI Transaction Analysis
CANONICAL_COLUMNS = [
    "date",
    "amount",
    "type",  # "INCOME" or "EXPENSE"
    "category",
    "merchant",
    "description",
    "account_type",
    "source",
]

ROADMAP_CATEGORIES = [
    "food",
    "shopping",
    "transport",
    "entertainment",
    "bills",
    "healthcare",
    "education",
    "salary",
    "investment",
    "other",
]

CATEGORY_MAPPINGS = {
    "online shopping": "shopping",
    "electronics": "shopping",
    "clothing": "shopping",
    "apparel": "shopping",
    "gift": "shopping",
    "beauty": "shopping",
    "grooming": "shopping",
    "food": "food",
    "grocery": "food",
    "snacks": "food",
    "lunch": "food",
    "dinner": "food",
    "milk": "food",
    "travel": "transport",
    "transport": "transport",
    "transportation": "transport",
    "train": "transport",
    "auto": "transport",
    "entertainment": "entertainment",
    "subscription": "entertainment",
    "festivals": "entertainment",
    "culture": "entertainment",
    "social life": "entertainment",
    "bills": "bills",
    "household": "bills",
    "maid": "bills",
    "rent": "bills",
    "cook": "bills",
    "documents": "bills",
    "garbage disposal": "bills",
    "healthcare": "healthcare",
    "health": "healthcare",
    "education": "education",
    "self-development": "education",
    "salary": "salary",
    "income": "salary",
    "investment": "investment",
    "emi": "bills",
}


def normalize_category(cat: Union[str, float, None]) -> str:
    """Maps arbitrary category strings to canonical Fintra-AI categories."""
    if pd.isna(cat) or not str(cat).strip():
        return "other"
    cleaned = str(cat).strip().lower()
    return CATEGORY_MAPPINGS.get(cleaned, cleaned if cleaned in ROADMAP_CATEGORIES else "other")


def validate_and_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes financial transaction data.
    Ensures safe types, valid dates, positive amounts, and handles missing fields.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

    clean_df = df.copy()

    # 1. Standardize column names (lowercase & stripped)
    clean_df.columns = [str(c).strip() for c in clean_df.columns]

    # 2. Date parsing & sorting
    if "date" in clean_df.columns or "Date" in clean_df.columns:
        col = "date" if "date" in clean_df.columns else "Date"
        clean_df["date"] = pd.to_datetime(clean_df[col], errors="coerce", format="mixed")
    else:
        clean_df["date"] = pd.NaT

    # 3. Amount parsing
    if "amount" in clean_df.columns or "Amount" in clean_df.columns:
        col = "amount" if "amount" in clean_df.columns else "Amount"
        clean_df["amount"] = pd.to_numeric(clean_df[col], errors="coerce").fillna(0.0).abs()
    else:
        clean_df["amount"] = 0.0

    # 4. Type classification (INCOME vs EXPENSE)
    if "type" in clean_df.columns:
        clean_df["type"] = clean_df["type"].astype(str).str.upper().str.strip()
        clean_df["type"] = clean_df["type"].apply(lambda x: "INCOME" if "INC" in x or "CREDIT" in x else "EXPENSE")
    elif "TransactionType" in clean_df.columns:
        clean_df["type"] = clean_df["TransactionType"].astype(str).str.upper().str.strip()
        clean_df["type"] = clean_df["type"].apply(lambda x: "INCOME" if "CREDIT" in x or "INCOME" in x else "EXPENSE")
    elif "Income/Expense" in clean_df.columns:
        clean_df["type"] = clean_df["Income/Expense"].astype(str).str.upper().str.strip()
        clean_df["type"] = clean_df["type"].apply(lambda x: "INCOME" if "INC" in x else "EXPENSE")
    else:
        # Default to EXPENSE unless category suggests income
        clean_df["type"] = "EXPENSE"

    # 5. Category normalization
    if "category" in clean_df.columns:
        clean_df["category"] = clean_df["category"].apply(normalize_category)
    elif "Category" in clean_df.columns:
        clean_df["category"] = clean_df["Category"].apply(normalize_category)
    else:
        clean_df["category"] = "other"

    # 6. Merchant / Subcategory extraction
    if "merchant" in clean_df.columns:
        clean_df["merchant"] = clean_df["merchant"].fillna("Unknown Merchant").astype(str).str.strip()
    elif "Subcategory" in clean_df.columns and "Category" in clean_df.columns:
        clean_df["merchant"] = clean_df["Subcategory"].fillna(clean_df["Category"]).fillna("Unknown Merchant").astype(str).str.strip()
    elif "Description" in clean_df.columns:
        clean_df["merchant"] = (
            clean_df["Description"]
            .astype(str)
            .str.replace(r"^Transaction at\s*", "", regex=True)
            .str.strip()
        )
    else:
        clean_df["merchant"] = "Unknown Merchant"

    # 7. Description
    if "description" in clean_df.columns:
        clean_df["description"] = clean_df["description"].fillna("").astype(str).str.strip()
    elif "Description" in clean_df.columns:
        clean_df["description"] = clean_df["Description"].fillna("").astype(str).str.strip()
    elif "Note" in clean_df.columns:
        clean_df["description"] = clean_df["Note"].fillna("").astype(str).str.strip()
    else:
        clean_df["description"] = clean_df["merchant"]

    # 8. Account Type
    if "AccountType" in clean_df.columns:
        clean_df["account_type"] = clean_df["AccountType"].fillna("Savings").astype(str).str.strip()
    elif "Mode" in clean_df.columns:
        clean_df["account_type"] = clean_df["Mode"].fillna("Current").astype(str).str.strip()
    else:
        clean_df["account_type"] = "Default Account"

    # 9. Source tracking
    if "source" not in clean_df.columns:
        clean_df["source"] = "imported_dataset"

    # Reorder and filter canonical columns
    result = clean_df[CANONICAL_COLUMNS].copy()
    result = result.sort_values(by="date", ascending=True).reset_index(drop=True)
    return result


def load_project_dataset(
    dataset_path: Optional[str] = None,
    include_raw_sources: bool = True
) -> pd.DataFrame:
    """
    Loads transactions from known project directories.
    Falls back gracefully if specific files are absent.
    """
    # If path provided directly, load it
    if dataset_path and os.path.exists(dataset_path):
        raw = pd.read_csv(dataset_path)
        return validate_and_clean_dataframe(raw)

    # Search standard project paths
    possible_paths = [
        "ml/datasets/raw/personal_finance_dataset_8000_extended.csv",
        "../ml/datasets/raw/personal_finance_dataset_8000_extended.csv",
        "../../ml/datasets/raw/personal_finance_dataset_8000_extended.csv",
        "ml/datasets/raw/Daily_Household_Transactions.csv",
        "../ml/datasets/raw/Daily_Household_Transactions.csv",
        "ml/financial_transactions_test.csv",
        "../ml/financial_transactions_test.csv",
    ]

    loaded_dfs = []
    for p in possible_paths:
        if os.path.exists(p):
            try:
                raw = pd.read_csv(p)
                cleaned = validate_and_clean_dataframe(raw)
                cleaned["source"] = os.path.basename(p)
                loaded_dfs.append(cleaned)
                if not include_raw_sources:
                    break
            except Exception as e:
                print(f"[warn] Failed reading {p}: {e}")

    if loaded_dfs:
        combined = pd.concat(loaded_dfs, ignore_index=True)
        # Drop absolute duplicates
        combined = combined.drop_duplicates(subset=["date", "amount", "merchant", "category"]).reset_index(drop=True)
        return combined

    # Return structured empty DataFrame if no files found
    return pd.DataFrame(columns=CANONICAL_COLUMNS)


def generate_sample_financial_dataset(n_records: int = 250, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic, reproducible sample dataset for demonstrations
    and testing when real data is unavailable.
    """
    np.random.seed(seed)
    start_date = pd.Timestamp("2026-01-01")
    dates = [start_date + pd.Timedelta(days=int(d), hours=int(np.random.randint(0, 24))) 
             for d in np.random.uniform(0, 180, n_records)]
    
    merchants = {
        "food": ["Zomato", "Swiggy", "Dominos", "Starbucks", "Blinkit", "BigBasket"],
        "shopping": ["Amazon", "Flipkart", "Myntra", "Zara", "Apple Store", "Ikea"],
        "transport": ["Uber", "Ola", "Metro Rail", "Petrol Station", "IRCTC"],
        "bills": ["Airtel Broadband", "Electricity Board", "House Rent", "Water Utility"],
        "entertainment": ["Netflix", "Spotify", "PVR Cinemas", "BookMyShow", "Disney+"],
        "healthcare": ["Apollo Pharmacy", "Cult.fit", "Dentist Clinic", "Diagnostic Lab"],
        "education": ["Coursera", "Udemy", "Bookstore", "ChatGPT Plus"],
        "salary": ["Tech Employer Payroll", "Consulting Direct Deposit"],
        "investment": ["Zerodha Broking", "Groww Mutual Fund"],
    }
    
    rows = []
    # Add monthly salary records
    for month in range(1, 7):
        rows.append({
            "date": pd.Timestamp(f"2026-{month:02d}-01 10:00:00"),
            "amount": 75000.0,
            "type": "INCOME",
            "category": "salary",
            "merchant": "Tech Employer Payroll",
            "description": "Monthly Salary Credit",
            "account_type": "Salary",
            "source": "synthetic_seed",
        })
        # Add a bonus in month 3
        if month == 3:
            rows.append({
                "date": pd.Timestamp(f"2026-{month:02d}-15 11:30:00"),
                "amount": 25000.0,
                "type": "INCOME",
                "category": "salary",
                "merchant": "Consulting Direct Deposit",
                "description": "Freelance Bonus Credit",
                "account_type": "Savings",
                "source": "synthetic_seed",
            })
    
    # Add expense transactions
    for date in dates:
        category = np.random.choice(
            ["food", "shopping", "transport", "bills", "entertainment", "healthcare", "education"],
            p=[0.30, 0.20, 0.15, 0.15, 0.10, 0.05, 0.05]
        )
        merchant = np.random.choice(merchants[category])
        
        # Base amounts per category
        if category == "bills":
            amount = np.random.uniform(500, 15000)
        elif category == "shopping":
            amount = np.random.uniform(300, 8000)
        elif category == "food":
            amount = np.random.uniform(100, 1500)
        elif category == "entertainment":
            amount = np.random.choice([199, 499, 649, 1499, 850])
        else:
            amount = np.random.uniform(50, 3000)
            
        rows.append({
            "date": date,
            "amount": round(float(amount), 2),
            "type": "EXPENSE",
            "category": category,
            "merchant": merchant,
            "description": f"Payment to {merchant}",
            "account_type": np.random.choice(["Savings", "Current", "Credit Card"]),
            "source": "synthetic_seed",
        })

    df = pd.DataFrame(rows)
    return validate_and_clean_dataframe(df)
