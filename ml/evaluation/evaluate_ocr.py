"""
Held-Out Test Set Evaluation Pipeline for Phase 15: OCR Receipt Intelligence.

Evaluates on 200 held-out test receipts across all financial metrics:
- Total Amount Extraction Accuracy
- ISO 8601 Date Normalization Accuracy
- Clean Merchant Name Recognition Accuracy
- Payment Mode Accuracy
- Phase 3 Expense Category Classification Accuracy
- Average End-to-End Latency
"""

import json
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from inference.predict import predict_category  # noqa: E402
from utils.ocr_rules import (  # noqa: E402
    extract_line_item_summary,
    extract_merchant_name,
    extract_payment_mode,
    extract_tax_breakdown,
    extract_total_amount,
    extract_transaction_date,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "ocr_receipts_test.json")


def main():
    print("=" * 85)
    print("Phase 15: OCR Receipt Intelligence — Held-Out Test Evaluation")
    print("=" * 85)

    if not os.path.exists(TEST_FILE):
        print(f"[error] Test file not found: {TEST_FILE}")
        sys.exit(1)

    with open(TEST_FILE, "r") as f:
        test_records = json.load(f)

    print(f"[info] Evaluating on {len(test_records)} held-out test receipts...\n")

    total_correct = 0
    date_correct = 0
    merchant_correct = 0
    payment_correct = 0
    category_correct = 0

    t_start = time.perf_counter()

    for rec in test_records:
        raw_text = rec["raw_text"]
        gt = rec["ground_truth"]
        lines = raw_text.split("\n")

        # 1. Total Amount
        pred_total, _ = extract_total_amount(raw_text)
        if abs(pred_total - gt["total_amount"]) < 0.05:
            total_correct += 1

        # 2. Date
        pred_date, _ = extract_transaction_date(raw_text)
        if pred_date == gt["date"]:
            date_correct += 1

        # 3. Merchant
        pred_merchant, _ = extract_merchant_name(lines)
        if pred_merchant.lower() in gt["merchant"].lower() or gt["merchant"].lower() in pred_merchant.lower():
            merchant_correct += 1

        # 4. Payment Mode
        pred_pm = extract_payment_mode(raw_text)
        if pred_pm == gt["payment_mode"]:
            payment_correct += 1

        # 5. Integrated Category Prediction (Phase 3 Model)
        item_summary = extract_line_item_summary(lines)
        cat_desc = f"{pred_merchant} {item_summary}" if item_summary else pred_merchant
        cat_res = predict_category(
            merchant=pred_merchant,
            description=cat_desc,
            amount=pred_total,
            date=pred_date,
        )
        pred_cat = cat_res.get("category", "")
        if pred_cat == gt["category"]:
            category_correct += 1

    total_time_ms = (time.perf_counter() - t_start) * 1000.0
    n = len(test_records)
    avg_latency_ms = total_time_ms / n

    print("=================================================================")
    print(f"Total Amount Extraction Accuracy:      {(total_correct / n) * 100:5.2f}% (Benchmark >= 98.0%)")
    print(f"ISO Date Normalization Accuracy:       {(date_correct / n) * 100:5.2f}% (Benchmark >= 98.0%)")
    print(f"Merchant Name Recognition Accuracy:    {(merchant_correct / n) * 100:5.2f}% (Benchmark >= 95.0%)")
    print(f"Payment Mode Identification Accuracy:  {(payment_correct / n) * 100:5.2f}%")
    print(f"Phase 3 Expense Category Accuracy:     {(category_correct / n) * 100:5.2f}%")
    print(f"Average Processing Latency / Receipt:  {avg_latency_ms:5.3f} milliseconds (< 100ms target)")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
