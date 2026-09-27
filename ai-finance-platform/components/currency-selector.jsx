"use client";

import React from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useCurrency, SUPPORTED_CURRENCIES } from "@/lib/currency-context";
import { Check, Globe } from "lucide-react";

export function CurrencySelector() {
  const { currency, setCurrency } = useCurrency();
  const current = SUPPORTED_CURRENCIES[currency] || SUPPORTED_CURRENCIES.USD;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="border-white/20 hover:border-white/40 hover:text-white hover:bg-white/10 text-white bg-white/5 font-semibold text-xs h-9 px-2.5 gap-1.5 flex items-center transition-all"
        >
          <span className="text-sm">{current.flag}</span>
          <span className="font-mono">{current.code}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-56 bg-neutral-900/95 border-white/20 backdrop-blur-xl text-neutral-100 shadow-2xl p-1.5 z-[100]"
      >
        <DropdownMenuLabel className="text-xs font-semibold text-neutral-400 px-2 py-1.5 flex items-center gap-1.5">
          <Globe className="h-3.5 w-3.5 text-[#88CE02]" />
          Display Currency
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-white/10" />
        {Object.values(SUPPORTED_CURRENCIES).map((c) => {
          const isSelected = c.code === currency;
          return (
            <DropdownMenuItem
              key={c.code}
              onClick={() => setCurrency(c.code)}
              className={`flex items-center justify-between px-2 py-1.5 rounded-md text-xs cursor-pointer transition-colors ${
                isSelected
                  ? "bg-white/10 text-[#88CE02] font-semibold"
                  : "hover:bg-white/5 text-neutral-200"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-base">{c.flag}</span>
                <div>
                  <div className="flex items-center gap-1">
                    <span className="font-mono font-bold">{c.code}</span>
                    <span className="text-[11px] text-neutral-400">({c.symbol})</span>
                  </div>
                  <p className="text-[10px] text-neutral-400 leading-none">{c.name}</p>
                </div>
              </div>
              {isSelected && <Check className="h-3.5 w-3.5 text-[#88CE02]" />}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
