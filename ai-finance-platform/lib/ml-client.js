/**
 * Fintra-AI ML Microservice HTTP Client
 * Connects Next.js server and client components to the Python FastAPI backend.
 */

const ML_BASE_URL =
  process.env.ML_SERVICE_URL ||
  process.env.NEXT_PUBLIC_ML_SERVICE_URL ||
  "http://127.0.0.1:8000";

/**
 * Predicts the expense category for a given merchant, description, and amount.
 * Gracefully returns null if the ML service is unreachable.
 */
export async function predictExpenseCategory({ merchant, description = "", amount = 0 }) {
  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/predict/category`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        merchant: merchant || "General",
        description: description || "",
        amount: Number(amount) || 0,
      }),
      // Short timeout to keep UI responsive
      signal: AbortSignal.timeout(3000),
    });

    if (!res.ok) return null;
    const data = await res.json();
    return {
      category: data.category,
      confidence: data.confidence,
      isLowConfidence: data.is_low_confidence,
    };
  } catch (error) {
    // Graceful degradation when ML microservice is offline
    console.warn("ML Category Prediction service unavailable:", error.message);
    return null;
  }
}

/**
 * Checks if a proposed transaction is a statistical spending anomaly.
 */
export async function checkSpendingAnomaly({ merchant, amount, category = "general" }) {
  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/predict/anomaly`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        merchant: merchant || "",
        amount: Number(amount) || 0,
        category: category || "general",
        hour_of_day: new Date().getHours(),
      }),
      signal: AbortSignal.timeout(3000),
    });

    if (!res.ok) return null;
    const data = await res.json();
    return {
      isAnomaly: data.is_anomaly,
      severity: data.severity,
      reasons: data.reasons || [],
    };
  } catch (error) {
    console.warn("ML Anomaly Detection service unavailable:", error.message);
    return null;
  }
}

/**
 * Extracts structured transaction details from OCR receipt text.
 */
export async function scanReceiptText(rawText) {
  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/predict/ocr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: rawText }),
      signal: AbortSignal.timeout(5000),
    });

    if (!res.ok) return null;
    return await res.json();
  } catch (error) {
    console.warn("ML OCR Scanner service unavailable:", error.message);
    return null;
  }
}

/**
 * Sends a conversational query to the AI Copilot.
 */
export async function askCopilot({
  userQuery,
  monthlyIncome = 50000,
  monthlyExpenses = 30000,
  currentBalance = 50000,
  personaId = "BALANCED_GROWTH",
}) {
  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/copilot/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_query: userQuery,
        monthly_income: Number(monthlyIncome) || 50000,
        monthly_expenses: Number(monthlyExpenses) || 30000,
        current_balance: Number(currentBalance) || 50000,
        persona_id: personaId,
      }),
      signal: AbortSignal.timeout(8000),
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (error) {
    console.warn("ML Copilot service unavailable, using smart local fallback:", error.message);
  }

  // Graceful deterministic fallback
  const surplus = Math.max(0, monthlyIncome - monthlyExpenses);
  const runwayMonths = monthlyExpenses > 0 ? (currentBalance / monthlyExpenses).toFixed(1) : 3;

  return {
    status: "success",
    query: userQuery,
    ai_advisory: `Based on your monthly surplus of $${surplus.toLocaleString()} and emergency runway of ${runwayMonths} months, your financial baseline is solid. Focus on maintaining a 3–6 month emergency buffer while investing at least 50% of your remaining surplus into low-cost diversified funds.`,
    deterministic_ml_context: {
      monthly_surplus: surplus,
      runway_months: Number(runwayMonths),
      financial_health_score: runwayMonths >= 3 ? 85 : 65,
    },
    action_checklist: [
      `Keep $${(monthlyExpenses * 3).toLocaleString()} reserved in a high-yield liquid savings buffer.`,
      `Direct $${Math.round(surplus * 0.4).toLocaleString()}/mo into automated index fund investments.`,
      "Review any recurring subscriptions exceeding $50/mo.",
    ],
  };
}

/**
 * Checks if the user can safely afford a big-ticket purchase.
 */
export async function checkAffordability({
  itemName,
  itemPrice,
  monthlyIncome = 50000,
  monthlyExpenses = 30000,
  currentLiquidSavings = 50000,
  existingMonthlyEmi = 0,
}) {
  const price = Number(itemPrice) || 0;
  const income = Number(monthlyIncome) || 50000;
  const expenses = Number(monthlyExpenses) || 30000;
  const liquid = Number(currentLiquidSavings) || 50000;

  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/copilot/affordability`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        item_name: itemName || "Purchase",
        item_price_inr: price,
        monthly_income: income,
        monthly_expenses: expenses,
        current_liquid_savings: liquid,
        existing_monthly_emi: Number(existingMonthlyEmi) || 0,
      }),
      signal: AbortSignal.timeout(8000),
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (error) {
    console.warn("ML Affordability service unavailable, using smart local fallback:", error.message);
  }

  // Graceful deterministic fallback solver
  const surplus = Math.max(0, income - expenses - existingMonthlyEmi);
  const safeRunwayReq = expenses * 3;
  const postPurchaseSavings = liquid - price;

  let verdict = "AFFORDABLE_CASH";
  let strategy = "Pay upfront in full to avoid interest charges.";
  let advice = `You can afford ${itemName} ($${price.toLocaleString()}). You will retain $${postPurchaseSavings.toLocaleString()} in liquid reserves.`;

  if (postPurchaseSavings < safeRunwayReq) {
    if (surplus >= (price / 6) * 1.2) {
      verdict = "AFFORDABLE_NO_COST_EMI";
      strategy = "Use a 3 to 6-month 0% interest EMI plan to preserve your emergency cash.";
      advice = `Full upfront payment would reduce your emergency buffer. However, with your monthly surplus of $${surplus.toLocaleString()}, a 6-month EMI of ~$${Math.round(price / 6).toLocaleString()}/mo is well within your safe budget.`;
    } else {
      verdict = "NOT_RECOMMENDED_CURRENTLY";
      const months = Math.ceil(price / Math.max(1, surplus));
      strategy = `Save for ${months} months in a dedicated sinking fund before purchasing.`;
      advice = `Purchasing this now will leave your emergency runway critically low. Consider building your cash buffer first.`;
    }
  }

  return {
    status: "success",
    item_name: itemName,
    item_price_inr: price,
    verdict,
    recommended_strategy: strategy,
    impact_on_emergency_fund: {
      current_liquid_savings_inr: liquid,
      post_purchase_liquid_savings_inr: Math.max(0, postPurchaseSavings),
      current_runway_months: Number((liquid / Math.max(1, expenses)).toFixed(1)),
      post_purchase_runway_months: Number((Math.max(0, postPurchaseSavings) / Math.max(1, expenses)).toFixed(1)),
    },
    ai_copilot_advice: advice,
  };
}

