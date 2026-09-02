"""
Production Inference Engine for Phase 15: OCR Receipt Intelligence & Smart Scanner.

Provides:
- `scan_receipt_text(raw_text: str)`: Scans OCR text output to extract merchant, total amount,
  normalized ISO date, GST breakdown, payment method, and automatically classifies the expense category.
- `scan_receipt_file(file_path: str)`: Reads image / PDF receipts with EasyOCR / PyMuPDF fallback.
- Interactive CLI for instant terminal testing.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

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

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
METADATA_PATH = os.path.join(MODEL_DIR, "ocr_metadata.json")


class SmartReceiptScannerEngine:
    def __init__(self):
        self.metadata = {}
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)

    def scan_receipt_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Parses OCR receipt text into a clean, structured expense creation payload.
        """
        if not raw_text or not raw_text.strip():
            return {
                "status": "error",
                "message": "Empty receipt text provided.",
            }

        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        # 1. Extract Core Financial Entities
        merchant, merchant_conf = extract_merchant_name(lines)
        total_amount, total_conf = extract_total_amount(raw_text)
        txn_date, date_conf = extract_transaction_date(raw_text)
        tax_info = extract_tax_breakdown(raw_text)
        payment_mode = extract_payment_mode(raw_text)
        item_summary = extract_line_item_summary(lines)

        # 2. Automated Category Classification (Phase 3 Integration)
        cat_desc = f"{merchant} {item_summary}" if item_summary else merchant
        cat_res = predict_category(
            merchant=merchant,
            description=cat_desc,
            amount=total_amount,
            date=txn_date,
        )
        predicted_category = cat_res.get("category", "shopping")
        cat_conf = cat_res.get("confidence", 0.85)

        # Overall composite confidence
        composite_confidence = round(
            float(merchant_conf * 0.30 + total_conf * 0.40 + date_conf * 0.20 + (cat_conf or 0.8) * 0.10),
            2,
        )

        return {
            "status": "success",
            "extracted_expense": {
                "merchant": merchant,
                "total_amount_inr": total_amount,
                "currency": "INR",
                "transaction_date": txn_date,
                "predicted_category": predicted_category,
                "payment_mode": payment_mode,
                "tax_amount_inr": tax_info.get("tax_amount_inr", 0.0),
                "line_items_summary": item_summary if item_summary else "General Purchase",
            },
            "extraction_confidence": composite_confidence,
            "entity_confidences": {
                "merchant_confidence": merchant_conf,
                "total_amount_confidence": total_conf,
                "date_confidence": date_conf,
                "category_confidence": round(float(cat_conf or 0.8), 2),
            },
        }

    def scan_receipt_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scans a receipt image or text file.
        """
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found at: {file_path}"}

        # If text file, read directly
        if file_path.endswith(".txt") or file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.scan_receipt_text(content)

        # Image OCR Fallback: Try EasyOCR / PIL
        try:
            import easyocr
            reader = easyocr.Reader(["en"], gpu=False)
            results = reader.readtext(file_path, detail=0)
            raw_text = "\n".join(results)
            return self.scan_receipt_text(raw_text)
        except ImportError:
            # Basic fallback message
            return {
                "status": "partial_fallback",
                "message": "EasyOCR not installed in local environment. Pass OCR text directly to scan_receipt_text().",
            }


def main():
    parser = argparse.ArgumentParser(description="Phase 15 Smart Receipt Scanner CLI")
    parser.add_argument("--text", type=str, default=None, help="Raw OCR receipt text string")
    parser.add_argument("--file", type=str, default=None, help="Path to receipt text/image file")

    args = parser.parse_args()

    engine = SmartReceiptScannerEngine()

    if args.file:
        res = engine.scan_receipt_file(args.file)
    elif args.text:
        res = engine.scan_receipt_text(args.text)
    else:
        sample_receipt = """*** TAX INVOICE ***
STARBUCKS COFFEE
GSTIN: 27AABCT1234A1Z5
Date: 25/08/2026   Time: 14:35
Bill No: INV-48291
--------------------------------
1x Caffe Latte (Venti)     345.00
1x Blueberry Muffin        240.00
--------------------------------
Subtotal:               INR   585.00
GST (5%):               INR    29.25
GRAND TOTAL:            INR   614.25
--------------------------------
Paid via UPI - APPROVED
Thank you! Visit again."""
        print("[info] No input provided. Testing with sample Starbucks receipt:")
        res = engine.scan_receipt_text(sample_receipt)

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
