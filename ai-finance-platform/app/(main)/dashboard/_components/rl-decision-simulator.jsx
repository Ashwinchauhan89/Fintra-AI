"use client";

import React, { useState, useEffect, useTransition } from "react";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Cpu,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  DollarSign,
  ArrowRight,
  Layers,
  Activity,
  Flame,
} from "lucide-react";
import { simulateRLDecision } from "@/lib/ml-client";

const PRESET_ARCHETYPES = [
  {
    id: "debt_focus",
    name: "Debt Elimination",
    badge: "High Debt Burden",
    income: 60000,
    expenses: 38000,
    savings: 40000,
    debt: 120000,
    investment: 15000,
    emergencyFund: 20000,
    riskTolerance: 0.4,
    financialGoal: 500000,
  },
  {
    id: "balanced",
    name: "Balanced Builder",
    badge: "Moderate Buffer",
    income: 75000,
    expenses: 42000,
    savings: 120000,
    debt: 35000,
    investment: 60000,
    emergencyFund: 50000,
    riskTolerance: 0.6,
    financialGoal: 800000,
  },
  {
    id: "aggressive_growth",
    name: "Wealth Accelerator",
    badge: "Zero Debt & Compounding",
    income: 95000,
    expenses: 45000,
    savings: 200000,
    debt: 0,
    investment: 150000,
    emergencyFund: 80000,
    riskTolerance: 0.8,
    financialGoal: 1200000,
  },
  {
    id: "issue_54_case",
    name: "Issue #54 Benchmark",
    badge: "Official Spec Case",
    income: 60000,
    expenses: 35000,
    savings: 150000,
    debt: 50000,
    investment: 100000,
    emergencyFund: 50000,
    riskTolerance: 0.6,
    financialGoal: 500000,
  },
];

