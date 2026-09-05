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
