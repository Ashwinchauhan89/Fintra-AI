"use server";

import { auth } from "@clerk/nextjs/server";
import { db } from "@/lib/prisma";

const KNOWN_SUBSCRIPTIONS = [
  { pattern: /netflix/i, name: "Netflix", category: "entertainment", defaultCost: 19.99 },
  { pattern: /spotify/i, name: "Spotify", category: "entertainment", defaultCost: 10.99 },
  { pattern: /youtube/i, name: "YouTube Premium", category: "entertainment", defaultCost: 13.99 },
  { pattern: /prime|amazon\s*prime/i, name: "Amazon Prime", category: "entertainment", defaultCost: 14.99 },
  { pattern: /apple|icloud/i, name: "Apple One / iCloud", category: "utilities", defaultCost: 9.99 },
  { pattern: /chatgpt|openai/i, name: "ChatGPT Plus", category: "education", defaultCost: 20.00 },
  { pattern: /github/i, name: "GitHub Copilot", category: "education", defaultCost: 10.00 },
  { pattern: /gym|fitness/i, name: "Gym Membership", category: "healthcare", defaultCost: 45.00 },
  { pattern: /broadband|wifi|internet/i, name: "Home Internet", category: "utilities", defaultCost: 60.00 },
  { pattern: /adobe/i, name: "Adobe Creative Cloud", category: "personal", defaultCost: 35.99 },
];

export async function getUserSubscriptions() {
  try {
    const { userId } = await auth();
    if (!userId) {
      return { success: false, error: "Unauthorized" };
    }

    const user = await db.user.findUnique({
      where: { clerkUserId: userId },
    });

    if (!user) {
      return { success: false, error: "User not found" };
    }

    // 1. Fetch explicitly flagged recurring transactions
    const recurringTxs = await db.transaction.findMany({
      where: {
        userId: user.id,
        isRecurring: true,
      },
      include: {
        account: {
          select: { name: true },
        },
      },
      orderBy: { date: "desc" },
    });

    // 2. Fetch recent transactions to discover unflagged recurring subscriptions
    const recentTxs = await db.transaction.findMany({
      where: {
        userId: user.id,
        type: "EXPENSE",
      },
      take: 100,
      orderBy: { date: "desc" },
    });

    const discoveredSubs = new Map();

    // Add explicitly recurring transactions first
    recurringTxs.forEach((tx) => {
      const amount = Number(tx.amount) || 0;
      discoveredSubs.set(tx.description.toLowerCase(), {
        id: tx.id,
        name: tx.description,
        category: tx.category,
        amount,
        interval: tx.recurringInterval || "MONTHLY",
        nextPayment: tx.nextRecurringDate ? new Date(tx.nextRecurringDate).toISOString() : new Date().toISOString(),
        accountName: tx.account?.name || "Main Account",
        isDetected: false,
      });
    });

    // Match against known subscription catalog
    recentTxs.forEach((tx) => {
      const desc = tx.description || "";
      for (const sub of KNOWN_SUBSCRIPTIONS) {
        if (sub.pattern.test(desc) && !discoveredSubs.has(desc.toLowerCase())) {
          const amount = Number(tx.amount) || sub.defaultCost;
          discoveredSubs.set(desc.toLowerCase(), {
            id: tx.id,
            name: sub.name,
            category: sub.category,
            amount,
            interval: "MONTHLY",
            nextPayment: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
            accountName: "Detected via Transactions",
            isDetected: true,
          });
          break;
        }
      }
    });

    const subscriptionsList = Array.from(discoveredSubs.values());

    // Calculate monthly commitment total
    let monthlyTotal = 0;
    subscriptionsList.forEach((sub) => {
      if (sub.interval === "YEARLY") {
        monthlyTotal += sub.amount / 12;
      } else if (sub.interval === "WEEKLY") {
        monthlyTotal += sub.amount * 4.33;
      } else if (sub.interval === "DAILY") {
        monthlyTotal += sub.amount * 30;
      } else {
        monthlyTotal += sub.amount;
      }
    });

    return {
      success: true,
      data: {
        subscriptions: subscriptionsList,
        monthlyTotal: Math.round(monthlyTotal * 100) / 100,
        annualTotal: Math.round(monthlyTotal * 12 * 100) / 100,
        activeCount: subscriptionsList.length,
      },
    };
  } catch (error) {
    console.error("Failed to load subscriptions:", error);
    return { success: false, error: error.message };
  }
}
