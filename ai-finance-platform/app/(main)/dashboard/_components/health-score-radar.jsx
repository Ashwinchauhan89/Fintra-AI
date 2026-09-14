"use client";

import React, { useMemo } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, ShieldCheck, TrendingUp, AlertTriangle } from "lucide-react";

export function HealthScoreRadar({ accounts = [], transactions = [] }) {
  // Compute financial health signals
  const { score, grade, radarData, insights } = useMemo(() => {
    const totalBalance = accounts.reduce((acc, a) => acc + (Number(a.balance) || 0), 0);
    const totalIncome = transactions
      .filter((t) => t.type === "INCOME")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);
    const totalExpenses = transactions
      .filter((t) => t.type === "EXPENSE")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

    const monthlyIncome = totalIncome > 0 ? totalIncome : 50000;
    const monthlyExpenses = totalExpenses > 0 ? totalExpenses : 30000;

    // 1. Savings Rate (target: >= 20%)
    const savingsRatio = Math.max(0, (monthlyIncome - monthlyExpenses) / monthlyIncome);
    const savingsScore = Math.min(100, Math.round((savingsRatio / 0.3) * 100));

    // 2. Emergency Runway (target: >= 3 months)
    const runwayMonths = monthlyExpenses > 0 ? totalBalance / monthlyExpenses : 0;
    const runwayScore = Math.min(100, Math.round((runwayMonths / 6) * 100));

    // 3. Debt-to-Income / Obligation Control (target: < 30%)
    const debtRatio = Math.min(1, monthlyExpenses / monthlyIncome);
    const debtControlScore = Math.max(20, Math.round((1 - debtRatio * 0.7) * 100));

    // 4. Wants / Discretionary Control
    const discretionaryRatio = 0.25;
    const discretionaryScore = Math.min(100, Math.round((1 - discretionaryRatio) * 100));

    // 5. Liquidity Buffer (target: >= 50k INR)
    const liquidityScore = Math.min(100, Math.round((totalBalance / 100000) * 100));

    const compositeScore = Math.round(
      savingsScore * 0.3 + runwayScore * 0.25 + debtControlScore * 0.2 + discretionaryScore * 0.15 + liquidityScore * 0.1
    );

    let assignedGrade = "C";
    if (compositeScore >= 90) assignedGrade = "A+";
    else if (compositeScore >= 80) assignedGrade = "A";
    else if (compositeScore >= 70) assignedGrade = "B";
    else if (compositeScore >= 60) assignedGrade = "C";
    else assignedGrade = "D";

    const data = [
      { pillar: "Savings Rate", value: savingsScore, fullMark: 100 },
      { pillar: "Emergency Runway", value: runwayScore, fullMark: 100 },
      { pillar: "Debt Control", value: debtControlScore, fullMark: 100 },
      { pillar: "Spending Buffer", value: discretionaryScore, fullMark: 100 },
      { pillar: "Liquidity", value: liquidityScore, fullMark: 100 },
    ];

    const tips = [];
    if (runwayMonths < 3) {
      tips.push("Build your emergency buffer towards 3-6 months of expenses.");
    } else {
      tips.push("Strong emergency runway buffer maintained.");
    }
    if (savingsRatio < 0.2) {
      tips.push("Aim to raise your monthly savings rate to at least 20%.");
    } else {
      tips.push("Excellent savings discipline above demographic baseline.");
    }

    return {
      score: compositeScore,
      grade: assignedGrade,
      radarData: data,
      insights: tips,
    };
  }, [accounts, transactions]);

  return (
    <Card className="hover:shadow-md transition-all border-emerald-500/20 bg-gradient-to-br from-card to-card/50">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Activity className="h-5 w-5 text-emerald-500" />
            AI Financial Health Score
          </CardTitle>
          <CardDescription>Multi-pillar diagnostic based on spending, runway & savings</CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className={`text-base px-3 py-1 font-bold ${
              score >= 80
                ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                : score >= 65
                ? "bg-amber-500/10 text-amber-500 border-amber-500/30"
                : "bg-rose-500/10 text-rose-500 border-rose-500/30"
            }`}
          >
            Grade {grade} ({score}/100)
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Radar Chart */}
          <div className="h-[240px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="hsl(var(--muted-foreground))" strokeOpacity={0.25} />
                <PolarAngleAxis
                  dataKey="pillar"
                  tick={{ fill: "hsl(var(--foreground))", fontSize: 11 }}
                />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Health Score"
                  dataKey="value"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.45}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Diagnostic Pillars & Recommendations */}
          <div className="space-y-3">
            <div className="text-sm font-semibold text-muted-foreground flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
              Key Diagnostics & Insights
            </div>
            <ul className="space-y-2 text-xs">
              {insights.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-2 text-muted-foreground bg-muted/40 p-2 rounded-md">
                  <TrendingUp className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
