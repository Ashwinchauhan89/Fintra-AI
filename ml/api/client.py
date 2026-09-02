"""
Python Client SDK for Fintra-AI ML Production Microservice.
"""

from typing import Any, Dict, List, Optional
import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


class FintraMLClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/health")
            res.raise_for_status()
            return res.json()

    def classify_expense(self, merchant: str, description: str, amount: float, date: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/expenses/classify",
                json={"merchant": merchant, "description": description, "amount": amount, "date": date},
            )
            res.raise_for_status()
            return res.json()

    def scan_receipt(self, raw_text: str) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/ocr/scan",
                json={"raw_text": raw_text},
            )
            res.raise_for_status()
            return res.json()

    def recommend_budget(self, monthly_income: float, lifestyle: str = "balanced", savings_target_pct: float = 0.20) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/budget/recommend",
                json={"monthly_income": monthly_income, "lifestyle": lifestyle, "savings_target_pct": savings_target_pct},
            )
            res.raise_for_status()
            return res.json()

    def diagnose_health_score(self, monthly_income: float, current_balance: float, monthly_expenses: Dict[str, float], debt_obligations: float = 0.0) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/health-score/diagnose",
                json={"monthly_income": monthly_income, "current_balance": current_balance, "monthly_expenses": monthly_expenses, "debt_obligations": debt_obligations},
            )
            res.raise_for_status()
            return res.json()

    def check_fraud(self, amount: float, category: str = "shopping", hour_of_day: int = 14) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/fraud/check",
                json={"amount": amount, "category": category, "hour_of_day": hour_of_day},
            )
            res.raise_for_status()
            return res.json()

    def underwrite_loan(self, monthly_income: float, requested_loan_amount: float, loan_tenure_months: int, credit_score: int = 750) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/loans/underwrite",
                json={"monthly_income": monthly_income, "requested_loan_amount": requested_loan_amount, "loan_tenure_months": loan_tenure_months, "credit_score": credit_score},
            )
            res.raise_for_status()
            return res.json()

    def estimate_credit_score(self, monthly_income: float, total_credit_limit: float, total_credit_used: float) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/credit/estimate",
                json={"monthly_income": monthly_income, "total_credit_limit": total_credit_limit, "total_credit_used": total_credit_used},
            )
            res.raise_for_status()
            return res.json()

    def recommend_investments(self, monthly_income: float, age: int, risk_profile: str = "BALANCED") -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/investments/recommend",
                json={"monthly_income": monthly_income, "age": age, "risk_profile": risk_profile},
            )
            res.raise_for_status()
            return res.json()

    def segment_persona(self, monthly_income: float, essential_expenses: float, discretionary_spend: float, monthly_sip: float) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/persona/segment",
                json={"monthly_income": monthly_income, "monthly_essential_expenses": essential_expenses, "monthly_discretionary_spend": discretionary_spend, "monthly_investments_sip": monthly_sip},
            )
            res.raise_for_status()
            return res.json()

    def ask_copilot(self, user_query: str, monthly_income: float = 75000.0, monthly_expenses: float = 40000.0) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/copilot/ask",
                json={"user_query": user_query, "monthly_income": monthly_income, "monthly_expenses": monthly_expenses},
            )
            res.raise_for_status()
            return res.json()

    def check_affordability(self, item_name: str, item_price_inr: float, monthly_income: float, monthly_expenses: float, current_liquid_savings: float) -> Dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(
                f"{self.base_url}/api/v1/copilot/affordability",
                json={"item_name": item_name, "item_price_inr": item_price_inr, "monthly_income": monthly_income, "monthly_expenses": monthly_expenses, "current_liquid_savings": current_liquid_savings},
            )
            res.raise_for_status()
            return res.json()
