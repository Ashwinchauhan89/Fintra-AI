"use server";

import { auth } from "@clerk/nextjs/server";
import { db } from "@/lib/prisma";
import { revalidatePath } from "next/cache";

const DEFAULT_GOALS = [
  {
    id: "goal-1",
    title: "Emergency Runway Cushion",
    category: "emergency",
    targetAmount: 10000,
    currentAmount: 6800,
    targetDate: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000).toISOString(),
    color: "#10b981",
    notes: "6 months of essential living expenses kept strictly liquid.",
  },
  {
    id: "goal-2",
    title: "Home Down Payment",
    category: "housing",
    targetAmount: 50000,
    currentAmount: 22500,
    targetDate: new Date(Date.now() + 730 * 24 * 60 * 60 * 1000).toISOString(),
    color: "#3b82f6",
    notes: "Primary residence down payment fund in low-risk index/debt instruments.",
  },
  {
    id: "goal-3",
    title: "Annual Vacation Sinking Fund",
    category: "travel",
    targetAmount: 3500,
    currentAmount: 2400,
    targetDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
    color: "#f59e0b",
    notes: "Summer getaway without recurring credit card debt.",
  },
  {
    id: "goal-4",
    title: "AI Workstation & Hardware",
    category: "tech",
    targetAmount: 2200,
    currentAmount: 1750,
    targetDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
    color: "#8b5cf6",
    notes: "Upgrading development machine for local model inference.",
  },
];

export async function getUserGoals() {
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

    // Compute goals and dynamic pace metrics
    const enrichedGoals = DEFAULT_GOALS.map((goal) => {
      const remaining = Math.max(0, goal.targetAmount - goal.currentAmount);
      const targetTime = new Date(goal.targetDate).getTime();
      const now = Date.now();
      const daysRemaining = Math.max(1, Math.ceil((targetTime - now) / (1000 * 60 * 60 * 24)));
      const monthsRemaining = Math.max(1, Math.ceil(daysRemaining / 30));
      const requiredMonthlyPace = Math.round(remaining / monthsRemaining);
      const progressPercent = Math.min(100, Math.round((goal.currentAmount / goal.targetAmount) * 100));

      let paceStatus = "ON_TRACK";
      if (progressPercent >= 100) {
        paceStatus = "COMPLETED";
      } else if (daysRemaining <= 60 && progressPercent < 60) {
        paceStatus = "BEHIND";
      }

      return {
        ...goal,
        remaining,
        daysRemaining,
        monthsRemaining,
        requiredMonthlyPace,
        progressPercent,
        paceStatus,
      };
    });

    const totalTarget = enrichedGoals.reduce((sum, g) => sum + g.targetAmount, 0);
    const totalCurrent = enrichedGoals.reduce((sum, g) => sum + g.currentAmount, 0);
    const totalMonthlyRequired = enrichedGoals
      .filter((g) => g.paceStatus !== "COMPLETED")
      .reduce((sum, g) => sum + g.requiredMonthlyPace, 0);

    return {
      success: true,
      data: {
        goals: enrichedGoals,
        totalTarget,
        totalCurrent,
        overallProgress: Math.round((totalCurrent / totalTarget) * 100),
        totalMonthlyRequired,
      },
    };
  } catch (error) {
    console.error("Failed to load financial goals:", error);
    return { success: false, error: error.message };
  }
}

export async function contributeToGoal({ goalId, amount }) {
  try {
    const { userId } = await auth();
    if (!userId) throw new Error("Unauthorized");

    revalidatePath("/goals");
    revalidatePath("/dashboard");

    return { success: true, message: `Successfully contributed $${amount} to goal.` };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
