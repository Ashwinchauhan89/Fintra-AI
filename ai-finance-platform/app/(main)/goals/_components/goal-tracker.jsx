"use client";

import React, { useState } from "react";
import {
  Target,
  ShieldCheck,
  Home,
  Plane,
  Laptop,
  Plus,
  TrendingUp,
  Clock,
  Sparkles,
  Calendar,
  CheckCircle2,
  DollarSign,
  ArrowUpRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { format } from "date-fns";

const CATEGORY_ICONS = {
  emergency: ShieldCheck,
  housing: Home,
  travel: Plane,
  tech: Laptop,
  default: Target,
};

export function GoalTracker({ initialData }) {
  const [goalsData, setGoalsData] = useState(initialData);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [contributionAmount, setContributionAmount] = useState("");

  const { goals = [], totalTarget = 0, totalCurrent = 0, overallProgress = 0, totalMonthlyRequired = 0 } = goalsData || {};

  const handleQuickAdd = (goal) => {
    setSelectedGoal(goal);
    setContributionAmount("250");
  };

  const handleConfirmContribution = (e) => {
    e.preventDefault();
    const amount = Number(contributionAmount);
    if (!selectedGoal || amount <= 0) return;

    setGoalsData((prev) => {
      const updatedGoals = prev.goals.map((g) => {
        if (g.id === selectedGoal.id) {
          const newCurrent = g.currentAmount + amount;
          const newProgress = Math.min(100, Math.round((newCurrent / g.targetAmount) * 100));
          return {
            ...g,
            currentAmount: newCurrent,
            remaining: Math.max(0, g.targetAmount - newCurrent),
            progressPercent: newProgress,
            paceStatus: newProgress >= 100 ? "COMPLETED" : g.paceStatus,
          };
        }
        return g;
      });

      const newTotalCurrent = updatedGoals.reduce((sum, g) => sum + g.currentAmount, 0);

      return {
        ...prev,
        goals: updatedGoals,
        totalCurrent: newTotalCurrent,
        overallProgress: Math.round((newTotalCurrent / prev.totalTarget) * 100),
      };
    });

    toast.success(`Allocated $${amount} to ${selectedGoal.title}!`);
    setSelectedGoal(null);
    setContributionAmount("");
  };

  return (
    <div className="space-y-6">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Total Goal Capital
            </CardTitle>
            <Target className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              ${totalTarget.toLocaleString()}
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Combined milestone targets
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Accumulated Funds
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              ${totalCurrent.toLocaleString()}
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Saved across sinking funds
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Overall Completion
            </CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              {overallProgress}%
            </div>
            <div className="mt-2">
              <Progress value={overallProgress} className="h-1.5" />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow border-primary/20 bg-primary/5">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-primary">
              Monthly Required Pace
            </CardTitle>
            <DollarSign className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-primary">
              ${totalMonthlyRequired.toLocaleString()}/mo
            </div>
            <p className="text-[11px] text-primary/80 mt-1">
              To hit all deadlines on time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Contribution Drawer / Modal */}
      {selectedGoal && (
        <Card className="border-primary/30 bg-card shadow-xl p-4 animate-in fade-in duration-200">
          <form onSubmit={handleConfirmContribution} className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="space-y-0.5 text-center sm:text-left">
              <div className="text-sm font-bold flex items-center gap-2 text-foreground">
                <Sparkles className="h-4 w-4 text-amber-500" />
                Add Contribution to {selectedGoal.title}
              </div>
              <p className="text-xs text-muted-foreground">
                Remaining: ${selectedGoal.remaining.toLocaleString()} | Deadline: {format(new Date(selectedGoal.targetDate), "MMM yyyy")}
              </p>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-36">
                <span className="absolute left-2.5 top-2 text-xs font-bold text-muted-foreground">$</span>
                <Input
                  type="number"
                  min="1"
                  value={contributionAmount}
                  onChange={(e) => setContributionAmount(e.target.value)}
                  className="pl-6 text-xs h-8"
                  placeholder="Amount"
                  required
                />
              </div>
              <Button type="submit" size="sm" className="text-xs h-8 px-4 font-semibold">
                Confirm
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setSelectedGoal(null)}
                className="text-xs h-8"
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {goals.map((goal) => {
          const Icon = CATEGORY_ICONS[goal.category] || CATEGORY_ICONS.default;
          return (
            <Card key={goal.id} className="hover:shadow-md transition-all border-border/80 flex flex-col justify-between">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="h-9 w-9 rounded-xl flex items-center justify-center shrink-0 border"
                      style={{ backgroundColor: `${goal.color}15`, borderColor: `${goal.color}30`, color: goal.color }}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-sm font-bold text-foreground">
                        {goal.title}
                      </CardTitle>
                      <CardDescription className="text-[11px]">
                        Target Date: {format(new Date(goal.targetDate), "MMMM yyyy")} ({goal.daysRemaining} days left)
                      </CardDescription>
                    </div>
                  </div>

                  <Badge
                    variant="outline"
                    className={`text-[10px] font-bold px-2 py-0.5 ${
                      goal.paceStatus === "COMPLETED"
                        ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
                        : goal.paceStatus === "ON_TRACK"
                        ? "bg-blue-500/10 text-blue-600 border-blue-500/30"
                        : "bg-amber-500/10 text-amber-600 border-amber-500/30"
                    }`}
                  >
                    {goal.paceStatus === "COMPLETED"
                      ? "Achieved 🎉"
                      : goal.paceStatus === "ON_TRACK"
                      ? "On Track"
                      : "Pace Alert"}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Progress Bar & Amount Numbers */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="font-mono text-foreground font-bold">
                      ${goal.currentAmount.toLocaleString()}
                    </span>
                    <span className="text-muted-foreground font-mono">
                      ${goal.targetAmount.toLocaleString()} ({goal.progressPercent}%)
                    </span>
                  </div>
                  <Progress value={goal.progressPercent} className="h-2" />
                </div>

                {/* Pace Details */}
                <div className="p-2.5 rounded-lg bg-muted/30 border grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-[10px] text-muted-foreground block">Required Savings Pace</span>
                    <span className="font-bold text-foreground font-mono">
                      ${goal.requiredMonthlyPace.toLocaleString()}/mo
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-muted-foreground block">Remaining Deficit</span>
                    <span className="font-bold text-primary font-mono">
                      ${goal.remaining.toLocaleString()}
                    </span>
                  </div>
                </div>

                {goal.notes && (
                  <p className="text-[11px] text-muted-foreground italic leading-tight">
                    &ldquo;{goal.notes}&rdquo;
                  </p>
                )}

                <div className="pt-1 flex items-center justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickAdd(goal)}
                    className="text-xs h-7 gap-1 font-semibold hover:bg-primary hover:text-primary-foreground transition-colors"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Quick Allocate
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* AI Goal Strategy Insight */}
      <Card className="border-primary/20 bg-gradient-to-r from-primary/5 via-card to-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-500" />
            AI Sinking Fund Intelligence & Automated Rule
          </CardTitle>
        </CardHeader>
        <CardContent className="text-xs text-muted-foreground space-y-1.5 leading-relaxed">
          <p>
            By setting up automated bank transfers on salary day equal to your <strong>${totalMonthlyRequired.toLocaleString()}/mo</strong> combined goal pace, you eliminate the cognitive burden of saving and prevent lifestyle inflation from eroding your emergency runway.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
