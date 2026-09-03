"use server";

import {
  predictExpenseCategory,
  checkSpendingAnomaly,
  scanReceiptText,
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
