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

/**
 * Simulates multi-month financial trajectory using the Reinforcement Learning Engine (Issue #54).
 * Calls the FastAPI RL endpoint or falls back gracefully to a high-fidelity deterministic simulator.
 */
export async function simulateRLDecision({
  income,
  expenses,
  savings,
  debt = 0,
  investment = 0,
  emergencyFund = null,
  riskTolerance = 0.6,
  financialGoal = 500000,
  goalProgress = null,
  simulationPeriodMonths = 24,
}) {
  const inc = Number(income) || 60000;
  const exp = Number(expenses) || 35000;
  const sav = Number(savings) || 150000;
  const dbt = Number(debt) || 0;
  const inv = Number(investment) || 0;
  const emg = emergencyFund !== null ? Number(emergencyFund) : Math.min(sav * 0.4, exp * 3);
  const rsk = Number(riskTolerance) || 0.6;
  const gol = Number(financialGoal) || 500000;
  const months = Number(simulationPeriodMonths) || 24;

  try {
    const res = await fetch(`${ML_BASE_URL}/api/v1/rl/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        income: inc,
        expenses: exp,
        savings: sav,
        debt: dbt,
        investment: inv,
        emergency_fund: emg,
        risk_tolerance: rsk,
        financial_goal: gol,
        goal_progress: goalProgress !== null ? Number(goalProgress) : undefined,
        simulation_period_months: months,
      }),
      signal: AbortSignal.timeout(6000),
    });

    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (error) {
    console.warn("FastAPI RL Simulation service offline, using deterministic policy engine:", error.message);
  }

  // Graceful deterministic policy simulation fallback
  let curDebt = dbt;
  let curSav = sav;
  let curInv = inv;
  let curEmg = emg;
  let debtFreeMonth = null;
  const trajectory = [];
  const actionCounts = {
    "Pay Down Debt": 0,
    "Increase Emergency Fund": 0,
    "Adjust Investment Allocation": 0,
    "Increase Savings": 0,
    "Reduce Discretionary Spending": 0,
  };

  const initialNetWorth = curSav + curInv + curEmg - curDebt;
  const initHealth = Math.min(100, Math.round(
    ((curEmg / Math.max(1, exp)) / 6 * 30) +
    (curDebt === 0 ? 25 : Math.max(0, 25 - (curDebt / (inc * 12)) * 30)) +
    (Math.min(25, (curSav + curInv) / (inc * 6) * 25)) +
    (Math.min(20, Math.max(0, inc - exp) / inc * 66))
  ));

  trajectory.push({
    month: 0,
    income: Math.round(inc),
    expenses: Math.round(exp),
    savings: Math.round(curSav),
    debt: Math.round(curDebt),
    investment: Math.round(curInv),
    emergency_fund: Math.round(curEmg),
    net_worth: Math.round(initialNetWorth),
    goal_progress: Number(Math.min(1, Math.max(0, initialNetWorth / gol)).toFixed(2)),
    action_name: "Starting Baseline",
    health_score: initHealth,
  });

  for (let m = 1; m <= months; m++) {
    let curExp = exp;
    let actionName = "Increase Savings";

    // Policy logic: Eradicate high debt first, then establish 3-6 mo buffer, then invest
    if (curDebt > 0) {
      actionName = "Pay Down Debt";
      actionCounts["Pay Down Debt"]++;
      const surplus = Math.max(0, inc - curExp);
      const pay = Math.min(curDebt, surplus * 0.75);
      curDebt = Math.max(0, curDebt * (1 + 0.12 / 12) - pay);
      const rem = surplus - pay;
      curSav += rem * 0.5 + (curSav * (0.045 / 12));
      curEmg += rem * 0.5;
      if (curDebt === 0 && !debtFreeMonth) debtFreeMonth = m;
    } else if (curEmg < curExp * 3) {
      actionName = "Increase Emergency Fund";
      actionCounts["Increase Emergency Fund"]++;
      const surplus = Math.max(0, inc - curExp);
      curEmg += surplus * 0.8;
      curSav += (surplus * 0.2) + (curSav * (0.045 / 12));
      curInv += curInv * ((0.07 + rsk * 0.05) / 12);
    } else {
      actionName = "Adjust Investment Allocation";
      actionCounts["Adjust Investment Allocation"]++;
      const surplus = Math.max(0, inc - curExp);
      curInv += (surplus * 0.75) + (curInv * ((0.07 + rsk * 0.05) / 12));
      curSav += (surplus * 0.25) + (curSav * (0.045 / 12));
    }

    const netWorth = curSav + curInv + curEmg - curDebt;
    const progress = Math.min(1, Math.max(0, netWorth / gol));
    const runway = curEmg / Math.max(1, curExp);
    const health = Math.min(100, Math.round(
      (Math.min(6, runway) / 6 * 30) +
      (curDebt === 0 ? 25 : Math.max(0, 25 - (curDebt / (inc * 12)) * 30)) +
      (Math.min(25, (curSav + curInv) / (inc * 6) * 25)) +
      (Math.min(20, Math.max(0, inc - curExp) / inc * 66))
    ));

    trajectory.push({
      month: m,
      income: Math.round(inc),
      expenses: Math.round(curExp),
      savings: Math.round(curSav),
      debt: Math.round(curDebt),
      investment: Math.round(curInv),
      emergency_fund: Math.round(curEmg),
      net_worth: Math.round(netWorth),
      goal_progress: Number(progress.toFixed(2)),
      action_name: actionName,
      health_score: health,
    });
  }

  const finalNetWorth = curSav + curInv + curEmg - curDebt;
  const finalHealth = trajectory[trajectory.length - 1].health_score;

  let strategy = "Maintain disciplined surplus allocation and sustain positive net cash flow";
  if (dbt > 0) {
    strategy = debtFreeMonth
      ? `Accelerate debt repayment to become completely debt-free by Month ${debtFreeMonth}, then redirect capital into high-growth investments`
      : "Aggressively curtail high-interest liabilities while maintaining a safe emergency buffer";
  } else if (rsk > 0.5) {
    strategy = "Systematically channel monthly surplus into compounding multi-asset growth funds";
  } else {
    strategy = "Increase savings and secure high-yield liquid emergency reserves";
  }

  return {
    status: "success",
    recommended_strategy: strategy,
    projected_savings: Math.round(curSav),
    projected_debt: Math.round(curDebt),
    projected_investments: Math.round(curInv),
    projected_emergency_fund: Math.round(curEmg),
    projected_net_worth: Math.round(finalNetWorth),
    goal_progress: Number(Math.min(1, Math.max(0, finalNetWorth / gol)).toFixed(2)),
    simulation_period_months: months,
    monthly_trajectory: trajectory,
    action_breakdown: actionCounts,
    risk_indicators: {
      initial_emergency_runway_months: Number((emg / Math.max(1, exp)).toFixed(1)),
      final_emergency_runway_months: Number((curEmg / Math.max(1, exp)).toFixed(1)),
      initial_debt_to_income_ratio: Number((dbt / Math.max(1, inc * 12)).toFixed(3)),
      final_debt_to_income_ratio: Number((curDebt / Math.max(1, inc * 12)).toFixed(3)),
      initial_health_score: initHealth,
      final_health_score: finalHealth,
      health_score_gain: finalHealth - initHealth,
      debt_free_month: debtFreeMonth,
    },
  };
}

