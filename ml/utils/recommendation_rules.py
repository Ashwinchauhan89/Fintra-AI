"""
Financial Product Catalog, Reward Calculus & Matchmaking Utilities for Phase 16.

Defines:
- Curated Multi-Category Product Catalog (Credit Cards, Savings/FDs, Insurance, Investments, Refinancing)
- Dynamic Net Annual Value (NAV in INR) Calculator across spending categories
- Vectorized Cosine Relevance & Fast Matrix Dot-Product Matchmaker
- Anti-Predatory Eligibility Guardrails & Persona Affinity Weights
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Curated Financial Product Marketplace Catalog (Indian & Global Market)
# ---------------------------------------------------------------------------

PRODUCT_CATALOG = [
    # --- A. CREDIT CARDS ---
    {
        "product_id": "CC_CASHBACK_MILLENNIA",
        "name": "HDFC Millennia Cashback Credit Card",
        "category": "CREDIT_CARDS",
        "sub_category": "CASHBACK_SHOPPING",
        "provider": "HDFC Bank",
        "annual_fee_inr": 1000.0,
        "min_credit_score": 720,
        "min_monthly_income": 35000.0,
        "target_personas": ["YOUNG_TECH_PROFESSIONAL", "BUDGET_CONSCIOUS_STUDENT", "BALANCED_FAMILY_HOMEMAKER"],
        "reward_multipliers": {
            "dining": 0.05,       # 5% cashback on Swiggy/Zomato
            "shopping": 0.05,     # 5% cashback on Amazon/Flipkart
            "groceries": 0.01,    # 1% cashback
            "travel": 0.01,
            "fuel": 0.01,
            "utilities": 0.01,
        },
        "welcome_bonus_inr": 1000.0,
        "key_perks": ["5% cashback on top online merchants", "1% cashback on all offline spends", "Lounge access (4/yr)"],
        "rating": 4.8,
    },
    {
        "product_id": "CC_AIRTEL_AXIS",
        "name": "Airtel Axis Bank Utility & Food Card",
        "category": "CREDIT_CARDS",
        "sub_category": "UTILITIES_CASHBACK",
        "provider": "Axis Bank",
        "annual_fee_inr": 500.0,
        "min_credit_score": 700,
        "min_monthly_income": 25000.0,
        "target_personas": ["BALANCED_FAMILY_HOMEMAKER", "BUDGET_CONSCIOUS_STUDENT", "YOUNG_TECH_PROFESSIONAL"],
        "reward_multipliers": {
            "dining": 0.10,       # 10% on Swiggy/Zomato
            "shopping": 0.01,
            "groceries": 0.10,    # 10% on BigBasket
            "travel": 0.01,
            "fuel": 0.01,
            "utilities": 0.25,    # 25% on Airtel & Utility bills
        },
        "welcome_bonus_inr": 500.0,
        "key_perks": ["25% cashback on Airtel mobile/DTH/broadband", "10% on BigBasket, Swiggy, Zomato", "10% on electricity/gas bills"],
        "rating": 4.9,
    },
    {
        "product_id": "CC_TRAVEL_AXIS_ATLAS",
        "name": "Axis Bank Atlas Travel & Miles Card",
        "category": "CREDIT_CARDS",
        "sub_category": "TRAVEL_AIR_MILES",
        "provider": "Axis Bank",
        "annual_fee_inr": 5000.0,
        "min_credit_score": 750,
        "min_monthly_income": 100000.0,
        "target_personas": ["YOUNG_TECH_PROFESSIONAL", "HIGH_NET_WORTH_INVESTOR", "SMB_BUSINESS_OWNER"],
        "reward_multipliers": {
            "dining": 0.04,
            "shopping": 0.02,
            "groceries": 0.02,
            "travel": 0.10,       # 5x Edge Miles (10% effective value on airlines/hotels)
            "fuel": 0.01,
            "utilities": 0.01,
        },
        "welcome_bonus_inr": 5000.0,
        "key_perks": ["5,000 Edge Miles welcome bonus", "Tiered milestone bonuses up to 10,000 miles", "Unlimited domestic lounge access"],
        "rating": 4.9,
    },
    {
        "product_id": "CC_AMEX_PLATINUM_TRAVEL",
        "name": "American Express Platinum Travel Card",
        "category": "CREDIT_CARDS",
        "sub_category": "TRAVEL_LIFESTYLE",
        "provider": "American Express",
        "annual_fee_inr": 5000.0,
        "min_credit_score": 740,
        "min_monthly_income": 80000.0,
        "target_personas": ["YOUNG_TECH_PROFESSIONAL", "HIGH_NET_WORTH_INVESTOR"],
        "reward_multipliers": {
            "dining": 0.03,
            "shopping": 0.08,     # Milestone vouchers (₹4L spend = ₹32k vouchers)
            "groceries": 0.04,
            "travel": 0.08,
            "fuel": 0.01,
            "utilities": 0.02,
        },
        "welcome_bonus_inr": 4000.0,
        "key_perks": ["Taj hotel voucher worth ₹10,000 on ₹4 Lakh annual spend", "40,000 Membership Rewards points on milestones"],
        "rating": 4.7,
    },
    {
        "product_id": "CC_BPCL_SBI_OCTANE",
        "name": "BPCL SBI Card Octane Fuel Card",
        "category": "CREDIT_CARDS",
        "sub_category": "FUEL_TRANSPORT",
        "provider": "SBI Card",
        "annual_fee_inr": 1499.0,
        "min_credit_score": 680,
        "min_monthly_income": 30000.0,
        "target_personas": ["BALANCED_FAMILY_HOMEMAKER", "SMB_BUSINESS_OWNER", "YOUNG_TECH_PROFESSIONAL"],
        "reward_multipliers": {
            "dining": 0.025,
            "shopping": 0.01,
            "groceries": 0.025,
            "travel": 0.01,
            "fuel": 0.0725,       # 7.25% value back on BPCL fuel (25x reward points)
            "utilities": 0.01,
        },
        "welcome_bonus_inr": 1500.0,
        "key_perks": ["7.25% value back on fuel purchases at BPCL pumps", "1% fuel surcharge waiver", "4 complimentary domestic lounge visits/yr"],
        "rating": 4.6,
    },
    {
        "product_id": "CC_IDFC_FIRST_WOW",
        "name": "IDFC FIRST WOW Secured Credit Builder Card",
        "category": "CREDIT_CARDS",
        "sub_category": "CREDIT_BUILDER",
        "provider": "IDFC FIRST Bank",
        "annual_fee_inr": 0.0,  # Lifetime Free
        "min_credit_score": 300,  # No credit score required (FD backed)
        "min_monthly_income": 10000.0,
        "target_personas": ["BUDGET_CONSCIOUS_STUDENT", "DEBT_REHABILITATION_SEEKER"],
        "reward_multipliers": {
            "dining": 0.01,
            "shopping": 0.01,
            "groceries": 0.01,
            "travel": 0.01,
            "fuel": 0.01,
            "utilities": 0.01,
        },
        "welcome_bonus_inr": 0.0,
        "key_perks": ["Zero annual fee forever (Lifetime Free)", "Guaranteed approval backed by fixed deposit (FD earns 7.5%)", "Builds CIBIL credit score rapidly"],
        "rating": 4.8,
    },
    {
        "product_id": "CC_HDFC_INFINIA_METAL",
        "name": "HDFC Bank Infinia Metal Edition",
        "category": "CREDIT_CARDS",
        "sub_category": "SUPER_PREMIUM_METAL",
        "provider": "HDFC Bank",
        "annual_fee_inr": 12500.0,
        "min_credit_score": 780,
        "min_monthly_income": 250000.0,
        "target_personas": ["HIGH_NET_WORTH_INVESTOR"],
        "reward_multipliers": {
            "dining": 0.099,      # 3x SmartBuy dining (9.9%)
            "shopping": 0.099,    # 3x SmartBuy e-commerce
            "groceries": 0.033,
            "travel": 0.165,      # 5x SmartBuy flights/hotels (16.5% reward rate)
            "fuel": 0.01,
            "utilities": 0.033,
        },
        "welcome_bonus_inr": 12500.0,
        "key_perks": ["1:1 reward redemption for flights & Apple products", "Unlimited global lounge access + 4 guest visits", "24/7 dedicated metal concierge"],
        "rating": 5.0,
    },

    # --- B. HIGH-YIELD SAVINGS & FIXED DEPOSITS ---
    {
        "product_id": "SAV_INDUSIND_INDIE",
        "name": "IndusInd INDIE High-Yield Savings Account",
        "category": "SAVINGS_AND_DEPOSITS",
        "sub_category": "HIGH_YIELD_SAVINGS",
        "provider": "IndusInd Bank",
        "annual_fee_inr": 0.0,
        "min_credit_score": 300,
        "min_monthly_income": 15000.0,
        "target_personas": ["BUDGET_CONSCIOUS_STUDENT", "YOUNG_TECH_PROFESSIONAL", "BALANCED_FAMILY_HOMEMAKER", "SMB_BUSINESS_OWNER"],
        "reward_multipliers": {},
        "base_apy": 0.0675,       # 6.75% annualized on daily balance
        "welcome_bonus_inr": 250.0,
        "key_perks": ["6.75% interest on savings balance", "Zero balance digital account", "Auto-sweep FD linkage at 7.75%"],
        "rating": 4.7,
    },
    {
        "product_id": "FD_SHRIRAM_FINANCE",
        "name": "Shriram Finance Corporate Fixed Deposit",
        "category": "SAVINGS_AND_DEPOSITS",
        "sub_category": "FIXED_DEPOSIT_LADDER",
        "provider": "Shriram Finance",
        "annual_fee_inr": 0.0,
        "min_credit_score": 300,
        "min_monthly_income": 20000.0,
        "target_personas": ["BALANCED_FAMILY_HOMEMAKER", "HIGH_NET_WORTH_INVESTOR", "SMB_BUSINESS_OWNER"],
        "reward_multipliers": {},
        "base_apy": 0.0860,       # 8.60% p.a. (AAA Rated)
        "welcome_bonus_inr": 0.0,
        "key_perks": ["Highest safety rating (ICRA AAA / CRISIL AAA)", "8.60% fixed annualized return", "+0.50% extra for senior citizens"],
        "rating": 4.8,
    },

    # --- C. INSURANCE PRODUCTS ---
    {
        "product_id": "INS_HDFC_CLICK2PROTECT",
        "name": "HDFC Life Click 2 Protect 3D Plus Term Insurance",
        "category": "INSURANCE_PRODUCTS",
        "sub_category": "PURE_TERM_LIFE",
        "provider": "HDFC Life",
        "annual_fee_inr": 9500.0,  # Annual premium for ₹1 Cr cover
        "min_credit_score": 650,
        "min_monthly_income": 30000.0,
        "target_personas": ["BALANCED_FAMILY_HOMEMAKER", "YOUNG_TECH_PROFESSIONAL", "SMB_BUSINESS_OWNER"],
        "reward_multipliers": {},
        "insurance_cover_multiple": 15.0,  # 15x annual income life cover
        "welcome_bonus_inr": 0.0,
        "key_perks": ["99.5% claim settlement ratio", "₹1 Crore - ₹2 Crore pure term cover", "Tax deduction under Section 80C"],
        "rating": 4.9,
    },
    {
        "product_id": "INS_CARE_HEALTH_SUPREME",
        "name": "Care Health Supreme Comprehensive Health Cover",
        "category": "INSURANCE_PRODUCTS",
        "sub_category": "HEALTH_INSURANCE",
        "provider": "Care Health Insurance",
        "annual_fee_inr": 12000.0,  # Annual premium for ₹15 Lakh family floater
        "min_credit_score": 300,
        "min_monthly_income": 25000.0,
        "target_personas": ["BALANCED_FAMILY_HOMEMAKER", "YOUNG_TECH_PROFESSIONAL", "SMB_BUSINESS_OWNER", "HIGH_NET_WORTH_INVESTOR"],
        "reward_multipliers": {},
        "insurance_cover_multiple": 0.0,
        "welcome_bonus_inr": 0.0,
        "key_perks": ["Unlimited automatic recharge of sum insured", "No room rent capping", "Cashless hospitalization at 21,000+ hospitals"],
        "rating": 4.8,
    },

    # --- D. DEBT REFINANCING & BALANCE TRANSFER ---
    {
        "product_id": "REFINANCE_SBI_DEBT_CONSOLIDATION",
        "name": "SBI Personal Loan Debt Consolidation Scheme",
        "category": "LOAN_REFINANCING",
        "sub_category": "BALANCE_TRANSFER",
        "provider": "State Bank of India",
        "annual_fee_inr": 0.0,
        "min_credit_score": 650,
        "min_monthly_income": 25000.0,
        "target_personas": ["DEBT_REHABILITATION_SEEKER", "BALANCED_FAMILY_HOMEMAKER"],
        "reward_multipliers": {},
        "base_apy": 0.115,  # 11.5% APR (Replaces 36-42% credit card debt)
        "welcome_bonus_inr": 0.0,
        "key_perks": ["Replaces 36-42% credit card revolving debt with 11.5% fixed loan", "Saves up to ₹35,000 in interest per ₹1 Lakh balance", "Single easy monthly EMI"],
        "rating": 4.8,
    },
]

# ---------------------------------------------------------------------------
# 2. Net Annual Value (NAV) Calculation Engine
# ---------------------------------------------------------------------------

def calculate_product_net_annual_value(
    product: Dict[str, Any],
    user_spends: Dict[str, float],
    liquid_savings: float = 0.0,
    existing_card_debt: float = 0.0,
) -> Tuple[float, str]:
    """
    Computes exact estimated annual monetary savings / cashback / return (in INR).
    Returns (net_annual_value_inr, value_justification).
    """
    cat = product["category"]
    fee = product.get("annual_fee_inr", 0.0)
    welcome_bonus = product.get("welcome_bonus_inr", 0.0)

    if cat == "CREDIT_CARDS":
        multipliers = product.get("reward_multipliers", {})
        annual_rewards = 0.0
        top_saving_cat = "General Spend"
        max_cat_saving = 0.0

        for category, mult in multipliers.items():
            monthly_cat_spend = user_spends.get(category, 0.0)
            annual_cat_spend = monthly_cat_spend * 12.0
            cat_cashback = annual_cat_spend * mult
            annual_rewards += cat_cashback
            if cat_cashback > max_cat_saving:
                max_cat_saving = cat_cashback
                top_saving_cat = category

        net_value = annual_rewards + welcome_bonus - fee
        justification = (
            f"Earns ~INR {annual_rewards:,.0f}/yr in cashbacks (led by {top_saving_cat}) + INR {welcome_bonus:,.0f} bonus - INR {fee:,.0f} fee."
        )
        return round(net_value, 2), justification

    elif cat == "SAVINGS_AND_DEPOSITS":
        apy = product.get("base_apy", 0.04)
        # Incremental interest over base standard 3.0% savings account
        incremental_yield = apy - 0.030
        annual_interest = liquid_savings * incremental_yield
        net_value = annual_interest + welcome_bonus
        justification = f"Earns INR {annual_interest:,.0f}/yr incremental interest over standard 3% savings accounts at {apy*100:.2f}% APY."
        return round(net_value, 2), justification

    elif cat == "LOAN_REFINANCING":
        refinance_apr = product.get("base_apy", 0.12)
        # Saves the difference between 38% card APR and 12% loan APR
        interest_saved = existing_card_debt * (0.38 - refinance_apr)
        justification = f"Saves INR {interest_saved:,.0f}/yr in high-interest charges by replacing 38% card APR with {refinance_apr*100:.1f}% fixed loan."
        return round(interest_saved, 2), justification

    elif cat == "INSURANCE_PRODUCTS":
        # Insurance value is financial security; ROI represented as protected capital multiple
        cover = user_spends.get("monthly_income", 50000.0) * 12.0 * product.get("insurance_cover_multiple", 15.0)
        justification = f"Secures INR {cover/100000:,.1f} Lakhs pure life protection for your dependents at INR {fee:,.0f}/yr premium."
        return round(fee * 1.5, 2), justification

    return 0.0, "Tailored financial marketplace match."


# ---------------------------------------------------------------------------
# 3. Vectorized Matchmaker & Ranking Pipeline
# ---------------------------------------------------------------------------

SPEND_CATEGORIES_ORDER = ["dining", "shopping", "groceries", "travel", "fuel", "utilities"]


def get_user_spend_vector(user_spends: Dict[str, float]) -> np.ndarray:
    """
    Extracts normalized category spend vector for cosine matching.
    """
    spends = np.array([user_spends.get(c, 0.0) for c in SPEND_CATEGORIES_ORDER], dtype=np.float64)
    total = np.sum(spends)
    if total > 0:
        return spends / total
    return np.ones(len(SPEND_CATEGORIES_ORDER)) / len(SPEND_CATEGORIES_ORDER)


def get_product_reward_vector(product: Dict[str, Any]) -> np.ndarray:
    """
    Extracts normalized category reward multiplier vector.
    """
    mults = product.get("reward_multipliers", {})
    rewards = np.array([mults.get(c, 0.0) for c in SPEND_CATEGORIES_ORDER], dtype=np.float64)
    norm = np.linalg.norm(rewards)
    if norm > 0:
        return rewards / norm
    return np.zeros(len(SPEND_CATEGORIES_ORDER))
