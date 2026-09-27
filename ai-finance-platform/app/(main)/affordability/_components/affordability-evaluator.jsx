"use client";

import React, { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  HelpCircle,
  ShieldCheck,
  AlertTriangle,
  Clock,
  ArrowRight,
  TrendingDown,
  DollarSign,
  Laptop,
  Plane,
  Smartphone,
  Wrench,
  CheckCircle2,
  XCircle,
  CreditCard,
  Zap,
} from "lucide-react";
import { evaluatePurchaseAffordability } from "@/actions/affordability";
import { toast } from "sonner";

const PRESET_EXPENSES = [
  {
    name: "MacBook Pro M3 Max",
    amount: "2499",
    urgency: "DISCRETIONARY",
    tenure: "0",
    icon: Laptop,
    badge: "Tech Upgrade",
  },
  {
    name: "Tokyo Vacation Flights",
    amount: "850",
    urgency: "DISCRETIONARY",
    tenure: "0",
    icon: Plane,
    badge: "Travel",
  },
  {
    name: "Flagship Smartphone",
    amount: "1199",
    urgency: "DISCRETIONARY",
    tenure: "6",
    icon: Smartphone,
    badge: "6-Mo Financing",
  },
  {
    name: "Car Transmission Repair",
    amount: "1450",
    urgency: "ESSENTIAL",
    tenure: "0",
    icon: Wrench,
    badge: "Essential",
  },
];

