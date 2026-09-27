"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export const SUPPORTED_CURRENCIES = {
  USD: { code: "USD", symbol: "$", name: "US Dollar", flag: "🇺🇸", rate: 1.0, decimals: 2 },
  EUR: { code: "EUR", symbol: "€", name: "Euro", flag: "🇪🇺", rate: 0.92, decimals: 2 },
  GBP: { code: "GBP", symbol: "£", name: "British Pound", flag: "🇬🇧", rate: 0.79, decimals: 2 },
  INR: { code: "INR", symbol: "₹", name: "Indian Rupee", flag: "🇮🇳", rate: 83.5, decimals: 2 },
  CAD: { code: "CAD", symbol: "CA$", name: "Canadian Dollar", flag: "🇨🇦", rate: 1.36, decimals: 2 },
  AUD: { code: "AUD", symbol: "A$", name: "Australian Dollar", flag: "🇦🇺", rate: 1.52, decimals: 2 },
  JPY: { code: "JPY", symbol: "¥", name: "Japanese Yen", flag: "🇯🇵", rate: 155.0, decimals: 0 },
};

const CurrencyContext = createContext({
  currency: "USD",
  setCurrency: () => {},
  convert: (amount) => amount,
  format: (amount) => `$${Number(amount || 0).toFixed(2)}`,
  rates: {},
  currencies: Object.values(SUPPORTED_CURRENCIES),
});

export function CurrencyProvider({ children }) {
  const [currency, setCurrencyState] = useState("USD");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("fintra_currency");
      if (saved && SUPPORTED_CURRENCIES[saved]) {
        setCurrencyState(saved);
      }
    } catch {
      // Ignore localStorage access failures
    }
  }, []);

  const setCurrency = (code) => {
    if (!SUPPORTED_CURRENCIES[code]) return;
    setCurrencyState(code);
    try {
      localStorage.setItem("fintra_currency", code);
    } catch {
      // Ignore localStorage write failures
    }
  };

  const convert = (amountInUSD, targetCode = currency) => {
    const numeric = Number(amountInUSD) || 0;
    const curr = SUPPORTED_CURRENCIES[targetCode] || SUPPORTED_CURRENCIES.USD;
    return numeric * curr.rate;
  };

  const format = (amountInUSD, targetCode = currency) => {
    const numeric = Number(amountInUSD) || 0;
    const curr = SUPPORTED_CURRENCIES[targetCode] || SUPPORTED_CURRENCIES.USD;
    const converted = numeric * curr.rate;

    if (curr.code === "JPY") {
      return `${curr.symbol}${Math.round(converted).toLocaleString()}`;
    }

    return `${curr.symbol}${converted.toLocaleString(undefined, {
      minimumFractionDigits: curr.decimals,
      maximumFractionDigits: curr.decimals,
    })}`;
  };

  return (
    <CurrencyContext.Provider
      value={{
        currency,
        currentCurrency: SUPPORTED_CURRENCIES[currency] || SUPPORTED_CURRENCIES.USD,
        setCurrency,
        convert,
        format,
        rates: SUPPORTED_CURRENCIES,
        currencies: Object.values(SUPPORTED_CURRENCIES),
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency() {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error("useCurrency must be used within a CurrencyProvider");
  }
  return context;
}
