"use server";

import { auth } from "@clerk/nextjs/server";
import { db } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { GoogleGenerativeAI } from "@google/generative-ai";
import aj from "@/lib/arcjet";
import { request } from "@arcjet/next";
import { z } from "zod";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const MAX_RECEIPT_SIZE = 5 * 1024 * 1024;
const RECEIPT_CATEGORIES = [
  "housing",
  "transportation",
  "groceries",
  "utilities",
  "entertainment",
  "food",
  "shopping",
  "healthcare",
  "education",
  "personal",
  "travel",
  "insurance",
  "gifts",
  "bills",
  "other-expense",
];
const receiptSchema = z.object({
  amount: z.coerce.number().finite().positive(),
  date: z.string().trim().min(1),
  description: z.string().trim().min(1).max(240),
  merchantName: z.string().trim().min(1).max(160),
  category: z.enum(RECEIPT_CATEGORIES),
});

const serializeDecimalFields = (obj) => {
  const serialized = { ...obj };

  if (obj.amount?.toNumber) {
    serialized.amount = obj.amount.toNumber();
  }

  if (obj.balance?.toNumber) {
    serialized.balance = obj.balance.toNumber();
  }

  return serialized;
};

const validateTransactionData = (data) => {
  const amount = Number(data.amount);

  if (!Number.isFinite(amount) || amount <= 0) {
    throw new Error("Transaction amount must be a positive number");
  }

  if (!data.accountId || !["INCOME", "EXPENSE"].includes(data.type)) {
    throw new Error("Invalid transaction account or type");
  }

  return { ...data, amount };
};

// Create Transaction
export async function createTransaction(data) {
  try {
    const { userId } = await auth();
    if (!userId) throw new Error("Unauthorized");

    // Get request data for ArcJet
    const req = await request();

    // Check rate limit
    const decision = await aj.protect(req, {
      userId,
      requested: 1, // Specify how many tokens to consume
    });

    if (decision.isDenied()) {
      if (decision.reason.isRateLimit()) {
        const { remaining, reset } = decision.reason;
        console.error({
          code: "RATE_LIMIT_EXCEEDED",
          details: {
            remaining,
            resetInSeconds: reset,
          },
        });

        throw new Error("Too many requests. Please try again later.");
      }

      throw new Error("Request blocked");
    }

    const user = await db.user.findUnique({
      where: { clerkUserId: userId },
    });

    if (!user) {
      throw new Error("User not found");
    }

    const validatedData = validateTransactionData(data);

    // Create the transaction and update the balance atomically.
    const transaction = await db.$transaction(async (tx) => {
      const account = await tx.account.findFirst({
        where: {
          id: validatedData.accountId,
          userId: user.id,
        },
        select: { id: true },
      });

      if (!account) {
        throw new Error("Account not found");
      }

      const newTransaction = await tx.transaction.create({
        data: {
          ...validatedData,
          userId: user.id,
          nextRecurringDate:
            validatedData.isRecurring && validatedData.recurringInterval
              ? calculateNextRecurringDate(validatedData.date, validatedData.recurringInterval)
              : null,
        },
      });

      await tx.account.update({
        where: { id: account.id },
        data: {
          balance: {
            increment:
              validatedData.type === "EXPENSE"
                ? -validatedData.amount
                : validatedData.amount,
          },
        },
      });

      return newTransaction;
    });

    revalidatePath("/dashboard");
    revalidatePath(`/account/${transaction.accountId}`);

    return { success: true, data: serializeDecimalFields(transaction) };
  } catch (error) {
    throw new Error(error.message);
  }
}

export async function getTransaction(id) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthorized");

  const user = await db.user.findUnique({
    where: { clerkUserId: userId },
  });

  if (!user) throw new Error("User not found");

  const transaction = await db.transaction.findFirst({
    where: {
      id,
      userId: user.id,
    },
  });

  if (!transaction) throw new Error("Transaction not found");

  return serializeDecimalFields(transaction);
}

export async function updateTransaction(id, data) {
  try {
    const { userId } = await auth();
    if (!userId) throw new Error("Unauthorized");

    const user = await db.user.findUnique({
      where: { clerkUserId: userId },
    });

    if (!user) throw new Error("User not found");

    const validatedData = validateTransactionData(data);

    // Re-read and mutate all affected records in one transaction so the
    // original transaction and account balances cannot drift apart.
    const transaction = await db.$transaction(async (tx) => {
      const originalTransaction = await tx.transaction.findFirst({
        where: { id, userId: user.id },
      });

      if (!originalTransaction) throw new Error("Transaction not found");

      const destinationAccount = await tx.account.findFirst({
        where: {
          id: validatedData.accountId,
          userId: user.id,
        },
        select: { id: true },
      });

      if (!destinationAccount) throw new Error("Account not found");

      const oldBalanceChange =
        originalTransaction.type === "EXPENSE"
          ? -originalTransaction.amount.toNumber()
          : originalTransaction.amount.toNumber();
      const newBalanceChange =
        validatedData.type === "EXPENSE"
          ? -validatedData.amount
          : validatedData.amount;

      if (originalTransaction.accountId === destinationAccount.id) {
        await tx.account.update({
          where: { id: destinationAccount.id },
          data: {
            balance: { increment: newBalanceChange - oldBalanceChange },
          },
        });
      } else {
        await tx.account.update({
          where: { id: originalTransaction.accountId },
          data: { balance: { increment: -oldBalanceChange } },
        });
        await tx.account.update({
          where: { id: destinationAccount.id },
          data: { balance: { increment: newBalanceChange } },
        });
      }

      return tx.transaction.update({
        where: { id },
        data: {
          ...validatedData,
          nextRecurringDate:
            validatedData.isRecurring && validatedData.recurringInterval
              ? calculateNextRecurringDate(validatedData.date, validatedData.recurringInterval)
              : null,
        },
      });
    });

    revalidatePath("/dashboard");
    revalidatePath(`/account/${transaction.accountId}`);
    if (transaction.accountId !== data.accountId) {
      revalidatePath(`/account/${data.accountId}`);
    }

    return { success: true, data: serializeDecimalFields(transaction) };
  } catch (error) {
    throw new Error(error.message);
  }
}

