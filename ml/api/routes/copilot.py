"""
AI + ML Hybrid Copilot & Affordability Solver (Phase 19).

Synthesizes deterministic ML model outputs (cash flow, credit scores, health score, budgeting)
into actionable natural language financial guidance via Google Gemini API / Financial Heuristic Synthesizer.
"""

import os
from fastapi import APIRouter, HTTPException
from api.schemas import (
    AffordabilityCheckRequest,
    AffordabilityCheckResponse,
    CopilotAskRequest,
    CopilotAskResponse,
)
from inference.predict_budget import calculate_financial_health_score, recommend_budget
from inference.predict_forecasting import predict_cash_flow

router = APIRouter(prefix="/api/v1/copilot", tags=["AI + ML Hybrid Copilot"])


@router.post("/ask", response_model=CopilotAskResponse)
def ask_financial_copilot(req: CopilotAskRequest):
    """
    Conversational AI financial advisory connecting deterministic ML models with conversational intelligence.
    """
    try:
        # 1. Compute Deterministic ML Diagnostics Context
        health_diag = calculate_financial_health_score(
            monthly_income=req.monthly_income or 75000.0,
            current_balance=req.current_balance or 80000.0,
            monthly_expenses={"general": req.monthly_expenses or 42000.0},
        )
        monthly_surplus = max(0.0, (req.monthly_income or 75000.0) - (req.monthly_expenses or 42000.0))

        ml_context = {
            "monthly_surplus_inr": monthly_surplus,
            "financial_health_score": health_diag.get("financial_health_score", 85.0),
            "health_grade": health_diag.get("grade", "A"),
            "runway_months": health_diag.get("runway_months", 3.5),
            "persona_id": req.persona_id,
        }

        # 2. Check if GEMINI_API_KEY is configured for dynamic LLM generation
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""You are Fintra-AI Copilot, an expert certified financial advisor for Indian users.
User Query: "{req.user_query}"
User ML Profile:
- Monthly Income: INR {req.monthly_income:,.0f}
- Monthly Expenses: INR {req.monthly_expenses:,.0f}
- Monthly Surplus: INR {monthly_surplus:,.0f}
- Current Bank Balance: INR {req.current_balance:,.0f}
- Financial Health Score: {health_diag.get('financial_health_score')}/100 ({health_diag.get('grade')})
- Emergency Runway: {health_diag.get('runway_months')} months
- Persona: {req.persona_id}

Provide concise, clear, and actionable advice tailored to these exact numbers. Keep under 3 paragraphs."""
                response = model.generate_content(prompt)
                ai_text = response.text
            except Exception:
                ai_text = generate_rule_based_advisory(req.user_query, ml_context)
        else:
            ai_text = generate_rule_based_advisory(req.user_query, ml_context)

        # 3. Actionable Checklist
        checklist = [
            f"Allocate INR {monthly_surplus * 0.5:,.0f}/mo into a dedicated high-yield liquid recurring fund.",
            f"Maintain your {health_diag.get('runway_months')} months emergency cushion before locking long-term funds.",
            "Enable automated SIP debits on salary day to enforce disciplined wealth growth.",
        ]

        return CopilotAskResponse(
            status="success",
            query=req.user_query,
            ai_advisory=ai_text,
            deterministic_ml_context=ml_context,
            action_checklist=checklist,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/affordability", response_model=AffordabilityCheckResponse)
def check_item_affordability(req: AffordabilityCheckRequest):
    """
    Evaluates whether a user can safely afford a big-ticket purchase without depleting emergency runway.
    """
    try:
        monthly_surplus = max(0.0, req.monthly_income - req.monthly_expenses - req.existing_monthly_emi)
        emergency_cushion_required = req.monthly_expenses * 3.0  # 3 months minimum safe runway
        post_purchase_savings = req.current_liquid_savings - req.item_price_inr

        # Decision Matrix
        if post_purchase_savings >= emergency_cushion_required:
            verdict = "AFFORDABLE_CASH"
            strategy = "Pay in full upfront using debit / UPI to avoid unnecessary EMI interest charges."
            advice = (
                f"You can easily afford the {req.item_name} (INR {req.item_price_inr:,.0f}). "
                f"After the purchase, you will still retain INR {post_purchase_savings:,.0f} in liquid savings, "
                f"which safely protects your {post_purchase_savings / max(1, req.monthly_expenses):.1f}-month emergency cushion."
            )
        elif monthly_surplus >= (req.item_price_inr / 6.0) * 1.3:
            verdict = "AFFORDABLE_NO_COST_EMI"
            strategy = "Opt for a 3 to 6-month No-Cost EMI on credit card while keeping emergency funds intact."
            monthly_emi = round(req.item_price_inr / 6.0, 2)
            advice = (
                f"Direct full cash payment would reduce your emergency buffer below safe limits. "
                f"However, with your monthly surplus of INR {monthly_surplus:,.0f}, a 6-month No-Cost EMI "
                f"(~INR {monthly_emi:,.0f}/mo) is very comfortable and will not strain your monthly budget."
            )
        else:
            verdict = "NOT_RECOMMENDED_CURRENTLY"
            months_to_save = round(req.item_price_inr / max(1.0, monthly_surplus), 1)
            strategy = f"Postpone purchase by {months_to_save} months to build adequate savings cushion."
            advice = (
                f"Purchasing {req.item_name} right now will severely compromise your financial safety net. "
                f"We strongly recommend setting up a dedicated goal SIP of INR {monthly_surplus * 0.7:,.0f}/mo for {months_to_save} months."
            )

        return AffordabilityCheckResponse(
            status="success",
            item_name=req.item_name,
            item_price_inr=req.item_price_inr,
            verdict=verdict,
            recommended_strategy=strategy,
            impact_on_emergency_fund={
                "current_liquid_savings_inr": req.current_liquid_savings,
                "post_purchase_liquid_savings_inr": max(0.0, post_purchase_savings),
                "safe_runway_threshold_inr": emergency_cushion_required,
                "current_runway_months": round(req.current_liquid_savings / max(1.0, req.monthly_expenses), 1),
                "post_purchase_runway_months": round(max(0.0, post_purchase_savings) / max(1.0, req.monthly_expenses), 1),
            },
            ai_copilot_advice=advice,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_rule_based_advisory(query: str, context: dict) -> str:
    """
    High-quality structured financial heuristic advisor fallback.
    """
    surplus = context.get("monthly_surplus_inr", 30000.0)
    score = context.get("financial_health_score", 85.0)
    grade = context.get("health_grade", "A")
    runway = context.get("runway_months", 3.0)

    return (
        f"Based on your current financial diagnostics (Health Score: {score}/100 - Grade {grade}), "
        f"you have a monthly disposable surplus of INR {surplus:,.0f} and an emergency runway of {runway} months.\n\n"
        f"Regarding your query: '{query}', the optimal strategy is to commit 50% of your surplus (INR {surplus * 0.5:,.0f}/mo) "
        f"into high-liquidity recurring instruments, while preserving your essential cash runway for unforeseen market swings."
    )
