"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Menu,
  X,
  LayoutDashboard,
  CreditCard,
  FileText,
  Upload,
  PenBox,
  Sparkles,
} from "lucide-react";
import { Button } from "./ui/button";

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="md:hidden">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="rounded-full text-white hover:bg-white/10 h-9 w-9"
        aria-label="Toggle Navigation Menu"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </Button>

      {isOpen && (
        <div className="absolute top-16 left-4 right-4 bg-black/95 backdrop-blur-2xl border border-white/20 rounded-2xl p-4 shadow-2xl space-y-2 animate-in fade-in slide-in-from-top-3 z-50">
          <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider px-3 py-1">
            Navigation Menu
          </div>

          <Link
            href="/dashboard"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-3 py-2 rounded-xl text-neutral-200 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors"
          >
            <LayoutDashboard size={18} className="text-primary" />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/subscriptions"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-3 py-2 rounded-xl text-neutral-200 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors"
          >
            <CreditCard size={18} className="text-[#88CE02]" />
            <span>Subscriptions Tracker</span>
          </Link>

          <Link
            href="/reports"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-3 py-2 rounded-xl text-neutral-200 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors"
          >
            <FileText size={18} className="text-blue-400" />
            <span>Executive Reports & Statements</span>
          </Link>

          <Link
            href="/transaction/import"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-3 py-2 rounded-xl text-neutral-200 hover:text-white hover:bg-white/10 text-sm font-medium transition-colors"
          >
            <Upload size={18} className="text-amber-400" />
            <span>Import Bank Statement (CSV)</span>
          </Link>

          <div className="pt-2 border-t border-white/10">
            <Link
              href="/transaction/create"
              onClick={() => setIsOpen(false)}
              className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-[#88CE02] text-black hover:bg-lime-400 font-extrabold text-sm shadow transition-colors"
            >
              <PenBox size={16} />
              <span>Add Transaction</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
