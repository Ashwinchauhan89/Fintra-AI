"use client";

import React, { useState, useMemo } from "react";
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TrendingUp, PieChart as PieIcon, Sparkles, ArrowUpRight } from "lucide-react";

const RISK_PROFILES = {
  conservative: {
    label: "Conservative",
    expectedReturn: 0.08, // 8%
    allocation: [
      { name: "Debt / Fixed Income", value: 50, color: "#3b82f6" },
      { name: "Large Cap Equities", value: 30, color: "#10b981" },
      { name: "Gold & Commodities", value: 10, color: "#f59e0b" },
      { name: "Liquid Cash Buffer", value: 10, color: "#8b5cf6" },
    ],
  },
  balanced: {
    label: "Balanced",
    expectedReturn: 0.11, // 11%
    allocation: [
      { name: "Large Cap Equities", value: 45, color: "#10b981" },
      { name: "Mid/Small Cap", value: 15, color: "#06b6d4" },
      { name: "Debt / Bonds", value: 25, color: "#3b82f6" },
      { name: "Gold & Commodities", value: 10, color: "#f59e0b" },
      { name: "Liquid Cash", value: 5, color: "#8b5cf6" },
    ],
  },
  aggressive: {
    label: "Aggressive Growth",
    expectedReturn: 0.14, // 14%
    allocation: [
      { name: "Diversified Equities", value: 55, color: "#10b981" },
      { name: "Mid & Emerging Cap", value: 25, color: "#06b6d4" },
      { name: "Debt / Safe Assets", value: 10, color: "#3b82f6" },
      { name: "Gold & Commodities", value: 5, color: "#f59e0b" },
      { name: "High Growth / REITs", value: 5, color: "#ec4899" },
    ],
  },
};

export function PortfolioSimulator() {
  const [monthlySip, setMonthlySip] = useState(500);
  const [years, setYears] = useState(10);
  const [strategy, setStrategy] = useState("balanced");

  const currentProfile = RISK_PROFILES[strategy];

  // Calculate compound interest and timeline
  const { totalInvested, futureValue, estimatedWealthGain, projectionTimeline } = useMemo(() => {
    const r = currentProfile.expectedReturn;
    const n = 12; // monthly compounding
    const months = years * 12;
    const monthlyRate = r / n;

    // SIP formula: P * [((1 + i)^n - 1) / i] * (1 + i)
    const fv = monthlySip * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate);
    const invested = monthlySip * months;
    const gain = Math.max(0, fv - invested);

    // Build timeline points for chart
    const timeline = [];
    for (let yr = 1; yr <= years; yr++) {
      const curMonths = yr * 12;
      const curInvested = monthlySip * curMonths;
      const curFv = monthlySip * ((Math.pow(1 + monthlyRate, curMonths) - 1) / monthlyRate) * (1 + monthlyRate);
      timeline.push({
        year: `Yr ${yr}`,
        invested: Math.round(curInvested),
        projectedWealth: Math.round(curFv),
      });
    }

    return {
      totalInvested: Math.round(invested),
      futureValue: Math.round(fv),
      estimatedWealthGain: Math.round(gain),
      projectionTimeline: timeline,
    };
  }, [monthlySip, years, strategy, currentProfile]);

  return (
    <Card className="hover:shadow-md transition-all border-border/80">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4">
        <div>
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-500" />
            Multi-Asset Portfolio & SIP Simulator
          </CardTitle>
          <CardDescription>
            Simulate monthly compounding wealth growth and asset distribution
          </CardDescription>
        </div>
        <div className="flex items-center gap-1.5 bg-muted/60 p-1 rounded-lg">
          {Object.entries(RISK_PROFILES).map(([key, profile]) => (
            <button
              key={key}
              onClick={() => setStrategy(key)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                strategy === key
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {profile.label}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Sliders Control Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-xl bg-muted/30 border">
          {/* Monthly SIP Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-muted-foreground">Monthly Investment</span>
              <span className="font-bold text-foreground font-mono text-base">
                ${monthlySip.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="50"
              max="5000"
              step="50"
              value={monthlySip}
              onChange={(e) => setMonthlySip(Number(e.target.value))}
              className="w-full accent-primary h-2 bg-muted rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>$50/mo</span>
              <span>$5,000/mo</span>
            </div>
          </div>

          {/* Horizon Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium text-muted-foreground">Investment Horizon</span>
              <span className="font-bold text-foreground font-mono text-base">
                {years} {years === 1 ? "Year" : "Years"}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="30"
              step="1"
              value={years}
              onChange={(e) => setYears(Number(e.target.value))}
              className="w-full accent-primary h-2 bg-muted rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>1 Year</span>
              <span>30 Years</span>
            </div>
          </div>
        </div>

        {/* Highlight Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-lg bg-muted/40 border flex flex-col justify-between">
            <span className="text-xs text-muted-foreground font-medium">Total Invested</span>
            <span className="text-xl font-bold font-mono text-foreground mt-1">
              ${totalInvested.toLocaleString()}
            </span>
            <span className="text-[11px] text-muted-foreground mt-0.5">
              ${monthlySip}/mo for {years}y
            </span>
          </div>

          <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex flex-col justify-between">
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium flex items-center justify-between">
              Est. Wealth Returns
              <ArrowUpRight className="h-3.5 w-3.5" />
            </span>
            <span className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1">
              +${estimatedWealthGain.toLocaleString()}
            </span>
            <span className="text-[11px] text-emerald-600/80 dark:text-emerald-400/80 mt-0.5">
              Compound growth effect
            </span>
          </div>

          <div className="p-3.5 rounded-lg bg-primary/10 border border-primary/20 flex flex-col justify-between">
            <span className="text-xs text-primary font-medium">Projected Future Wealth</span>
            <span className="text-xl font-bold font-mono text-primary mt-1">
              ${futureValue.toLocaleString()}
            </span>
            <span className="text-[11px] text-primary/80 mt-0.5">
              {totalInvested > 0 ? (futureValue / totalInvested).toFixed(1) : 1}x of principal
            </span>
          </div>
        </div>

        {/* Charts: Growth Curve + Asset Allocation Donut */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          {/* Compound Growth Area Chart */}
          <div className="lg:col-span-2 space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <TrendingUp className="h-4 w-4 text-emerald-500" />
                Wealth Accumulation Trajectory
              </span>
              <span className="text-[11px] font-normal">
                Exp. Return: {(currentProfile.expectedReturn * 100).toFixed(0)}% p.a.
              </span>
            </div>
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={projectionTimeline} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorFv" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="colorInvested" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                  <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    formatter={(val) => [`$${Number(val).toLocaleString()}`, ""]}
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      borderColor: "hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="projectedWealth"
                    name="Projected Wealth"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorFv)"
                  />
                  <Area
                    type="monotone"
                    dataKey="invested"
                    name="Invested Principal"
                    stroke="#6366f1"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorInvested)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Allocation Donut */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
              <PieIcon className="h-4 w-4 text-primary" />
              Optimal Asset Basket
            </div>
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={currentProfile.allocation}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {currentProfile.allocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val, name) => [`${val}%`, name]}
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      borderColor: "hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-1 text-xs">
              {currentProfile.allocation.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-[11px] text-muted-foreground">
                  <span className="flex items-center gap-1.5">
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="truncate max-w-[120px]">{item.name}</span>
                  </span>
                  <span className="font-semibold text-foreground font-mono">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