export function AffordabilityEvaluator({ initialResult }) {
  const [itemName, setItemName] = useState("MacBook Pro M3");
  const [amount, setAmount] = useState("1999");
  const [urgency, setUrgency] = useState("DISCRETIONARY");
  const [installmentMonths, setInstallmentMonths] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(initialResult?.data || null);

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    const numericAmount = Number(amount);
    if (!itemName.trim() || numericAmount <= 0) {
      toast.error("Please enter a valid item name and purchase amount.");
      return;
    }

    setLoading(true);
    try {
      const res = await evaluatePurchaseAffordability({
        itemName,
        amount: numericAmount,
        urgency,
        installmentMonths,
        installmentInterestRatePct: installmentMonths > 0 ? 0 : 0,
      });

      if (res.success) {
        setResult(res.data);
        toast.success(`Evaluated affordability for "${itemName}"!`);
      } else {
        toast.error(res.error || "Failed to evaluate affordability.");
      }
    } catch {
      toast.error("An error occurred during evaluation.");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPreset = (preset) => {
    setItemName(preset.name);
    setAmount(preset.amount);
    setUrgency(preset.urgency);
    setInstallmentMonths(Number(preset.tenure));
  };

  // Status-based color mapping
  const getDecisionBadge = (rec) => {
    switch (rec) {
      case "PAY_IN_FULL":
        return {
          label: "PAY IN FULL",
          color: "bg-emerald-500/10 text-emerald-500 border-emerald-500/30",
          icon: CheckCircle2,
        };
      case "INSTALLMENTS":
        return {
          label: "USE INSTALLMENTS (EMI)",
          color: "bg-cyan-500/10 text-cyan-500 border-cyan-500/30",
          icon: CreditCard,
        };
      case "PAY_PARTIALLY":
        return {
          label: "PAY PARTIALLY (STAGGER)",
          color: "bg-amber-500/10 text-amber-500 border-amber-500/30",
          icon: Clock,
        };
      case "WAIT":
        return {
          label: "WAIT & SAVE",
          color: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
          icon: Clock,
        };
      case "DO_NOT_PROCEED":
      default:
        return {
          label: "DO NOT PROCEED",
          color: "bg-rose-500/10 text-rose-500 border-rose-500/30",
          icon: XCircle,
        };
    }
  };

  const badgeInfo = getDecisionBadge(result?.recommendation);
  const BadgeIcon = badgeInfo.icon;

  return (
    <div className="space-y-6">
      {/* Top Presets Row */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-muted-foreground mr-1 flex items-center gap-1">
          <Zap className="h-3.5 w-3.5 text-[#88CE02]" /> Quick Scenarios:
        </span>
        {PRESET_EXPENSES.map((preset) => {
          const Icon = preset.icon;
          return (
            <Button
              key={preset.name}
              type="button"
              variant="outline"
              size="sm"
              onClick={() => handleApplyPreset(preset)}
              className="text-xs h-8 border-border/60 hover:border-primary/40 gap-1.5"
            >
              <Icon className="h-3.5 w-3.5 text-muted-foreground" />
              <span>{preset.name}</span>
              <span className="font-mono text-[11px] text-muted-foreground">
                (${Number(preset.amount).toLocaleString()})
              </span>
            </Button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Input Form Column */}
        <Card className="lg:col-span-5 border-border/60 shadow-sm">
          <CardHeader className="pb-4 border-b border-border/40">
            <CardTitle className="text-base sm:text-lg font-bold flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-primary" />
              Expense Details
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Define the item, price tag, and financing options to stress-test your cash flow
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-4">
            <form onSubmit={handleEvaluate} className="space-y-4">
              {/* Item Name */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  What do you want to buy?
                </label>
                <Input
                  type="text"
                  placeholder="e.g. MacBook Pro, Vacation, Ergonomic Chair..."
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  className="font-medium text-sm"
                  required
                />
              </div>

              {/* Amount */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  Estimated Cost ($)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    min="1"
                    step="1"
                    placeholder="1999"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="pl-9 font-mono font-bold text-base"
                    required
                  />
                </div>
              </div>

              {/* Priority & Urgency */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  Priority / Urgency Level
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setUrgency("DISCRETIONARY")}
                    className={`py-2 px-3 text-xs font-semibold rounded-lg border transition-all text-center ${
                      urgency === "DISCRETIONARY"
                        ? "bg-primary/10 border-primary text-primary shadow-sm"
                        : "border-border/60 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    Discretionary (Want)
                  </button>
                  <button
                    type="button"
                    onClick={() => setUrgency("ESSENTIAL")}
                    className={`py-2 px-3 text-xs font-semibold rounded-lg border transition-all text-center ${
                      urgency === "ESSENTIAL"
                        ? "bg-primary/10 border-primary text-primary shadow-sm"
                        : "border-border/60 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    Essential (Need)
                  </button>
                </div>
              </div>

              {/* Financing Tenures */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  Payment Mode / Financing
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { label: "Full Cash", value: 0 },
                    { label: "3 Mo EMI", value: 3 },
                    { label: "6 Mo EMI", value: 6 },
                    { label: "12 Mo EMI", value: 12 },
                  ].map((t) => (
                    <button
                      key={t.value}
                      type="button"
                      onClick={() => setInstallmentMonths(t.value)}
                      className={`py-1.5 px-2 text-[11px] font-semibold rounded-lg border transition-all text-center ${
                        installmentMonths === t.value
                          ? "bg-primary text-primary-foreground border-primary"
                          : "border-border/60 text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-[#88CE02] text-black hover:bg-lime-400 font-extrabold shadow-[0_0_20px_rgba(136,206,2,0.3)] mt-2"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 animate-spin" /> Evaluating Cash Flow...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4" /> Run Affordability Test
                  </span>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results Column */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <>
              {/* Decision Hero Card */}
              <Card className="border-border/70 shadow-md overflow-hidden relative">
                <div className="p-5 sm:p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/40 pb-4">
                    <div>
                      <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                        AI Financial Agent Recommendation
                      </span>
                      <h3 className="text-xl sm:text-2xl font-black tracking-tight text-foreground mt-0.5">
                        {result.recommendation_title}
                      </h3>
                    </div>
                    <Badge
                      variant="outline"
                      className={`text-xs px-3 py-1 font-mono font-bold flex items-center gap-1.5 shrink-0 ${badgeInfo.color}`}
                    >
                      <BadgeIcon className="h-3.5 w-3.5" />
                      {badgeInfo.label}
                    </Badge>
                  </div>

                  {/* Action Verdict Callout */}
                  <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                    {result.action_verdict}
                  </p>

                  {/* 4 Metric Badges */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                    <div className="p-3 rounded-xl border bg-muted/20">
                      <span className="text-[10px] text-muted-foreground font-semibold block">
                        Safe Spend Limit
                      </span>
                      <span className="text-base sm:text-lg font-bold font-mono text-foreground mt-0.5 block">
                        ${result.amount_safe_to_spend?.toLocaleString()}
                      </span>
                    </div>

                    <div className="p-3 rounded-xl border bg-muted/20">
                      <span className="text-[10px] text-muted-foreground font-semibold block">
                        Risk Level
                      </span>
                      <span
                        className={`text-base sm:text-lg font-bold font-mono mt-0.5 block ${
                          result.risk_level === "LOW"
                            ? "text-emerald-500"
                            : result.risk_level === "MEDIUM"
                            ? "text-amber-500"
                            : "text-rose-500"
                        }`}
                      >
                        {result.risk_level}
                      </span>
                    </div>

                    <div className="p-3 rounded-xl border bg-muted/20">
                      <span className="text-[10px] text-muted-foreground font-semibold block">
                        Runway Impact
                      </span>
                      <span className="text-base sm:text-lg font-bold font-mono text-foreground mt-0.5 block">
                        {result.runway_before_months}m → {result.runway_after_months}m
                      </span>
                    </div>

                    <div className="p-3 rounded-xl border bg-muted/20">
                      <span className="text-[10px] text-muted-foreground font-semibold block">
                        AI Confidence
                      </span>
                      <span className="text-base sm:text-lg font-bold font-mono text-[#88CE02] mt-0.5 block">
                        {Math.round((result.confidence_score || 0.9) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* 30-Day Day-by-Day Cash Flow Projection Chart */}
              {result.cashflow_projection_30d?.length > 0 && (
                <Card className="border-border/60 shadow-sm">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-sm font-bold">
                          30-Day Liquidity Trajectory
                        </CardTitle>
                        <CardDescription className="text-xs text-muted-foreground">
                          Projected balance untouched vs post-purchase trajectory
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-3 text-xs">
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <span className="w-2.5 h-2.5 rounded-full bg-[#88CE02]" /> Baseline
                        </span>
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> With Expense
                        </span>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-2">
                    <div className="h-[200px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={result.cashflow_projection_30d}
                          margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                        >
                          <defs>
                            <linearGradient id="affordBaseGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#88CE02" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#88CE02" stopOpacity={0.0} />
                            </linearGradient>
                            <linearGradient id="affordPostGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                          <XAxis dataKey="day" stroke="#888888" fontSize={11} tickLine={false} />
                          <YAxis
                            stroke="#888888"
                            fontSize={11}
                            tickLine={false}
                            tickFormatter={(v) => `$${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "rgba(10, 10, 10, 0.95)",
                              border: "1px solid rgba(255, 255, 255, 0.15)",
                              borderRadius: "8px",
                              fontSize: "12px",
                            }}
                            formatter={(val, name) => [
                              `$${Number(val).toLocaleString()}`,
                              name === "baseline_balance" ? "Baseline" : "With Purchase",
                            ]}
                          />
                          <Area
                            type="monotone"
                            dataKey="baseline_balance"
                            stroke="#88CE02"
                            strokeWidth={2}
                            fill="url(#affordBaseGrad)"
                          />
                          <Area
                            type="monotone"
                            dataKey="with_purchase_balance"
                            stroke="#f43f5e"
                            strokeWidth={2}
                            strokeDasharray="4 4"
                            fill="url(#affordPostGrad)"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Trade-Offs & Alternative Strategies */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Trade-Offs */}
                <Card className="border-border/60 shadow-sm p-4 space-y-2">
                  <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                    <TrendingDown className="h-4 w-4 text-amber-500" /> Trade-Off Impact
                  </span>
                  <ul className="text-xs text-muted-foreground space-y-1.5 list-disc pl-4 leading-relaxed">
                    {result.tradeoffs?.map((t, idx) => (
                      <li key={idx}>{t}</li>
                    ))}
                  </ul>
                </Card>

                {/* Alternative Pathways */}
                <Card className="border-border/60 shadow-sm p-4 space-y-2">
                  <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4 text-primary" /> Recommended Strategy
                  </span>
                  {result.alternative_options?.length > 0 ? (
                    <div className="space-y-2 text-xs">
                      {result.alternative_options.map((alt, idx) => (
                        <div key={idx} className="p-2 rounded-lg bg-muted/40 border border-border/40">
                          <span className="font-semibold text-foreground block">{alt.label}</span>
                          <span className="text-[11px] text-muted-foreground">{alt.impact}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      No financing workarounds needed. Your current capital supports this purchase in full without breaching emergency safety buffers.
                    </p>
                  )}
                </Card>
              </div>
            </>
          ) : (
            <Card className="p-8 text-center border-dashed border-border/70 flex flex-col items-center justify-center space-y-3">
              <div className="p-3 rounded-2xl bg-muted/50 text-muted-foreground">
                <HelpCircle className="h-8 w-8" />
              </div>
              <h4 className="font-bold text-sm text-foreground">
                No Affordability Test Run Yet
              </h4>
              <p className="text-xs text-muted-foreground max-w-sm">
                Enter an item name and price tag on the left, or select one of the quick scenario chips above to simulate immediate affordability.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
