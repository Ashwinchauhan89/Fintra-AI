"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRightLeft, Globe, Sparkles, TrendingUp } from "lucide-react";
import { SUPPORTED_CURRENCIES, useCurrency } from "@/lib/currency-context";

export function FXConverterCard() {
  const { currency: activeCurrency } = useCurrency();
  const [amount, setAmount] = useState("100");
  const [fromCode, setFromCode] = useState(activeCurrency || "USD");
  const [toCode, setToCode] = useState("INR");

  const fromCurr = SUPPORTED_CURRENCIES[fromCode] || SUPPORTED_CURRENCIES.USD;
  const toCurr = SUPPORTED_CURRENCIES[toCode] || SUPPORTED_CURRENCIES.INR;

  // Convert via base USD: Amount / fromRate * toRate
  const numericAmount = Math.max(0, Number(amount) || 0);
  const amountInUSD = numericAmount / fromCurr.rate;
  const convertedAmount = amountInUSD * toCurr.rate;
  const exchangeRate = toCurr.rate / fromCurr.rate;

  const handleSwap = () => {
    setFromCode(toCode);
    setToCode(fromCode);
  };

  return (
    <Card className="border-border/60 shadow-sm overflow-hidden bg-gradient-to-br from-card to-card/60">
      <CardHeader className="pb-3 border-b border-border/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Globe className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-bold tracking-tight">
                Live Global FX Converter
              </CardTitle>
              <CardDescription className="text-[11px] text-muted-foreground">
                Real-time multi-currency exchange rate calculator
              </CardDescription>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 font-semibold flex items-center gap-1">
            <Sparkles className="h-3 w-3" /> Live Pegs
          </span>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {/* Converter Inputs Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-center">
          {/* Amount & From */}
          <div className="sm:col-span-2 space-y-1.5">
            <label className="text-[11px] font-semibold text-muted-foreground">
              Send Amount
            </label>
            <div className="flex gap-1.5">
              <Input
                type="number"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="font-mono text-sm font-bold"
                placeholder="0.00"
              />
              <select
                value={fromCode}
                onChange={(e) => setFromCode(e.target.value)}
                className="bg-muted text-foreground text-xs font-semibold px-2 py-1 rounded-md border border-input focus:outline-none"
              >
                {Object.values(SUPPORTED_CURRENCIES).map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.flag} {c.code}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Swap Button */}
          <div className="sm:col-span-1 flex justify-center pt-5">
            <Button
              type="button"
              variant="outline"
              size="icon"
              className="h-9 w-9 rounded-full border-border/80 hover:bg-muted"
              onClick={handleSwap}
            >
              <ArrowRightLeft className="h-4 w-4 text-muted-foreground" />
            </Button>
          </div>

          {/* Result & To */}
          <div className="sm:col-span-2 space-y-1.5">
            <label className="text-[11px] font-semibold text-muted-foreground">
              Recipient Gets
            </label>
            <div className="flex gap-1.5">
              <div className="flex-1 px-3 py-2 bg-muted/50 border border-input rounded-md font-mono text-sm font-bold text-foreground flex items-center overflow-x-auto">
                {toCurr.symbol}
                {convertedAmount.toLocaleString(undefined, {
                  minimumFractionDigits: toCurr.decimals,
                  maximumFractionDigits: toCurr.decimals,
                })}
              </div>
              <select
                value={toCode}
                onChange={(e) => setToCode(e.target.value)}
                className="bg-muted text-foreground text-xs font-semibold px-2 py-1 rounded-md border border-input focus:outline-none"
              >
                {Object.values(SUPPORTED_CURRENCIES).map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.flag} {c.code}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Exchange Rate Badge Note */}
        <div className="flex items-center justify-between text-[11px] text-muted-foreground bg-muted/30 p-2.5 rounded-lg border border-border/40 font-mono">
          <div className="flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-primary" />
            <span>Indicative Rate:</span>
          </div>
          <span className="font-bold text-foreground">
            1 {fromCode} = {exchangeRate.toFixed(4)} {toCode}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
