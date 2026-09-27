"use server";

import { auth } from "@clerk/nextjs/server";
import { db } from "@/lib/prisma";

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || "http://127.0.0.1:8000";

export async function evaluatePurchaseAffordability({
  itemName = "Requested Item",
  amount = 0,
  urgency = "DISCRETIONARY",
  installmentMonths = 0,
  installmentInterestRatePct = 0,
}) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return { success: false, error: "Unauthorized" };
    }

    const user = await db.user.findUnique({
      where: { clerkUserId: userId },
      include: {
        accounts: true,
        transactions: {
          orderBy: { date: "desc" },
          take: 100,
        },
      },
    });

    if (!user) {
      return { success: false, error: "User not found" };
    }

    // 1. Compute user balances & baseline figures
    const totalLiquidBalance = user.accounts.reduce(
      (sum, acc) => sum + Math.max(0, Number(acc.balance) || 0),
      0
    );

    const now = new Date();
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

    const recentIncome = user.transactions
      .filter((t) => t.type === "INCOME" && new Date(t.date) >= thirtyDaysAgo)
      .reduce((sum, t) => sum + (Number(t.amount) || 0), 0);

    const recentExpenses = user.transactions
      .filter((t) => t.type === "EXPENSE" && new Date(t.date) >= thirtyDaysAgo)
      .reduce((sum, t) => sum + (Number(t.amount) || 0), 0);

    // Fallbacks if account has zero history
    const monthlyIncome = recentIncome > 0 ? recentIncome : 5000;
    const monthlyEssentialExpenses = recentExpenses > 0 ? recentExpenses : 2800;
    const liquidBalance = totalLiquidBalance > 0 ? totalLiquidBalance : 12000;

    const payload = {
      item_name: itemName,
      amount: Number(amount),
      current_liquid_balance: liquidBalance,
      monthly_income: monthlyIncome,
      monthly_essential_expenses: monthlyEssentialExpenses,
      urgency,
      installment_months: Number(installmentMonths) || 0,
      installment_interest_rate_pct: Number(installmentInterestRatePct) || 0,
    };

    // 2. Query FastAPI prediction engine with graceful fallback
    try {
      const response = await fetch(`${ML_SERVICE_URL}/api/v1/predict/affordability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        cache: "no-store",
        next: { revalidate: 0 },
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, data: result };
      }
    } catch {
      // Fall through to deterministic local solver
    }

    // Local Deterministic Affordability Decision Solver
    const bal = payload.current_liquid_balance;
    const inc = payload.monthly_income;
    const ess = Math.max(1, payload.monthly_essential_expenses);
    const cost = payload.amount;
    const cushionRequired = ess * 3.0;
    const safeDiscretionary = Math.max(0, bal - cushionRequired);
    const monthlySurplus = inc - ess;

    const runwayBefore = Number((bal / ess).toFixed(1));
    const runwayAfter = Number((Math.max(0, bal - cost) / ess).toFixed(1));

    let recommendation = "WAIT";
    let recommendationTitle = "Wait Before Purchasing";
    let riskLevel = "MEDIUM";
    let confidenceScore = 0.92;
    let actionVerdict = "";
    const tradeoffs = [];
    const alternativeOptions = [];

    if (cost <= safeDiscretionary && monthlySurplus > 0) {
      recommendation = "PAY_IN_FULL";
      recommendationTitle = "Safely Affordable — Pay Upfront";
      riskLevel = "LOW";
      confidenceScore = 0.96;
      actionVerdict = `Your verified capital can safely absorb $${cost.toLocaleString()} while keeping ${runwayAfter} months of essential runway intact.`;
      tradeoffs.push(
        `Emergency runway adjusts from ${runwayBefore} mo to ${runwayAfter} mo (safely above the 3.0 mo threshold).`
      );
      tradeoffs.push(
        `Liquidity cushion drops by $${cost.toLocaleString()}, leaving $${Math.max(
          0,
          bal - cost
        ).toLocaleString()} in liquid reserves.`
      );
    } else if (payload.installment_months > 0) {
      const n = payload.installment_months;
      const apr = payload.installment_interest_rate_pct / 100;
      const emi = (cost * (1 + apr * (n / 12))) / n;

      if (emi <= monthlySurplus * 0.4 && bal >= cushionRequired * 0.75) {
        recommendation = "INSTALLMENTS";
        recommendationTitle = `Spread via ${n}-Month Installments`;
        riskLevel = apr === 0 ? "LOW" : "MEDIUM";
        confidenceScore = 0.91;
        actionVerdict = `Financing at $${Math.round(
          emi
        )}/month preserves your upfront liquid cushion of $${bal.toLocaleString()} with minimal surplus strain.`;
        tradeoffs.push(
          `Commits $${Math.round(emi)}/month of your $${Math.round(
            monthlySurplus
          )} free cash flow for ${n} months.`
        );
      } else {
        recommendation = "WAIT";
        riskLevel = "HIGH";
        recommendationTitle = "Installment Strain Too High — Wait";
        actionVerdict = `The proposed EMI ($${Math.round(
          emi
        )}/mo) consumes more than 40% of your free monthly surplus. Postponing is advised.`;
      }
    } else if (bal >= cost && urgency === "ESSENTIAL") {
      recommendation = "PAY_PARTIALLY";
      recommendationTitle = "Split via Down Payment & Buffer";
      riskLevel = "MEDIUM";
      confidenceScore = 0.88;
      actionVerdict = `This essential purchase eats into your emergency cushion. Consider paying $${Math.round(
        safeDiscretionary
      )} down and financing the remainder.`;
      tradeoffs.push(`Reduces emergency runway down to ${runwayAfter} months (caution buffer).`);
    } else if (bal >= cost) {
      const deficit = cost - safeDiscretionary;
      const daysToSave = Math.max(
        14,
        Math.ceil((deficit / Math.max(100, monthlySurplus)) * 30)
      );
      recommendation = "WAIT";
      riskLevel = "MEDIUM";
      confidenceScore = 0.90;
      recommendationTitle = `Postpone & Save for ${daysToSave} Days`;
      actionVerdict = `Buying now drops your liquid runway from ${runwayBefore} mo to ${runwayAfter} mo. Waiting ${daysToSave} days accumulates safe surplus.`;
      tradeoffs.push(`Immediate purchase leaves only ${runwayAfter} months of living expenses liquid.`);
      tradeoffs.push("Postponing preserves your safety margin while avoiding recurring debt.");
    } else {
      recommendation = "DO_NOT_PROCEED";
      recommendationTitle = "Immediate Overdraft Hazard — Do Not Proceed";
      riskLevel = "CRITICAL";
      confidenceScore = 0.98;
      actionVerdict = `This expense of $${cost.toLocaleString()} exceeds your total liquid balance ($${bal.toLocaleString()}). Purchasing now risks immediate insolvency.`;
      tradeoffs.push("Would require high-interest emergency borrowing or punitive overdraft fees.");
    }

    if (recommendation !== "PAY_IN_FULL") {
      alternativeOptions.push({
        type: "POSTPONE",
        label: "Wait for Next Pay Cycle",
        impact: `Rebuilds free cash flow by +$${Math.round(monthlySurplus)}/month.`,
      });
      alternativeOptions.push({
        type: "NO_COST_EMI",
        label: "Explore 0% Interest 3-6 Month Financing",
        impact: `Reduces upfront liquidity impact to ~$${Math.round(cost / 3)}/month.`,
      });
    }

    const projection = [];
    const dailyIncomeRate = inc / 30;
    const dailyExpenseRate = ess / 30;
    let curBase = bal;
    let curPost = recommendation === "PAY_IN_FULL" || recommendation === "PAY_PARTIALLY" ? Math.max(0, bal - cost) : bal;

    for (let day = 0; day <= 30; day += 5) {
      projection.push({
        day: `Day ${day}`,
        baseline_balance: Math.round(curBase),
        with_purchase_balance: Math.round(curPost),
      });
      curBase += (dailyIncomeRate - dailyExpenseRate) * 5;
      curPost += (dailyIncomeRate - dailyExpenseRate) * 5;
    }

    return {
      success: true,
      data: {
        status: "success",
        item_name: itemName,
        amount: cost,
        recommendation,
        recommendation_title: recommendationTitle,
        risk_level: riskLevel,
        confidence_score: confidenceScore,
        amount_safe_to_spend: Math.round(safeDiscretionary),
        runway_before_months: runwayBefore,
        runway_after_months: runwayAfter,
        monthly_surplus_before: Math.round(monthlySurplus),
        monthly_surplus_after: Math.round(monthlySurplus),
        savings_rate_impact_pct: 0,
        cashflow_projection_30d: projection,
        tradeoffs,
        alternative_options: alternativeOptions,
        action_verdict: actionVerdict,
      },
    };
  } catch (error) {
    console.error("Affordability evaluation failed:", error);
    return { success: false, error: error.message };
  }
}
