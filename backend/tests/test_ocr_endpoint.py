"""
Unit test suite for Phase 15 OCR Receipt Scanner in Backend API.
"""

import unittest
from backend.app.schemas.predictions import OCRScanRequest, OCRScanResponse


class TestOCREndpointSchemas(unittest.TestCase):
    def test_ocr_request_validation(self):
        receipt_text = "STARBUCKS COFFEE\nDate: 25/08/2026\nTotal: INR 362.00\nUPI"
        req = OCRScanRequest(raw_text=receipt_text)
        self.assertIn("STARBUCKS", req.raw_text)

    def test_ocr_response_validation(self):
        resp = OCRScanResponse(
            status="success",
            extracted_expense={
                "merchant": "Starbucks",
                "total_amount_inr": 362.0,
                "currency": "INR",
                "transaction_date": "2026-08-25",
                "predicted_category": "food",
                "payment_mode": "UPI",
            },
            extraction_confidence=0.92,
            entity_confidences={"merchant_confidence": 0.95, "total_confidence": 0.90},
        )
        self.assertEqual(resp.status, "success")
        self.assertEqual(resp.extracted_expense["merchant"], "Starbucks")
        self.assertEqual(resp.extracted_expense["total_amount_inr"], 362.0)


if __name__ == "__main__":
    unittest.main()
