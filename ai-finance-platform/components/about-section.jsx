"use client";

import React, { useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  Building2, CreditCard, Cpu, Globe2,
  Send, ShieldCheck, TrendingUp, Sparkles,
  ArrowUpRight, Bot, Zap, CheckCircle, AlertTriangle,
  Sliders, Layers, Lock
} from "lucide-react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const partners = [
  { name: "Plaid",         sub: "Open Banking",  Icon: Building2 },
  { name: "Stripe",        sub: "Payments",       Icon: CreditCard },
  { name: "Gemini AI",     sub: "Intelligence",   Icon: Cpu },
  { name: "Visa",          sub: "Card Sync",      Icon: CreditCard },
  { name: "Open Banking",  sub: "Protocol",       Icon: Globe2 },
  { name: "Resend",        sub: "Notifications",  Icon: Send },
  { name: "SOC-2",         sub: "Compliant",      Icon: ShieldCheck },
  // duplicate for loop
  { name: "Plaid",         sub: "Open Banking",  Icon: Building2 },
  { name: "Stripe",        sub: "Payments",       Icon: CreditCard },
  { name: "Gemini AI",     sub: "Intelligence",   Icon: Cpu },
  { name: "Visa",          sub: "Card Sync",      Icon: CreditCard },
  { name: "Open Banking",  sub: "Protocol",       Icon: Globe2 },
  { name: "Resend",        sub: "Notifications",  Icon: Send },
  { name: "SOC-2",         sub: "Compliant",      Icon: ShieldCheck },
];

const studioTabs = [
  {
    id: "cashflow",
    title: "Predictive Cashflow",
    icon: TrendingUp,
    badge: "Real-Time AI",
  },
  {
    id: "guard",
    title: "Anomaly Guard",
    icon: ShieldCheck,
    badge: "Auto-Protected",
  },
  {
    id: "allocation",
    title: "Smart Allocation",
    icon: Zap,
    badge: "99.4% Match",
  },
];

