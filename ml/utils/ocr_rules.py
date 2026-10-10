"""
OCR Receipt Intelligence, NLP Entity Extraction & Normalization Utilities for Phase 15.

Provides:
- Robust Header Cleaner & Merchant Extractor
- Multi-format ISO Date Normalizer
- Total Amount & GST Breakdown Extractor
- Payment Mode Identifier
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 1. Compiled Regex Patterns for Financial Entities
# ---------------------------------------------------------------------------

CURRENCY_SYMBOLS = r"(?:₹|INR|Rs\.?|USD|\$|EUR|€|GBP|£)"

TOTAL_KEYWORDS = [
    r"grand\s*total",
    r"net\s*payable",
    r"total\s*amount",
    r"amount\s*payable",
    r"balance\s*due",
    r"total\s*due",
    r"final\s*amount",
    r"invoice\s*total",
    r"bill\s*total",
    r"total\s*inr",
    r"total\s*rs",
    r"total",
]

TOTAL_PATTERN = re.compile(
    rf"(?:{'|'.join(TOTAL_KEYWORDS)})\s*[:=\-]?\s*{CURRENCY_SYMBOLS}?\s*([\d,]+\.?\d{{0,2}})",
    re.IGNORECASE,
)

GENERIC_AMOUNT_PATTERN = re.compile(
    rf"{CURRENCY_SYMBOLS}?\s*([\d,]+\.\d{{2}})",
    re.IGNORECASE,
)

TAX_KEYWORDS = [
    r"cgst",
    r"sgst",
    r"igst",
    r"gst",
    r"vat",
    r"tax",
    r"service\s*charge",
]

TAX_PATTERN = re.compile(
    rf"(?:{'|'.join(TAX_KEYWORDS)})\s*(?:\(\d+%\)|\d+%)?\s*[:=\-]?\s*{CURRENCY_SYMBOLS}?\s*([\d,]+\.?\d{{0,2}})",
    re.IGNORECASE,
)

PAYMENT_MODE_PATTERNS = [
    (re.compile(r"\b(upi|gpay|google[_\s]*pay|phonepe|paytm|bhim)\b", re.IGNORECASE), "UPI"),
    (re.compile(r"\b(credit[_\s]*card|visa|mastercard|amex|rupay)\b", re.IGNORECASE), "CREDIT_CARD"),
    (re.compile(r"\b(debit[_\s]*card|pos[_\s]*debit)\b", re.IGNORECASE), "DEBIT_CARD"),
    (re.compile(r"\b(cash|cash[_\s]*tendered|cash[_\s]*paid)\b", re.IGNORECASE), "CASH"),
    (re.compile(r"\b(net[_\s]*banking|neft|rtgs|imps|online[_\s]*transfer)\b", re.IGNORECASE), "NET_BANKING"),
]

HEADER_NOISE_TERMS = [
    "tax invoice",
    "retail invoice",
    "bill of supply",
    "cash receipt",
    "welcome to",
    "original copy",
    "duplicate copy",
    "customer copy",
    "merchant copy",
    "gstin",
    "cin:",
    "phone:",
    "tel:",
    "email:",
    "bill no",
    "invoice no",
]

# ---------------------------------------------------------------------------
# 2. Entity Extraction & Normalization Functions
# ---------------------------------------------------------------------------

def clean_amount_str(amt_str: str) -> float:
    """
    Cleans string numbers with commas and converts to float.
    """
    cleaned = amt_str.replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_merchant_name(text_lines: List[str]) -> Tuple[str, float]:
    """
    Extracts clean merchant name from top lines of the receipt.
    Returns (merchant_name, confidence).
    """
    candidates = []
    for line in text_lines[:10]:
        # Strip decorative symbols (*, =, -, #, ~, _, :)
        line_clean = re.sub(r"^[\*\=\-\#\~\_\:\s]+|[\*\=\-\#\~\_\:\s]+$", "", line).strip()
        if not line_clean or len(line_clean) < 3 or len(line_clean) > 60:
            continue

        lower_line = line_clean.lower()

        # Skip noise lines
        if any(noise in lower_line for noise in HEADER_NOISE_TERMS):
            continue

        # Filter out lines that are purely numbers or dates or times
        if re.match(r"^[\d\s\-/.:,apmAPM]+$", line_clean):
            continue

        # Check if line looks like Indian GSTIN
        if re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}", line_clean):
            continue

        # Clean merchant suffixes
        merchant_name = re.sub(
            r"\s+(pvt\.?\s*ltd\.?|private\s+limited|limited|store\s*#?\d+|outlet\s*#?\d+|branch|restaurant|cafe)$",
            "",
            line_clean,
            flags=re.IGNORECASE,
        ).strip()

        if merchant_name:
            candidates.append(merchant_name)

    if candidates:
        return candidates[0], 0.98
    return "Unknown Merchant", 0.30


def extract_total_amount(text: str) -> Tuple[float, float]:
    """
    Extracts the grand total / final payable amount with anchor prioritization.
    Returns (total_amount, confidence).
    """
    lines = text.split("\n")
    # 1. Search for keyword anchored totals first
    for line in reversed(lines):
        match = TOTAL_PATTERN.search(line)
        if match:
            amt = clean_amount_str(match.group(1))
            if amt > 0:
                return amt, 0.99

    # 2. Fallback: Search all lines matching currency or numbers, pick the highest reasonable amount
    all_amounts = []
    for line in lines:
        matches = GENERIC_AMOUNT_PATTERN.findall(line)
        for m in matches:
            amt = clean_amount_str(m)
            if 0 < amt < 500000.0:  # Reasonable transaction ceiling
                all_amounts.append(amt)

    if all_amounts:
        return max(all_amounts), 0.75

    return 0.0, 0.0


def extract_transaction_date(text: str) -> Tuple[str, float]:
    """
    Extracts transaction date and normalizes to ISO 8601 (YYYY-MM-DD).
    Returns (iso_date_str, confidence).
    """
    # 1. Date prefixed pattern: Date:\s*...
    date_prefix_match = re.search(r"date\s*[:=\-]?\s*([0-9a-zA-Z\s/.-]{6,20})", text, re.IGNORECASE)
    search_text = date_prefix_match.group(1) if date_prefix_match else text

    # Word format: 25 Aug 2026 or 25-Aug-2026
    word_match = re.search(
        r"\b(\d{1,2})[\s/-]+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s/-]+(\d{4})\b",
        search_text,
        re.IGNORECASE,
    )
    if word_match:
        try:
            day = int(word_match.group(1))
            month_str = word_match.group(2).capitalize()
            year = int(word_match.group(3))
            dt = datetime.strptime(f"{day:02d} {month_str} {year}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d"), 0.99
        except Exception:
            pass

    # Standard DD/MM/YYYY or DD-MM-YYYY (e.g. 25/08/2026)
    dmy_match = re.search(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b", search_text)
    if dmy_match:
        try:
            day = int(dmy_match.group(1))
            month = int(dmy_match.group(2))
            year = int(dmy_match.group(3))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}", 0.99
        except Exception:
            pass

    # ISO YYYY-MM-DD (e.g. 2026-08-25)
    iso_match = re.search(r"\b(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})\b", search_text)
    if iso_match:
        try:
            year = int(iso_match.group(1))
            month = int(iso_match.group(2))
            day = int(iso_match.group(3))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}", 0.99
        except Exception:
            pass

    # Fallback to current date
    return datetime.now().strftime("%Y-%m-%d"), 0.50


def extract_line_item_summary(text_lines: List[str]) -> str:
    """
    Extracts the most prominent purchased item description to assist Phase 3 Category classification.
    """
    candidates = []
    for line in text_lines:
        line_clean = line.strip()
        # Look for item lines with price at the end: e.g. "Basmati Rice 5kg    450.00"
        match = re.match(r"^([a-zA-Z0-9\s#\+\-\(\)]{3,30})\s+[\d,]+\.\d{2}$", line_clean)
        if match:
            item_text = match.group(1).strip()
            lower_item = item_text.lower()
            if not any(k in lower_item for k in ["total", "subtotal", "gst", "cgst", "sgst", "bill", "paid"]):
                candidates.append(item_text)

    if candidates:
        return ", ".join(candidates[:3])
    return ""


def extract_tax_breakdown(text: str) -> Dict[str, float]:
    """
    Extracts GST / Tax amount breakdown.
    """
    tax_total = 0.0
    for line in text.split("\n"):
        match = TAX_PATTERN.search(line)
        if match:
            amt = clean_amount_str(match.group(1))
            tax_total += amt

    return {"tax_amount_inr": round(tax_total, 2)}


def extract_payment_mode(text: str) -> str:
    """
    Identifies payment mode (UPI, CREDIT_CARD, DEBIT_CARD, CASH, NET_BANKING).
    """
    for pattern, mode in PAYMENT_MODE_PATTERNS:
        if pattern.search(text):
            return mode
    return "UNKNOWN"
