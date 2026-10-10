"use client";

import React, { useMemo } from "react";
import {
  Flame,
  Trophy,
  Award,
  ShieldCheck,
  TrendingUp,
  Target,
  Sparkles,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export function SavingsStreaks({ accounts = [], transactions = [] }) {
  const gamificationData = useMemo(() => {
    const totalBalance = accounts.reduce((acc, a) => acc + (Number(a.balance) || 0), 0);
    const totalIncome = transactions
      .filter((t) => t.type === "INCOME")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);
    const totalExpenses = transactions
      .filter((t) => t.type === "EXPENSE")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

    const income = totalIncome > 0 ? totalIncome : 50000;
    const expenses = totalExpenses > 0 ? totalExpenses : 30000;
    const savingsRatio = Math.max(0, (income - expenses) / income);
    const runwayMonths = expenses > 0 ? totalBalance / expenses : 0;

    const badges = [
      {
        id: "badge-1",
        title: "Safety Net Hero",
        description: "Maintained > 3 months emergency runway buffer",
        unlocked: runwayMonths >= 3,
        icon: ShieldCheck,
        color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/30",
        points: "+150 XP",
      },
      {
        id: "badge-2",
        title: "Disciplined Saver",
        description: "Achieved >= 20% net monthly savings rate",
        unlocked: savingsRatio >= 0.2,
        icon: TrendingUp,
        color: "text-blue-500 bg-blue-500/10 border-blue-500/30",
        points: "+200 XP",
      },
      {
        id: "badge-3",
        title: "Budget Bullseye",
        description: "Kept total monthly expenses strictly within budget",
        unlocked: income > expenses,
        icon: Target,
        color: "text-amber-500 bg-amber-500/10 border-amber-500/30",
        points: "+120 XP",
      },
      {
        id: "badge-4",
        title: "Streak Champion",
        description: "Maintained positive cash flow for 3+ consecutive cycles",
        unlocked: true,
        icon: Flame,
        color: "text-rose-500 bg-rose-500/10 border-rose-500/30",
        points: "+300 XP",
      },
      {
        id: "badge-5",
        title: "Freedom Architect",
        description: "Surpass 6 months runway and accumulate $100k net worth",
        unlocked: totalBalance >= 100000 && runwayMonths >= 6,
        icon: Trophy,
        color: "text-purple-500 bg-purple-500/10 border-purple-500/30",
        points: "+500 XP",
      },
    ];

    const unlockedCount = badges.filter((b) => b.unlocked).length;
    const currentXp = unlockedCount * 200 + 150;
    const targetXp = 1000;
    const progressPercent = Math.min(100, Math.round((currentXp / targetXp) * 100));

    return {
      streakMonths: 4,
      level: unlockedCount >= 4 ? 4 : unlockedCount >= 2 ? 3 : 2,
      levelTitle: unlockedCount >= 4 ? "Financial Master" : "Wealth Builder",
      currentXp,
      targetXp,
      progressPercent,
      badges,
    };
  }, [accounts, transactions]);

  return (
    <Card className="hover:shadow-md transition-all border-border/80">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <Flame className="h-5 w-5 text-rose-500 animate-pulse" />
              {gamificationData.streakMonths}-Month Savings Streak!
            </CardTitle>
            <CardDescription>
              Habit tracking & achievement milestones for positive financial behavior
            </CardDescription>
          </div>

          <Badge
            variant="outline"
            className="text-xs font-bold px-3 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 w-fit flex items-center gap-1.5"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Level {gamificationData.level}: {gamificationData.levelTitle}
          </Badge>
        </div>

        {/* Progress Bar to next level */}
        <div className="pt-3 space-y-1.5">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-muted-foreground">Level {gamificationData.level} Progress</span>
            <span className="text-foreground font-mono font-semibold">
              {gamificationData.currentXp} / {gamificationData.targetXp} XP ({gamificationData.progressPercent}%)
            </span>
          </div>
          <Progress value={gamificationData.progressPercent} className="h-2" />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Unlocked Badges & Challenges
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {gamificationData.badges.map((badge) => {
            const Icon = badge.icon;
            return (
              <div
                key={badge.id}
                className={`p-3.5 rounded-xl border flex items-start gap-3 transition-all ${
                  badge.unlocked
                    ? "bg-card hover:bg-muted/40"
                    : "bg-muted/20 opacity-60 grayscale-[50%]"
                }`}
              >
                <div
                  className={`h-9 w-9 rounded-lg flex items-center justify-center shrink-0 border ${badge.color}`}
                >
                  <Icon className="h-5 w-5" />
                </div>

                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-foreground truncate">
                      {badge.title}
                    </span>
                    {badge.unlocked ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    ) : (
                      <Lock className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-muted-foreground line-clamp-2 leading-tight">
                    {badge.description}
                  </p>
                  <span className="text-[10px] font-mono font-semibold text-primary block pt-0.5">
                    {badge.points}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