// Get User Transactions
export async function getUserTransactions(query = {}) {
  try {
    const { userId } = await auth();
    if (!userId) throw new Error("Unauthorized");

    const user = await db.user.findUnique({
      where: { clerkUserId: userId },
    });

    if (!user) {
      throw new Error("User not found");
    }

    const transactions = await db.transaction.findMany({
      where: {
        ...query,
        userId: user.id,
      },
      include: {
        account: true,
      },
      orderBy: {
        date: "desc",
      },
    });

    return {
      success: true,
      data: transactions.map((transaction) => ({
        ...serializeDecimalFields(transaction),
        account: transaction.account
          ? serializeDecimalFields(transaction.account)
          : transaction.account,
      })),
    };
  } catch (error) {
    throw new Error(error.message);
  }
}

// Scan Receipt
const hasSupportedImageSignature = (bytes, mimeType) => {
  if (mimeType === "image/jpeg") {
    return bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
  }
  if (mimeType === "image/png") {
    return bytes.slice(0, 8).join(",") === "137,80,78,71,13,10,26,10";
  }
  if (mimeType === "image/gif") {
    return new TextDecoder().decode(bytes.slice(0, 4)) === "GIF8";
  }
  if (mimeType === "image/webp") {
    return (
      new TextDecoder().decode(bytes.slice(0, 4)) === "RIFF" &&
      new TextDecoder().decode(bytes.slice(8, 12)) === "WEBP"
    );
  }
  return false;
};

export async function scanReceipt(file) {
  try {
    const { userId } = await auth();
    if (!userId) throw new Error("Unauthorized");

    const req = await request();
    const decision = await aj.protect(req, { userId, requested: 1 });
    if (decision.isDenied()) throw new Error("Receipt scan request blocked");

    if (!file || typeof file.arrayBuffer !== "function") {
      throw new Error("A receipt image is required");
    }
    if (!file.size || file.size > MAX_RECEIPT_SIZE) {
      throw new Error("Receipt image must be between 1 byte and 5 MB");
    }
    if (!["image/jpeg", "image/png", "image/gif", "image/webp"].includes(file.type)) {
      throw new Error("Only JPEG, PNG, GIF, and WebP receipts are supported");
    }

    const arrayBuffer = await file.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    if (!hasSupportedImageSignature(bytes, file.type)) {
      throw new Error("Receipt content does not match its image type");
    }

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    const base64String = Buffer.from(arrayBuffer).toString("base64");
    const prompt = `
      Analyze this receipt image and extract the following information in JSON format:
      - Total amount (just the number)
      - Date (in ISO format)
      - Description or items purchased (brief summary)
      - Merchant/store name
      - Suggested category (one of: ${RECEIPT_CATEGORIES.join(", ")})

      Only respond with valid JSON in this exact format:
      {
        "amount": number,
        "date": "ISO date string",
        "description": "string",
        "merchantName": "string",
        "category": "string"
      }
    `;

    const result = await model.generateContent([
      { inlineData: { data: base64String, mimeType: file.type } },
      prompt,
    ]);
    const response = await result.response;
    const cleanedText = response.text().replace(/```(?:json)?\n?/g, "").trim();
    const parsed = receiptSchema.safeParse(JSON.parse(cleanedText));

    if (!parsed.success || Number.isNaN(new Date(parsed.data?.date).getTime())) {
      throw new Error("Invalid receipt data returned by Gemini");
    }

    return {
      ...parsed.data,
      date: new Date(parsed.data.date),
    };
  } catch (error) {
    console.error("Error scanning receipt:", error);
    throw new Error(error.message || "Failed to scan receipt");
  }
}

// Helper function to calculate next recurring date
function calculateNextRecurringDate(startDate, interval) {
  const date = new Date(startDate);

  switch (interval) {
    case "DAILY":
      date.setDate(date.getDate() + 1);
      break;
    case "WEEKLY":
      date.setDate(date.getDate() + 7);
      break;
    case "MONTHLY":
      date.setMonth(date.getMonth() + 1);
      break;
    case "YEARLY":
      date.setFullYear(date.getFullYear() + 1);
      break;
  }

  return date;
}
