"use client";

import React, { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { AlertTriangle, Copy } from "lucide-react";

export function AnomalyBadge({ transaction, allTransactions = [] }) {
  const anomalyInfo = useMemo(() => {
    if (!transaction || transaction.type !== "EXPENSE") return null;

    const amount = Number(transaction.amount) || 0;
    if (amount <= 0) return null;

    // Check 1: Duplicate transaction detection (same amount & category within 2 days)
    const curDate = new Date(transaction.date).getTime();
    const duplicate = allTransactions.find((t) => {
      if (t.id === transaction.id) return false;
      const otherDate = new Date(t.date).getTime();
      const dayDiff = Math.abs(curDate - otherDate) / (1000 * 60 * 60 * 24);
      return (
        t.type === transaction.type &&
        Math.abs((Number(t.amount) || 0) - amount) < 0.01 &&
        dayDiff <= 2 &&
        t.category === transaction.category
      );
    });

    if (duplicate) {
      return {
        type: "duplicate",
        label: "Duplicate?",
        detail: `Matches another ${transaction.category} charge of $${amount.toFixed(2)} within 48h.`,
        color: "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30",
        icon: Copy,
      };
    }

    // Check 2: Category spend spike anomaly (> 2.5x category average)
    const categoryExpenses = allTransactions
      .filter((t) => t.category === transaction.category && t.type === "EXPENSE" && t.id !== transaction.id)
      .map((t) => Number(t.amount) || 0);

    if (categoryExpenses.length >= 3) {
      const avgCategory = categoryExpenses.reduce((a, b) => a + b, 0) / categoryExpenses.length;
      if (amount > avgCategory * 2.5 && amount > 100) {
        const factor = (amount / avgCategory).toFixed(1);
        return {
          type: "spike",
          label: `${factor}x Spend Spike`,
          detail: `This transaction is ${factor}x higher than your typical ${transaction.category} expense ($${avgCategory.toFixed(0)} avg).`,
          color: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30",
          icon: AlertTriangle,
        };
      }
    }

    return null;
  }, [transaction, allTransactions]);

  if (!anomalyInfo) return null;

  const Icon = anomalyInfo.icon;

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="inline-flex cursor-help">
            <Badge
              variant="outline"
              className={`gap-1 text-[10px] font-semibold px-1.5 py-0.5 border ${anomalyInfo.color} transition-colors`}
            >
              <Icon className="h-3 w-3 shrink-0" />
              <span>{anomalyInfo.label}</span>
            </Badge>
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-[220px] text-xs">
          {anomalyInfo.detail}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
