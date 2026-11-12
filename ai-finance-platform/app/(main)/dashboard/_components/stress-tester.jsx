"use client";

import React, { useState, useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  AlertTriangle,
  TrendingDown,
  ShieldAlert,
  Flame,
  RefreshCcw,
  Sparkles,
  ArrowDownRight,
  ShieldCheck,
  Zap,
} from "lucide-react";

const PRESET_SCENARIOS = {
  mild: {
    label: "Mild Squeeze",
    incomeCut: 10,
    expenseSurge: 5,
    emergencyShock: 500,
    desc: "Minor inflation uptick and temporary income dip",
  },
  recession: {
    label: "Recession Crunch",
    incomeCut: 25,
    expenseSurge: 15,
    emergencyShock: 2500,
    desc: "Substantial salary trim with high cost of living surge",
  },
  crisis: {
    label: "Black Swan Crisis",
    incomeCut: 45,
    expenseSurge: 25,
    emergencyShock: 5000,
    desc: "Severe macroeconomic dislocation and surprise medical/repair bill",
  },
};

export function StressTester({ accounts = [], transactions = [] }) {
  // Baseline financial extraction with resilient fallbacks
  const baseline = useMemo(() => {
    const totalLiquid = accounts.reduce((acc, a) => acc + (Number(a.balance) || 0), 0);
    const totalIncome = transactions
      .filter((t) => t.type === "INCOME")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);
    const totalExpenses = transactions
      .filter((t) => t.type === "EXPENSE")
      .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

    const monthlyIncome = totalIncome > 0 ? totalIncome : 5200;
    const monthlyExpense = totalExpenses > 0 ? totalExpenses : 3100;
    const startingCapital = totalLiquid > 0 ? totalLiquid : 16500;

    return {
      startingCapital,
      monthlyIncome,
      monthlyExpense,
    };
  }, [accounts, transactions]);

  // Simulation Sliders State
  const [incomeCut, setIncomeCut] = useState(20); // %
  const [expenseSurge, setExpenseSurge] = useState(10); // %
  const [emergencyShock, setEmergencyShock] = useState(1500); // $
  const [activePreset, setActivePreset] = useState(null);

  const applyPreset = (key) => {
    const p = PRESET_SCENARIOS[key];
    if (!p) return;
    setIncomeCut(p.incomeCut);
    setExpenseSurge(p.expenseSurge);
    setEmergencyShock(p.emergencyShock);
    setActivePreset(key);
  };

  const handleReset = () => {
    setIncomeCut(0);
    setExpenseSurge(0);
    setEmergencyShock(0);
    setActivePreset(null);
  };

  // Compute Stress Test Outcomes
  const simulation = useMemo(() => {
    const postIncome = baseline.monthlyIncome * (1 - incomeCut / 100);
    const postExpense = baseline.monthlyExpense * (1 + expenseSurge / 100);
    const postCapital = Math.max(0, baseline.startingCapital - emergencyShock);

    const baselineNet = baseline.monthlyIncome - baseline.monthlyExpense;
    const stressedNet = postIncome - postExpense;

    // Baseline runway
    const baselineRunway = baseline.monthlyExpense > 0 
      ? (baseline.startingCapital / baseline.monthlyExpense).toFixed(1)
      : "12+";

    // Stressed runway
    let stressedRunway = "12+";
    let status = "RESILIENT";
    let statusColor = "text-emerald-500 border-emerald-500/30 bg-emerald-500/10";

    if (stressedNet < 0) {
      const monthlyBurn = Math.abs(stressedNet);
      const months = postCapital / monthlyBurn;
      stressedRunway = months.toFixed(1);

      if (months < 3) {
        status = "CRITICAL HAZARD";
        statusColor = "text-rose-500 border-rose-500/30 bg-rose-500/10";
      } else if (months < 6) {
        status = "MODERATE VULNERABILITY";
        statusColor = "text-amber-500 border-amber-500/30 bg-amber-500/10";
      } else {
        status = "DEGRADED CUSHION";
        statusColor = "text-yellow-500 border-yellow-500/30 bg-yellow-500/10";
      }
    } else {
      status = "RESILIENT";
      statusColor = "text-emerald-500 border-emerald-500/30 bg-emerald-500/10";
    }

    // 12-Month Liquidity Curve
    const timeline = [];
    let curBase = baseline.startingCapital;
    let curStressed = postCapital;

    for (let m = 0; m <= 12; m++) {
      timeline.push({
        month: m === 0 ? "Now" : `M${m}`,
        Baseline: Math.round(curBase),
        Stressed: Math.max(0, Math.round(curStressed)),
      });
      curBase += baselineNet;
      curStressed += stressedNet;
    }

    const deficitPerMonth = stressedNet < 0 ? Math.abs(stressedNet) : 0;

    return {
      postIncome,
      postExpense,
      postCapital,
      baselineNet,
      stressedNet,
      baselineRunway,
      stressedRunway,
      status,
      statusColor,
      timeline,
      deficitPerMonth,
    };
  }, [baseline, incomeCut, expenseSurge, emergencyShock]);

  return (
    <Card className="border-border/60 shadow-sm overflow-hidden">
      <CardHeader className="flex flex-col md:flex-row md:items-center justify-between pb-4 gap-4 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-500 border border-rose-500/20">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <CardTitle className="text-xl font-bold tracking-tight">
              Recession & Financial Stress Lab
            </CardTitle>
          </div>
          <CardDescription className="text-xs text-muted-foreground mt-1">
            Simulate income dislocations, inflation surges, and surprise capital shocks over a 12-month horizon
          </CardDescription>
        </div>

        {/* Preset Triggers */}
        <div className="flex flex-wrap items-center gap-2">
          {Object.entries(PRESET_SCENARIOS).map(([key, p]) => (
            <Button
              key={key}
              size="sm"
              variant={activePreset === key ? "default" : "outline"}
              className={`text-xs h-7 px-2.5 ${
                activePreset === key ? "bg-rose-600 hover:bg-rose-700 text-white" : ""
              }`}
              onClick={() => applyPreset(key)}
            >
              <Zap className="h-3 w-3 mr-1" />
              {p.label}
            </Button>
          ))}
          <Button
            size="sm"
            variant="ghost"
            className="text-xs h-7 px-2 text-muted-foreground hover:text-foreground"
            onClick={handleReset}
          >
            <RefreshCcw className="h-3 w-3 mr-1" />
            Reset
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-6">
        {/* Sliders Input Control Board */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 p-4 rounded-xl bg-muted/30 border border-border/50">
          {/* Income Disruption */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
                <TrendingDown className="h-3.5 w-3.5 text-rose-500" /> Income Disruption
              </span>
              <span className="font-mono font-bold text-foreground">
                -{incomeCut}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              step="5"
              value={incomeCut}
              onChange={(e) => {
                setIncomeCut(Number(e.target.value));
                setActivePreset(null);
              }}
              className="w-full accent-rose-500 h-2 bg-muted rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-muted-foreground font-mono">
              <span>0% (Steady)</span>
              <span>-50% (Halved)</span>
            </div>
          </div>

          {/* Inflation Surge */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
                <Flame className="h-3.5 w-3.5 text-amber-500" /> Expense / Inflation Surge
              </span>
              <span className="font-mono font-bold text-foreground">
                +{expenseSurge}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              step="5"
              value={expenseSurge}
              onChange={(e) => {
                setExpenseSurge(Number(e.target.value));
                setActivePreset(null);
              }}
              className="w-full accent-amber-500 h-2 bg-muted rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-muted-foreground font-mono">
              <span>0% (Constant)</span>
              <span>+40% (Surge)</span>
            </div>
          </div>

          {/* Sudden Emergency Shock */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
                <AlertTriangle className="h-3.5 w-3.5 text-yellow-500" /> Surprise Capital Outflow
              </span>
              <span className="font-mono font-bold text-foreground">
                ${emergencyShock.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="10000"
              step="250"
              value={emergencyShock}
              onChange={(e) => {
                setEmergencyShock(Number(e.target.value));
                setActivePreset(null);
              }}
              className="w-full accent-yellow-500 h-2 bg-muted rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-muted-foreground font-mono">
              <span>$0</span>
              <span>$10,000</span>
            </div>
          </div>
        </div>

        {/* Dynamic Metric Tiles */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="p-3.5 rounded-xl border bg-card/60 flex flex-col justify-between">
            <span className="text-[11px] font-semibold text-muted-foreground">
              Survival Runway
            </span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-black font-mono text-foreground">
                {simulation.stressedRunway}
              </span>
              <span className="text-xs text-muted-foreground">months</span>
            </div>
            <div className="text-[10px] text-muted-foreground mt-1">
              Baseline: <span className="font-mono font-semibold">{simulation.baselineRunway} mo</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl border bg-card/60 flex flex-col justify-between">
            <span className="text-[11px] font-semibold text-muted-foreground">
              Stressed Cash Flow
            </span>
            <div className="mt-1 flex items-baseline gap-2">
              <span
                className={`text-2xl font-black font-mono ${
                  simulation.stressedNet >= 0 ? "text-emerald-500" : "text-rose-500"
                }`}
              >
                {simulation.stressedNet >= 0 ? "+" : "-"}$
                {Math.abs(Math.round(simulation.stressedNet)).toLocaleString()}
              </span>
              <span className="text-xs text-muted-foreground">/mo</span>
            </div>
            <div className="text-[10px] text-muted-foreground mt-1">
              Baseline: <span className="font-mono font-semibold">{simulation.baselineNet >= 0 ? "+" : ""}${Math.round(simulation.baselineNet)}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl border bg-card/60 flex flex-col justify-between">
            <span className="text-[11px] font-semibold text-muted-foreground">
              Initial Capital Buffer
            </span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-black font-mono text-foreground">
                ${Math.round(simulation.postCapital).toLocaleString()}
              </span>
            </div>
            <div className="text-[10px] text-muted-foreground mt-1">
              Shock absorption: <span className="font-mono font-semibold">-${emergencyShock.toLocaleString()}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl border bg-card/60 flex flex-col justify-between">
            <span className="text-[11px] font-semibold text-muted-foreground">
              Macro Stress Rating
            </span>
            <div className="mt-1">
              <Badge variant="outline" className={`font-mono text-xs font-bold ${simulation.statusColor}`}>
                {simulation.status}
              </Badge>
            </div>
            <div className="text-[10px] text-muted-foreground mt-1">
              {simulation.deficitPerMonth > 0
                ? `Burn rate: $${Math.round(simulation.deficitPerMonth)}/mo`
                : "Solvent & cash-flow positive"}
            </div>
          </div>
        </div>

        {/* 12-Month Liquidity Stress Curve Chart */}
        <div className="p-4 rounded-xl border bg-card/40">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <h4 className="text-sm font-bold text-foreground">
                12-Month Liquidity Depletion Curve
              </h4>
              <p className="text-xs text-muted-foreground">
                Baseline trajectory vs Stress scenario balance exhaustion
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#88CE02]" />
                <span className="text-muted-foreground">Baseline Trajectory</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-rose-500" />
                <span className="text-muted-foreground">Simulated Shock</span>
              </div>
            </div>
          </div>

          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={simulation.timeline} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#88CE02" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#88CE02" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="stressedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" stroke="#888888" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#888888"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(10, 10, 10, 0.95)",
                    border: "1px solid rgba(255, 255, 255, 0.15)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  formatter={(val, name) => [`$${Number(val).toLocaleString()}`, name]}
                />
                <Area
                  type="monotone"
                  dataKey="Baseline"
                  stroke="#88CE02"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#baselineGrad)"
                />
                <Area
                  type="monotone"
                  dataKey="Stressed"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  fillOpacity={1}
                  fill="url(#stressedGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Actionable Resilience Prescription */}
        <div className="p-4 rounded-xl border border-[#88CE02]/30 bg-[#88CE02]/5 flex items-start gap-3">
          <div className="p-2 rounded-lg bg-[#88CE02]/20 text-[#88CE02] shrink-0 mt-0.5">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="text-xs space-y-1">
            <p className="font-semibold text-foreground">
              Autonomous Financial Prescription
            </p>
            {simulation.deficitPerMonth > 0 ? (
              <p className="text-muted-foreground leading-relaxed">
                To bridge the <span className="text-rose-400 font-mono font-bold">${Math.round(simulation.deficitPerMonth)}/month</span> cash-flow deficit and extend your runway back past 6 months, consider immediately throttling non-essential discretionary categories (dining, subscriptions) by <span className="text-[#88CE02] font-mono font-bold">${Math.round(simulation.deficitPerMonth * 0.7)}</span> and maintaining an emergency reserve target of <span className="text-[#88CE02] font-mono font-bold">${Math.round(simulation.postExpense * 3).toLocaleString()}</span>.
              </p>
            ) : (
              <p className="text-muted-foreground leading-relaxed">
                Your current liquidity reserves and low debt profile safely absorb this simulated disruption. Even with a {incomeCut}% income loss and {expenseSurge}% inflation hike, you remain net cash-flow positive at <span className="text-emerald-400 font-mono font-bold">+${Math.round(simulation.stressedNet)}/month</span>.
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
