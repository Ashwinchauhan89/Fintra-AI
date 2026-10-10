"use client";

import React, { useState } from "react";
import {
  CreditCard,
  Calendar,
  DollarSign,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  ArrowUpRight,
  TrendingDown,
  Plus,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { format } from "date-fns";

export function SubscriptionTracker({ initialData }) {
  const [data, setData] = useState(
    initialData || {
      subscriptions: [
        {
          id: "sub-1",
          name: "Netflix Premium",
          category: "entertainment",
          amount: 19.99,
          interval: "MONTHLY",
          nextPayment: new Date(Date.now() + 3 * 86400000).toISOString(),
          accountName: "Main Checking",
          isDetected: false,
        },
        {
          id: "sub-2",
          name: "Spotify Individual",
          category: "entertainment",
          amount: 10.99,
          interval: "MONTHLY",
          nextPayment: new Date(Date.now() + 11 * 86400000).toISOString(),
          accountName: "Main Checking",
          isDetected: false,
        },
        {
          id: "sub-3",
          name: "Amazon Prime Annual",
          category: "entertainment",
          amount: 139.00,
          interval: "YEARLY",
          nextPayment: new Date(Date.now() + 65 * 86400000).toISOString(),
          accountName: "Credit Card",
          isDetected: false,
        },
        {
          id: "sub-4",
          name: "GitHub Copilot",
          category: "education",
          amount: 10.00,
          interval: "MONTHLY",
          nextPayment: new Date(Date.now() + 18 * 86400000).toISOString(),
          accountName: "Main Checking",
          isDetected: true,
        },
      ],
      monthlyTotal: 52.56,
      annualTotal: 630.72,
      activeCount: 4,
    }
  );

  const { subscriptions, monthlyTotal, annualTotal, activeCount } = data;

  // Potential savings if switching monthly subscriptions to annual billing (est. 18% savings)
  const potentialAnnualSavings = Math.round(monthlyTotal * 12 * 0.18);

  return (
    <div className="space-y-6">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Monthly Commitment
            </CardTitle>
            <DollarSign className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              ${monthlyTotal.toFixed(2)}
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Active recurring run-rate
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Projected Annual Cost
            </CardTitle>
            <Calendar className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              ${annualTotal.toFixed(2)}
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Over 12 billing cycles
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-muted-foreground">
              Active Subscriptions
            </CardTitle>
            <CreditCard className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              {activeCount}
            </div>
            <p className="text-[11px] text-muted-foreground mt-1">
              Tracked recurring services
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow border-emerald-500/20 bg-emerald-500/5">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
              Annual Savings Potential
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              ${potentialAnnualSavings}
            </div>
            <p className="text-[11px] text-emerald-600/80 dark:text-emerald-400/80 mt-1">
              Switching to annual plans
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Subscriptions Table Card */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4">
          <div>
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-primary" />
              Active Subscriptions & Recurring Bills
            </CardTitle>
            <CardDescription>
              Comprehensive ledger of recurring commitments across all bank accounts
            </CardDescription>
          </div>
          <Link href="/transaction/create">
            <Button size="sm" className="gap-1.5 text-xs font-semibold">
              <Plus className="h-4 w-4" />
              Add Recurring Bill
            </Button>
          </Link>
        </CardHeader>

        <CardContent className="p-0 overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/50 border-b text-muted-foreground font-semibold">
              <tr>
                <th className="p-3.5">Service Name</th>
                <th className="p-3.5">Category</th>
                <th className="p-3.5">Billing Cadence</th>
                <th className="p-3.5">Next Renewal</th>
                <th className="p-3.5">Account Source</th>
                <th className="p-3.5 text-right">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {subscriptions.map((sub) => (
                <tr key={sub.id} className="hover:bg-muted/30 transition-colors">
                  <td className="p-3.5 font-semibold text-foreground flex items-center gap-2">
                    <div className="h-7 w-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-xs uppercase">
                      {sub.name.slice(0, 2)}
                    </div>
                    <div>
                      <span>{sub.name}</span>
                      {sub.isDetected && (
                        <Badge variant="outline" className="ml-2 text-[9px] px-1 py-0 bg-blue-500/10 text-blue-500 border-blue-500/20">
                          Auto-Detected
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="p-3.5 capitalize">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-muted font-medium text-foreground">
                      {sub.category}
                    </span>
                  </td>
                  <td className="p-3.5 capitalize font-medium text-muted-foreground">
                    <Badge variant="secondary" className="text-[10px] uppercase font-semibold">
                      {sub.interval}
                    </Badge>
                  </td>
                  <td className="p-3.5 font-mono text-muted-foreground">
                    {sub.nextPayment ? format(new Date(sub.nextPayment), "MMM dd, yyyy") : "Pending"}
                  </td>
                  <td className="p-3.5 text-muted-foreground">
                    {sub.accountName}
                  </td>
                  <td className="p-3.5 text-right font-mono font-bold text-foreground">
                    ${Number(sub.amount).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Optimization Insights Banner */}
      <Card className="border-primary/20 bg-gradient-to-r from-primary/5 via-card to-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-500" />
            AI Subscription Intelligence & Optimization Tips
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs text-muted-foreground">
          <div className="flex items-start gap-2 bg-muted/30 p-2.5 rounded-lg border">
            <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
            <span>
              <strong>Annual Billing Discount:</strong> Switching services like Netflix, Spotify, or Prime to annual upfront billing typically yields 15%–20% discounts, saving up to <strong>${potentialAnnualSavings}/year</strong>.
            </span>
          </div>
          <div className="flex items-start gap-2 bg-muted/30 p-2.5 rounded-lg border">
            <AlertCircle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
            <span>
              <strong>Entertainment Overlap:</strong> You have multiple active digital media streaming subscriptions. Audit usage to eliminate underutilized platforms.
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
