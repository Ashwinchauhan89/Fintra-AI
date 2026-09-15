"use server";

import {
  predictExpenseCategory,
  checkSpendingAnomaly,
  scanReceiptText,
  askCopilot,
  checkAffordability,
} from "@/lib/ml-client";

/**
 * Server action to predict category on demand.
 */
export async function getCategoryPrediction({ merchant, description, amount }) {
  try {
    const result = await predictExpenseCategory({ merchant, description, amount });
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Server action to audit transaction spending anomaly.
 */
export async function auditSpendingRisk({ merchant, amount, category }) {
  try {
    const result = await checkSpendingAnomaly({ merchant, amount, category });
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Server action to parse receipt text via ML OCR engine.
 */
export async function parseReceiptOCR(rawText) {
  try {
    const result = await scanReceiptText(rawText);
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Server action to converse with AI Financial Copilot.
 */
export async function askFinancialCopilot({
  userQuery,
  monthlyIncome,
  monthlyExpenses,
  currentBalance,
}) {
  try {
    const result = await askCopilot({
      userQuery,
      monthlyIncome,
      monthlyExpenses,
      currentBalance,
    });
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Server action to calculate purchase affordability.
 */
export async function solvePurchaseAffordability({
  itemName,
  itemPrice,
  monthlyIncome,
  monthlyExpenses,
  currentLiquidSavings,
  existingMonthlyEmi,
}) {
  try {
    const result = await checkAffordability({
      itemName,
      itemPrice,
      monthlyIncome,
      monthlyExpenses,
      currentLiquidSavings,
      existingMonthlyEmi,
    });
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

