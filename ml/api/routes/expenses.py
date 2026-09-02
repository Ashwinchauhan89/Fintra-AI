"""
Expense Classification (Phase 3) & OCR Receipt Scanner (Phase 15) Routes.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import (
    ExpenseClassifyRequest,
    ExpenseClassifyResponse,
    OCRScanRequest,
    OCRScanResponse,
)
from inference.predict import predict_category
from inference.predict_ocr import SmartReceiptScannerEngine

router = APIRouter(prefix="/api/v1", tags=["Expenses & OCR Intelligence"])
ocr_engine = SmartReceiptScannerEngine()


@router.post("/expenses/classify", response_model=ExpenseClassifyResponse)
def classify_expense_category(req: ExpenseClassifyRequest):
    """
    Classifies a transaction into 1 of 7 categories (food, shopping, bills, transport, healthcare, entertainment, education).
    """
    try:
        res = predict_category(
            merchant=req.merchant,
            description=req.description,
            amount=req.amount,
            date=req.date,
        )
        return ExpenseClassifyResponse(
            category=res.get("category", "shopping"),
            confidence=res.get("confidence", 0.85),
            low_confidence=res.get("low_confidence", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/scan", response_model=OCRScanResponse)
def scan_receipt(req: OCRScanRequest):
    """
    Extracts financial entities (merchant, total amount, ISO date, GST breakdown, payment mode) from OCR receipt text.
    """
    try:
        res = ocr_engine.scan_receipt_text(req.raw_text)
        if res.get("status") != "success":
            raise HTTPException(status_code=400, detail=res.get("message", "Failed to parse receipt."))
        return OCRScanResponse(**res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