export function RLDecisionSimulator() {
  const [selectedPreset, setSelectedPreset] = useState("issue_54_case");
  const [income, setIncome] = useState(60000);
  const [expenses, setExpenses] = useState(35000);
  const [savings, setSavings] = useState(150000);
  const [debt, setDebt] = useState(50000);
  const [investment, setInvestment] = useState(100000);
  const [emergencyFund, setEmergencyFund] = useState(50000);
  const [riskTolerance, setRiskTolerance] = useState(0.6);
  const [financialGoal, setFinancialGoal] = useState(500000);
  const [months, setMonths] = useState(24);

  const [simulationResult, setSimulationResult] = useState(null);
  const [isPending, startTransition] = useTransition();

  const handleApplyPreset = (preset) => {
    setSelectedPreset(preset.id);
    setIncome(preset.income);
    setExpenses(preset.expenses);
    setSavings(preset.savings);
    setDebt(preset.debt);
    setInvestment(preset.investment);
    setEmergencyFund(preset.emergencyFund);
    setRiskTolerance(preset.riskTolerance);
    setFinancialGoal(preset.financialGoal);
  };

  const runSimulation = () => {
    startTransition(async () => {
      const res = await simulateRLDecision({
        income,
        expenses,
        savings,
        debt,
        investment,
        emergencyFund,
        riskTolerance,
        financialGoal,
        simulationPeriodMonths: months,
      });
      if (res) {
        setSimulationResult(res);
      }
    });
  };

  // Run initial simulation on mount or when key parameters change
  useEffect(() => {
    runSimulation();
  }, [months]);

  const trajectory = simulationResult?.monthly_trajectory || [];
  const risk = simulationResult?.risk_indicators || {};
  const breakdown = simulationResult?.action_breakdown || {};

  return (
    <Card className="border-border/80 shadow-sm hover:shadow-md transition-all overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-violet-500/10 via-background to-emerald-500/10 pb-5 border-b">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary gap-1 px-2.5 py-0.5">
                <Cpu className="h-3.5 w-3.5 animate-pulse text-violet-500" />
                Reinforcement Learning Engine
              </Badge>
              <Badge variant="secondary" className="text-[11px] font-mono">
                PyTorch + Gymnasium Policy
              </Badge>
              <Badge variant="outline" className="text-[11px] border-emerald-500/30 text-emerald-600 dark:text-emerald-400">
                Non-Custodial Simulator
              </Badge>
            </div>
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-amber-500" />
              Autonomous Financial Strategy Simulator
            </CardTitle>
            <CardDescription className="text-sm">
              Simulate dynamic forward cash flow decisions, debt elimination milestones, and multi-year wealth accumulation.
            </CardDescription>
          </div>

          {/* Horizon Selection */}
          <div className="flex items-center gap-2 bg-muted/60 p-1.5 rounded-lg self-start md:self-center">
            <span className="text-xs font-medium text-muted-foreground px-1">Horizon:</span>
            {[12, 24, 36].map((m) => (
              <button
                key={m}
                onClick={() => setMonths(m)}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                  months === m
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {m} Mo
              </button>
            ))}
          </div>
        </div>

        {/* Quick Presets */}
        <div className="pt-3 flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1">
            <Layers className="h-3 w-3" /> Archetypes:
          </span>
          {PRESET_ARCHETYPES.map((preset) => (
            <button
              key={preset.id}
              onClick={() => handleApplyPreset(preset)}
              className={`px-2.5 py-1 text-xs rounded-full border transition-all ${
                selectedPreset === preset.id
                  ? "bg-foreground text-background border-foreground font-semibold shadow-sm"
                  : "bg-background/80 text-muted-foreground border-border hover:border-foreground/40"
              }`}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Controls Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-muted/30 border">
          {/* Income */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Monthly Income</span>
              <span className="font-bold font-mono text-foreground">${income.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="20000"
              max="250000"
              step="5000"
              value={income}
              onChange={(e) => {
                setIncome(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-primary h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Expenses */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Monthly Expenses</span>
              <span className="font-bold font-mono text-foreground">${expenses.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="10000"
              max="150000"
              step="2500"
              value={expenses}
              onChange={(e) => {
                setExpenses(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-primary h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Liquid Savings */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Liquid Savings</span>
              <span className="font-bold font-mono text-foreground">${savings.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="0"
              max="500000"
              step="10000"
              value={savings}
              onChange={(e) => {
                setSavings(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-primary h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Outstanding Debt */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Outstanding Debt</span>
              <span className={`font-bold font-mono ${debt > 0 ? "text-rose-500" : "text-emerald-500"}`}>
                ${debt.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="300000"
              step="5000"
              value={debt}
              onChange={(e) => {
                setDebt(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-rose-500 h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Investments */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Investments</span>
              <span className="font-bold font-mono text-foreground">${investment.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="0"
              max="500000"
              step="10000"
              value={investment}
              onChange={(e) => {
                setInvestment(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-primary h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Emergency Fund */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Emergency Reserve</span>
              <span className="font-bold font-mono text-foreground">${emergencyFund.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="0"
              max="200000"
              step="5000"
              value={emergencyFund}
              onChange={(e) => {
                setEmergencyFund(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-emerald-500 h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Risk Tolerance */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Risk Profile</span>
              <span className="font-bold font-mono text-foreground">
                {riskTolerance <= 0.35 ? "Conservative" : riskTolerance <= 0.65 ? "Balanced" : "Aggressive"} ({(riskTolerance * 100).toFixed(0)}%)
              </span>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={riskTolerance}
              onChange={(e) => {
                setRiskTolerance(Number(e.target.value));
                setSelectedPreset(null);
              }}
              className="w-full accent-violet-500 h-1.5 bg-muted rounded cursor-pointer"
            />
          </div>

          {/* Action Trigger */}
          <div className="flex items-end">
            <Button
              onClick={runSimulation}
              disabled={isPending}
              className="w-full h-9 text-xs font-semibold gap-1.5 bg-primary hover:bg-primary/90"
            >
              {isPending ? (
                <>
                  <Activity className="h-3.5 w-3.5 animate-spin" />
                  Simulating Policy...
                </>
              ) : (
                <>
                  <TrendingUp className="h-3.5 w-3.5" />
                  Run RL Simulation
                </>
              )}
            </Button>
          </div>
        </div>

        {/* AI Policy Recommendation Card */}
        {simulationResult && (
          <div className="p-4 rounded-xl bg-gradient-to-r from-violet-500/15 via-primary/10 to-emerald-500/15 border border-primary/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/20 text-primary shrink-0 mt-0.5">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  RL Optimal Policy Strategy ({months} Months Horizon)
                </span>
                <p className="text-sm font-medium text-foreground leading-relaxed">
                  "{simulationResult.recommended_strategy}"
                </p>
              </div>
            </div>
            {risk.debt_free_month && (
              <Badge className="bg-emerald-500 text-white hover:bg-emerald-600 shrink-0 gap-1 px-3 py-1 font-semibold">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Debt Free by Month {risk.debt_free_month}
              </Badge>
            )}
          </div>
        )}

        {/* Key Metrics KPI Cards */}
        {simulationResult && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {/* Projected Savings */}
            <div className="p-4 rounded-xl bg-muted/40 border space-y-1">
              <span className="text-xs text-muted-foreground font-medium">Projected Liquid Savings</span>
              <div className="text-2xl font-bold font-mono text-foreground">
                ${simulationResult.projected_savings.toLocaleString()}
              </div>
              <div className="text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                +${Math.max(0, simulationResult.projected_savings - savings).toLocaleString()} accumulated
              </div>
            </div>

            {/* Projected Debt */}
            <div className="p-4 rounded-xl bg-muted/40 border space-y-1">
              <span className="text-xs text-muted-foreground font-medium">Remaining Debt</span>
              <div className={`text-2xl font-bold font-mono ${simulationResult.projected_debt === 0 ? "text-emerald-500" : "text-rose-500"}`}>
                ${simulationResult.projected_debt.toLocaleString()}
              </div>
              <div className="text-[11px] text-muted-foreground">
                {simulationResult.projected_debt === 0 ? (
                  <span className="text-emerald-500 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> 100% Debt Eradicated
                  </span>
                ) : (
                  <span>Amortized from ${debt.toLocaleString()}</span>
                )}
              </div>
            </div>

            {/* Projected Net Worth */}
            <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 space-y-1">
              <span className="text-xs text-primary font-medium">Projected Net Worth</span>
              <div className="text-2xl font-bold font-mono text-primary">
                ${simulationResult.projected_net_worth?.toLocaleString() || "—"}
              </div>
              <div className="text-[11px] text-primary/80">
                Includes investments & liquid reserves
              </div>
            </div>

            {/* Goal Progress */}
            <div className="p-4 rounded-xl bg-muted/40 border space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground font-medium">Goal Progress (${(financialGoal / 1000).toFixed(0)}k)</span>
                <span className="font-bold font-mono text-foreground">
                  {(simulationResult.goal_progress * 100).toFixed(0)}%
                </span>
              </div>
              <Progress value={simulationResult.goal_progress * 100} className="h-2" />
              <div className="text-[11px] text-muted-foreground">
                {simulationResult.goal_progress >= 1.0 ? "Target fully achieved!" : "On-track toward milestone"}
              </div>
            </div>
          </div>
        )}

        {/* Trajectory Area & Multi-line Chart */}
        {trajectory.length > 0 && (
          <div className="space-y-2 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-semibold text-muted-foreground pb-1">
              <span className="flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-primary" />
                Multi-Month Asset & Liability Trajectory
              </span>
              <span className="text-[11px] font-normal">
                Double-DQN Policy Rollout across {months} monthly decision steps
              </span>
            </div>

            <div className="h-[280px] w-full bg-card rounded-xl p-2 border">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trajectory} margin={{ top: 10, right: 15, left: 10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorNetWorth" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} tickFormatter={(m) => `M${m}`} />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload || !payload.length) return null;
                      const pt = payload[0].payload;
                      return (
                        <div className="bg-popover border border-border rounded-lg p-3 text-xs shadow-md space-y-1 font-sans">
                          <div className="font-bold text-foreground border-b pb-1 flex justify-between gap-4">
                            <span>Month {pt.month}</span>
                            <Badge variant="outline" className="text-[10px] py-0">
                              {pt.action_name}
                            </Badge>
                          </div>
                          <div className="text-emerald-500 font-mono">Net Worth: ${pt.net_worth.toLocaleString()}</div>
                          <div className="text-cyan-500 font-mono">Savings: ${pt.savings.toLocaleString()}</div>
                          <div className="text-violet-500 font-mono">Investments: ${pt.investment.toLocaleString()}</div>
                          <div className="text-rose-500 font-mono">Debt: ${pt.debt.toLocaleString()}</div>
                          <div className="text-muted-foreground text-[10px]">Health: {pt.health_score}/100</div>
                        </div>
                      );
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                  <Area
                    type="monotone"
                    dataKey="net_worth"
                    name="Net Worth"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorNetWorth)"
                  />
                  <Line
                    type="monotone"
                    dataKey="savings"
                    name="Liquid Savings"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="investment"
                    name="Investments"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="debt"
                    name="Remaining Debt"
                    stroke="#f43f5e"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Action Strategy Breakdown & Risk Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* Action Allocation Pills */}
          <div className="p-4 rounded-xl bg-muted/20 border space-y-3">
            <span className="text-xs font-bold text-muted-foreground flex items-center gap-1.5">
              <Cpu className="h-4 w-4 text-violet-500" />
              RL Policy Decision Distribution ({months} Months)
            </span>
            <div className="flex flex-wrap gap-2">
              {Object.entries(breakdown).map(([actionName, count]) => (
                <div
                  key={actionName}
                  className="px-3 py-1.5 rounded-lg bg-background border text-xs flex items-center gap-2 shadow-2xs"
                >
                  <span className="font-medium text-foreground">{actionName}</span>
                  <Badge variant="secondary" className="font-mono text-[11px] h-5 px-1.5">
                    {count} mo ({Math.round((count / months) * 100)}%)
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Diagnostics */}
          <div className="p-4 rounded-xl bg-muted/20 border space-y-3">
            <span className="text-xs font-bold text-muted-foreground flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
              Financial Health Diagnostics
            </span>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-background border text-center space-y-0.5">
                <span className="text-[10px] text-muted-foreground block">Emergency Buffer</span>
                <span className="font-bold font-mono text-foreground">
                  {risk.initial_emergency_runway_months || 0}m <ArrowRight className="inline h-2.5 w-2.5 text-muted-foreground" /> {risk.final_emergency_runway_months || 0}m
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-background border text-center space-y-0.5">
                <span className="text-[10px] text-muted-foreground block">Debt-to-Income</span>
                <span className="font-bold font-mono text-foreground">
                  {((risk.initial_debt_to_income_ratio || 0) * 100).toFixed(0)}% <ArrowRight className="inline h-2.5 w-2.5 text-muted-foreground" /> {((risk.final_debt_to_income_ratio || 0) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-background border text-center space-y-0.5">
                <span className="text-[10px] text-muted-foreground block">Health Score</span>
                <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  {risk.initial_health_score || 0} <ArrowRight className="inline h-2.5 w-2.5 text-muted-foreground" /> {risk.final_health_score || 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