const AboutSection = () => {
  const sectionRef = useRef(null);
  const marqueeRef = useRef(null);
  const [activeTab, setActiveTab] = useState("cashflow");

  useGSAP(() => {
    // Infinite marquee
    gsap.to(marqueeRef.current, {
      xPercent: -50,
      ease: "none",
      duration: 26,
      repeat: -1,
    });

    // Content reveal
    gsap.from(".about-content-anim", {
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top 75%",
      },
      y: 40,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      ease: "power3.out",
    });

    // Interactive widget entrance
    gsap.from(".studio-widget-anim", {
      scrollTrigger: {
        trigger: ".studio-widget-container",
        start: "top 80%",
      },
      scale: 0.94,
      y: 30,
      opacity: 0,
      duration: 0.8,
      ease: "back.out(1.4)",
    });
  }, { scope: sectionRef });

  return (
    <section
      id="fintech-studio"
      ref={sectionRef}
      className="py-24 bg-black relative overflow-hidden border-t border-neutral-900 scroll-mt-20"
    >

      {/* Dynamic ambient gradient orbs */}
      <div className="absolute left-1/4 top-1/3 -translate-y-1/2 w-[600px] h-[600px] bg-gsap-green/5 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute right-10 bottom-10 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="container mx-auto px-4 relative z-10 max-w-7xl">

        {/* ── Partner Marquee in Gray Transparent Pill ── */}
        <div className="text-center mb-4">
          <p className="text-[11px] uppercase tracking-[0.25em] text-neutral-400 font-bold">
            Integrated with Institutional Financial Infrastructure
          </p>
        </div>

        <div className="mb-20 rounded-2xl bg-white/[0.05] border border-white/[0.12] backdrop-blur-xl py-4 px-2 overflow-hidden relative shadow-[0_10px_30px_rgba(0,0,0,0.4)]">
          {/* Fade edges */}
          <div className="absolute left-0 inset-y-0 w-20 bg-gradient-to-r from-neutral-950/90 to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 inset-y-0 w-20 bg-gradient-to-l from-neutral-950/90 to-transparent z-10 pointer-events-none" />

          <div ref={marqueeRef} className="flex w-[200%] items-center">
            {partners.map(({ name, sub, Icon }, i) => (
              <div
                key={i}
                className="flex items-center gap-3 w-[calc(100%/14)] flex-shrink-0 group px-4 cursor-default"
              >
                <div className="w-10 h-10 rounded-xl bg-white/[0.08] border border-white/[0.15] flex items-center justify-center text-gsap-green group-hover:border-gsap-green group-hover:bg-gsap-green/20 group-hover:scale-105 transition-all duration-300 shadow-sm">
                  <Icon size={18} />
                </div>
                <div>
                  <p className="font-extrabold text-white text-sm leading-none group-hover:text-gsap-green transition-colors tracking-tight">{name}</p>
                  <p className="text-[10px] text-neutral-300 font-medium uppercase tracking-wider mt-1">{sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Main Manifesto & Interactive Studio Grid ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">

          {/* Left Column: Rich Manifesto */}
          <div className="lg:col-span-6 space-y-8">
            <div className="about-content-anim inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] border border-white/[0.12] text-xs font-semibold text-neutral-300 backdrop-blur-md">
              <Sparkles className="w-3.5 h-3.5 text-gsap-green animate-pulse" />
              <span>Next-Gen Neural Financial Engine</span>
            </div>

            <h2 className="about-content-anim text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-[1.12]">
              Personal finance shouldn&apos;t mean{" "}
              <span className="text-neutral-500 block">drowning in spreadsheets.</span>
              <span className="mt-3 block text-gsap-green">
                Fintra AI moves intelligence directly into daily actions.
              </span>
            </h2>

            <p className="about-content-anim text-neutral-400 text-base sm:text-lg leading-relaxed max-w-xl">
              While traditional finance apps only show what already happened, Fintra predicts what will happen next — forecasting cashflows, preventing wasteful drains, and compounding net worth automatically.
            </p>

            {/* Micro Highlights Pill Row */}
            <div className="about-content-anim grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
              <div className="p-3.5 rounded-xl bg-neutral-900/80 border border-neutral-800/90 hover:border-neutral-700 transition-colors">
                <div className="text-xl font-black text-gsap-green tabular-nums">+43%</div>
                <div className="text-xs text-neutral-400 font-medium mt-0.5">Average Savings Rate</div>
              </div>
              <div className="p-3.5 rounded-xl bg-neutral-900/80 border border-neutral-800/90 hover:border-neutral-700 transition-colors">
                <div className="text-xl font-black text-gsap-green tabular-nums">&lt; 0.2s</div>
                <div className="text-xs text-neutral-400 font-medium mt-0.5">Receipt Parsing Time</div>
              </div>
              <div className="p-3.5 rounded-xl bg-neutral-900/80 border border-neutral-800/90 col-span-2 sm:col-span-1 hover:border-neutral-700 transition-colors">
                <div className="text-xl font-black text-gsap-green tabular-nums">256-bit</div>
                <div className="text-xs text-neutral-400 font-medium mt-0.5">SOC-2 Bank Encryption</div>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Studio Widget */}
          <div className="lg:col-span-6 studio-widget-container">
            <div className="studio-widget-anim rounded-2xl border border-neutral-800/90 bg-neutral-950/90 shadow-[0_25px_70px_rgba(0,0,0,0.8),inset_0_1px_0_rgba(255,255,255,0.1)] overflow-hidden backdrop-blur-xl">

              {/* Studio Header Bar */}
              <div className="flex items-center justify-between px-5 py-3.5 bg-neutral-900/90 border-b border-neutral-800">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-gsap-green animate-pulse" />
                  <span className="text-xs font-bold text-white tracking-wide uppercase">
                    Fintra Studio Preview
                  </span>
                </div>
                <span className="text-[11px] text-neutral-400 font-mono bg-black/40 px-2.5 py-1 rounded-md border border-neutral-800">
                  Model: Fintra-Neural-v3
                </span>
              </div>

              {/* Interactive Tabs */}
              <div className="p-2 bg-black/40 border-b border-neutral-800/80 flex gap-1.5 overflow-x-auto">
                {studioTabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 whitespace-nowrap ${
                        isActive
                          ? "bg-neutral-800 text-white shadow-sm border border-neutral-700"
                          : "text-neutral-400 hover:text-white hover:bg-neutral-900/50"
                      }`}
                    >
                      <Icon className={`w-3.5 h-3.5 ${isActive ? "text-gsap-green" : "text-neutral-500"}`} />
                      <span>{tab.title}</span>
                    </button>
                  );
                })}
              </div>

              {/* Tab Dynamic Content Body */}
              <div className="p-6">
                {activeTab === "cashflow" && (
                  <div className="space-y-4 animate-in fade-in duration-300">
                    <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                      <div>
                        <div className="text-xs text-neutral-500 font-semibold uppercase tracking-wider">Projected 30-Day Surplus</div>
                        <div className="text-2xl font-black text-gsap-green mt-0.5">+$4,820.00</div>
                      </div>
                      <div className="px-3 py-1.5 rounded-full bg-gsap-green/10 text-gsap-green border border-gsap-green/20 text-xs font-bold flex items-center gap-1.5">
                        <ArrowUpRight className="w-3.5 h-3.5" />
                        <span>98.6% Confidence</span>
                      </div>
                    </div>

                    {/* Simulated Forecast Curve */}
                    <div className="rounded-xl bg-neutral-900/70 border border-neutral-800 p-4 space-y-2">
                      <div className="flex justify-between text-xs font-medium text-neutral-400">
                        <span>Autonomous Cashflow Vector</span>
                        <span className="text-gsap-green font-bold">+18.2% vs Last Month</span>
                      </div>
                      <div className="flex items-end gap-2 h-20 pt-2">
                        {[35, 48, 52, 65, 59, 78, 85, 94].map((val, idx) => (
                          <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                            <div
                              className="w-full rounded-t-sm transition-all duration-500"
                              style={{
                                height: `${val}%`,
                                background: idx >= 5
                                  ? "#88ce02"
                                  : `rgba(136,206,2,${0.2 + idx * 0.08})`,
                              }}
                            />
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between text-[10px] text-neutral-600 font-mono">
                        <span>Day 1</span>
                        <span>Day 15</span>
                        <span>Day 30 (Forecast)</span>
                      </div>
                    </div>

                    {/* Live Stream Line */}
                    <div className="flex items-center justify-between p-3 rounded-xl bg-neutral-900/50 border border-neutral-800 text-xs text-neutral-300">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-gsap-green animate-ping" />
                        <span>Auto-diverted <strong>$450.00</strong> to High-Yield Vault</span>
                      </div>
                      <span className="text-[10px] text-neutral-500 font-mono">2m ago</span>
                    </div>
                  </div>
                )}

                {activeTab === "guard" && (
                  <div className="space-y-3 animate-in fade-in duration-300">
                    <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                      <div>
                        <div className="text-xs text-neutral-500 font-semibold uppercase tracking-wider">Shield Status</div>
                        <div className="text-xl font-black text-white mt-0.5">Active & Monitoring</div>
                      </div>
                      <div className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>All 6 Accounts Synced</span>
                      </div>
                    </div>

                    {/* Threat / Optimization Card 1 */}
                    <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3">
                      <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="text-xs font-bold text-amber-200">Price Hike Detected: Cloud Storage</div>
                        <div className="text-[11px] text-amber-300/80 mt-0.5">Increased by +$12.99/mo without notification. Auto-negotiation ready.</div>
                      </div>
                      <span className="text-[10px] bg-amber-500/20 text-amber-300 font-bold px-2 py-0.5 rounded">Action Ready</span>
                    </div>

                    {/* Threat / Optimization Card 2 */}
                    <div className="p-3.5 rounded-xl bg-neutral-900 border border-neutral-800 flex items-start gap-3">
                      <CheckCircle className="w-4 h-4 text-gsap-green flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="text-xs font-bold text-white">Duplicate SaaS Charge Blocked</div>
                        <div className="text-[11px] text-neutral-400 mt-0.5">Prevented $49.00 double billing from Workspace API.</div>
                      </div>
                      <span className="text-[10px] text-gsap-green font-bold">Saved $49</span>
                    </div>
                  </div>
                )}

                {activeTab === "allocation" && (
                  <div className="space-y-4 animate-in fade-in duration-300">
                    <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                      <div>
                        <div className="text-xs text-neutral-500 font-semibold uppercase tracking-wider">Automated Portfolio Health</div>
                        <div className="text-2xl font-black text-white mt-0.5">96 / 100</div>
                      </div>
                      <span className="text-xs font-bold text-gsap-green bg-gsap-green/10 border border-gsap-green/20 px-3 py-1 rounded-full">Optimal Ratio</span>
                    </div>

                    {/* Allocation Bars */}
                    <div className="space-y-2.5">
                      {[
                        { label: "Index Equities & ETFs", pct: "60%", color: "#88ce02" },
                        { label: "High-Yield Cash Reserves", pct: "25%", color: "#34d399" },
                        { label: "Alternative & Crypto Assets", pct: "15%", color: "#a3e635" },
                      ].map((item) => (
                        <div key={item.label} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="text-neutral-300 font-medium">{item.label}</span>
                            <span className="text-white font-bold">{item.pct}</span>
                          </div>
                          <div className="h-2 rounded-full bg-neutral-800 overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{ width: item.pct, backgroundColor: item.color }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>

        </div>

      </div>
    </section>
  );
};

export default AboutSection;
