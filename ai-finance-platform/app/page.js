"use client";

import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Image from "next/image";
import {
  featuresData,
  howItWorksData,
  statsData,
  testimonialsData,
  faqData,
} from "@/data/landing";
import HeroSection from "@/components/hero";
import AboutSection from "@/components/about-section";
import Footer from "@/components/footer";
import Link from "next/link";

import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CheckCircle2, ArrowRight, Star, ChevronDown, HelpCircle, ShieldCheck, Check } from "lucide-react";


if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const TestimonialsSpotlight = () => {

  const [activeIdx, setActiveIdx] = useState(0);
  const activeReview = testimonialsData[activeIdx] || testimonialsData[0];

  return (
    <section
      id="testimonials"
      className="testimonials-section py-28 bg-black border-t border-neutral-900 relative overflow-hidden scroll-mt-28"
    >

      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-gsap-green/5 rounded-full blur-[140px] pointer-events-none" />

      <div className="container mx-auto px-4 md:px-8 relative z-10 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-gsap-green/10 border border-gsap-green/25 text-gsap-green text-xs font-bold uppercase tracking-widest mb-4">
            <Star className="w-3.5 h-3.5 fill-gsap-green" />
            <span>Customer Spotlight</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4 text-white">
            Loved by <span className="text-gsap-green">50,000+</span> wealth builders
          </h2>
          <p className="text-neutral-400 text-sm md:text-base">
            Click any member below to review their verified real-world financial impact.
          </p>
        </div>

        {/* 3 Interactive Customer Selector Pills */}
        <div className="flex flex-wrap items-center justify-center gap-3 md:gap-4 mb-10">
          {testimonialsData.slice(0, 3).map((t, idx) => {
            const isActive = activeIdx === idx;
            return (
              <button
                key={idx}
                onClick={() => setActiveIdx(idx)}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-full border transition-all duration-300 ${
                  isActive
                    ? "bg-gsap-green/15 border-gsap-green text-white shadow-[0_0_25px_rgba(136,206,2,0.3)] scale-105"
                    : "bg-neutral-900/80 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-white"
                }`}
              >
                <Image
                  src={t.image}
                  alt={t.name}
                  width={32}
                  height={32}
                  className={`rounded-full object-cover ring-2 transition-all ${
                    isActive ? "ring-gsap-green" : "ring-neutral-700"
                  }`}
                />
                <div className="text-left text-xs">
                  <div className={`font-bold ${isActive ? "text-gsap-green" : "text-white"}`}>
                    {t.name}
                  </div>
                  <div className="text-[10px] text-neutral-500">{t.role}</div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Center Spotlight Showcase Card */}
        <div className="relative rounded-3xl bg-neutral-950 border border-neutral-800/90 p-8 md:p-12 backdrop-blur-2xl shadow-[0_30px_90px_rgba(0,0,0,0.8)] overflow-hidden">
          {/* Top glowing line */}
          <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-gsap-green to-transparent opacity-80" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Story Quote (8 cols) */}
            <div className="lg:col-span-8 space-y-6">
              <div className="flex items-center gap-2">
                <div className="flex gap-1 text-gsap-green">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="w-4 h-4 fill-gsap-green" />
                  ))}
                </div>
                <span className="text-xs font-mono font-bold text-neutral-400 ml-2">
                  5.0 ★ Verified Plaid Member
                </span>
              </div>

              <blockquote className="text-xl sm:text-2xl md:text-3xl font-medium text-white leading-snug tracking-tight">
                &ldquo;{activeReview.quote}&rdquo;
              </blockquote>

              <div className="flex items-center gap-4 pt-4 border-t border-neutral-900">
                <Image
                  src={activeReview.image}
                  alt={activeReview.name}
                  width={52}
                  height={52}
                  className="rounded-full ring-2 ring-gsap-green object-cover"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-black text-white text-base md:text-lg">{activeReview.name}</h4>
                    <span className="inline-flex items-center gap-1 text-[11px] font-mono text-gsap-green px-2 py-0.5 rounded-full bg-gsap-green/10 border border-gsap-green/20">
                      <CheckCircle2 className="w-3 h-3" />
                      Verified
                    </span>
                  </div>
                  <p className="text-neutral-400 text-xs md:text-sm">{activeReview.role}</p>
                </div>
              </div>
            </div>

            {/* Right Financial Impact Tile (4 cols) */}
            <div className="lg:col-span-4 rounded-2xl bg-neutral-900/80 border border-neutral-800 p-6 flex flex-col justify-between space-y-4">
              <div>
                <div className="text-[10px] font-mono font-bold uppercase tracking-widest text-neutral-500 mb-1">
                  Verified Financial Impact
                </div>
                <div className="text-3xl sm:text-4xl font-black text-gsap-green tracking-tight">
                  {activeReview.impact}
                </div>
                <p className="text-neutral-400 text-xs mt-2 leading-relaxed">
                  Real audit telemetry recorded across automated savings and AI transaction categorization.
                </p>
              </div>

              <div className="pt-3 border-t border-neutral-800/80 flex items-center justify-between text-[11px] font-mono text-neutral-400">
                <span>Data Protection</span>
                <span className="text-white font-bold">256-Bit TLS</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const LandingPage = () => {

  const mainRef = useRef(null);
  const [openFaq, setOpenFaq] = useState(null);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  useGSAP(() => {
    // Progress bar
    gsap.to(".progress-bar", {
      scrollTrigger: {
        trigger: document.documentElement,
        start: "top top",
        end: "bottom bottom",
        scrub: 0.3,
      },
      scaleX: 1,
      ease: "none",
      transformOrigin: "left center",
    });

    // Stats
    gsap.from(".stat-item", {
      scrollTrigger: { trigger: ".stats-section", start: "top 85%" },
      y: 30,
      opacity: 0,
      duration: 0.7,
      stagger: 0.1,
      ease: "power2.out",
    });

    // Features Horizontal Scroll on Scroll — calibrated travel from card 1 to card 6
    const track = document.querySelector(".features-slider-track");
    const container = document.querySelector(".features-scroll-container");
    if (track && container) {
      const getDistance = () => {
        const parent = track.parentElement;
        const visibleWidth = parent ? parent.clientWidth : window.innerWidth * 0.62;
        return track.scrollWidth - visibleWidth + 40;
      };

      gsap.to(track, {
        x: () => -getDistance(),
        ease: "none",
        scrollTrigger: {
          trigger: container,
          start: "top top",
          end: () => "+=" + (getDistance() + 800),
          pin: true,
          scrub: 0.8,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });
    }

    // How it works
    gsap.from(".step-item", {
      scrollTrigger: { trigger: "#security", start: "top 80%" },
      y: 40,
      opacity: 0,
      duration: 0.7,
      stagger: 0.15,
      ease: "power3.out",
    });

    // Testimonials
    gsap.from(".testimonial-card", {
      scrollTrigger: { trigger: "#testimonials", start: "top 80%" },
      y: 30,
      opacity: 0,
      duration: 0.6,
      stagger: 0.12,
      ease: "power2.out",
    });

    // FAQ items
    gsap.from(".faq-item", {
      scrollTrigger: { trigger: "#faq", start: "top 80%" },
      y: 25,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      ease: "power2.out",
    });

    // CTA parallax
    gsap.to(".cta-shape-1", {
      scrollTrigger: { trigger: ".cta-section", start: "top bottom", end: "bottom top", scrub: 1 },
      y: -80,
    });
    gsap.to(".cta-shape-2", {
      scrollTrigger: { trigger: ".cta-section", start: "top bottom", end: "bottom top", scrub: 1 },
      y: 80,
    });
  }, { scope: mainRef });

  return (
    <div
      ref={mainRef}
      className="min-h-screen bg-background text-foreground selection:bg-gsap-green selection:text-black"
    >
      {/* ─── Scroll Progress Bar ─── */}
      <div className="progress-bar fixed top-0 left-0 w-full h-[3px] bg-gsap-green z-[100] scale-x-0 origin-left" />

      {/* ─── 1. Hero ─── */}
      <HeroSection />

      {/* ─── 2. Interactive Studio / About & Manifesto ─── */}
      <AboutSection />

      {/* ─── 3. Stats ─── */}
      <section className="stats-section py-16 md:py-20 bg-neutral-950 border-t border-neutral-900 relative overflow-hidden">
        <div className="absolute inset-0 dot-grid opacity-40 pointer-events-none" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {statsData.map((stat, i) => (
              <div key={i} className="stat-item text-center group relative">
                {i > 0 && (
                  <div className="hidden md:block absolute left-0 top-1/2 -translate-y-1/2 h-12 w-px bg-neutral-800" />
                )}
                <div className="text-4xl md:text-5xl font-black text-gsap-green mb-1.5 tabular-nums tracking-tight">
                  {stat.value}
                </div>
                <div className="text-white font-semibold text-sm uppercase tracking-widest mb-1">
                  {stat.label}
                </div>
                <div className="text-neutral-500 text-xs hidden sm:block">{stat.suffix}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── 4. Features (Pinned Side-by-Side Horizontal Scroll with Live Mini-Widgets) ─── */}
      <section
        id="features"
        className="features-scroll-container h-screen bg-black flex flex-col lg:flex-row items-center overflow-hidden border-t border-neutral-900 relative scroll-mt-28"
      >

        {/* Left Sticky Title Column */}
        <div className="w-full lg:w-[38%] flex-shrink-0 z-20 bg-black flex flex-col justify-center pl-6 md:pl-16 pr-8 relative h-auto lg:h-full py-8 lg:py-0">
          <div className="hidden lg:block absolute -right-12 top-0 bottom-0 w-16 bg-gradient-to-r from-black to-transparent pointer-events-none z-30" />
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gsap-green/10 border border-gsap-green/25 text-gsap-green text-xs font-bold uppercase tracking-widest mb-5 w-fit">
            Core Features
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black mb-5 leading-[1.12] tracking-tight text-white">
            Everything you need to{" "}
            <span className="text-gsap-green block">master your money</span>
          </h2>
          <p className="text-neutral-400 text-sm md:text-base leading-relaxed max-w-sm mb-6">
            AI-driven tools built for real personal finance intelligence &mdash; sliding seamlessly into your workflow.
          </p>

          <div className="flex items-center gap-3 text-xs text-neutral-400 font-mono">
            <span className="inline-block w-2 h-2 rounded-full bg-gsap-green animate-ping" />
            <span>6 Live AI Modules Active</span>
          </div>
        </div>

        {/* Right Sliding Cards Track */}
        <div className="flex-1 overflow-hidden flex items-center h-full relative z-10">
          <div className="features-slider-track flex items-center gap-6 pl-4 pr-16 flex-nowrap flex-shrink-0">
            {featuresData.map((feature, i) => (
              <div
                key={i}
                className="feature-card-wrapper w-[330px] sm:w-[380px] md:w-[410px] h-[410px] flex-shrink-0 group"
              >
                <div
                  className="h-full rounded-2xl bg-neutral-950/90 border border-neutral-800/90 hover:border-gsap-green/60 transition-all duration-300 flex flex-col justify-between relative overflow-hidden backdrop-blur-xl group-hover:shadow-[0_20px_50px_rgba(136,206,2,0.15)] group-hover:-translate-y-1"
                >
                  {/* Neon Green Top Accent Line */}
                  <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-gsap-green via-emerald-400 to-transparent opacity-70 group-hover:opacity-100 transition-opacity" />

                  {/* Watermark Number */}
                  <div className="absolute -top-2 right-4 text-7xl font-black text-gsap-green opacity-[0.06] group-hover:opacity-[0.14] transition-opacity select-none pointer-events-none tabular-nums font-mono">
                    {`0${i + 1}`}
                  </div>

                  {/* Card Body */}
                  <div className="p-7 flex flex-col h-full justify-between relative z-10">
                    <div className="space-y-4">
                      {/* Top row: Icon + Tag */}
                      <div className="flex items-center justify-between">
                        <div className="w-12 h-12 rounded-xl bg-gsap-green/10 border border-gsap-green/25 text-gsap-green flex items-center justify-center transition-all duration-300 group-hover:bg-gsap-green/20 group-hover:scale-105">
                          {feature.icon}
                        </div>

                        <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border border-gsap-green/25 text-gsap-green bg-gsap-green/10">
                          {feature.tag}
                        </span>
                      </div>

                      <div>
                        <h3 className="text-xl font-bold text-white mb-2 group-hover:text-gsap-green transition-colors duration-200">
                          {feature.title}
                        </h3>
                        <p className="text-neutral-400 text-xs sm:text-sm leading-relaxed">
                          {feature.description}
                        </p>
                      </div>

                      {/* Interactive Mini Widgets inside each card */}
                      {i === 0 && (
                        <div className="p-3 rounded-xl bg-neutral-900/80 border border-neutral-800 text-xs flex items-center justify-between">
                          <div>
                            <div className="text-[10px] text-neutral-500 uppercase font-bold">Monthly Trend</div>
                            <div className="text-sm font-black text-white">$4,820 <span className="text-gsap-green text-xs font-bold">+14%</span></div>
                          </div>
                          <div className="flex items-end gap-1 h-6">
                            {[40, 60, 45, 80, 95].map((h, idx) => (
                              <div key={idx} className="w-1.5 rounded-t bg-gsap-green" style={{ height: `${h}%` }} />
                            ))}
                          </div>
                        </div>
                      )}

                      {i === 1 && (
                        <div className="p-3 rounded-xl bg-neutral-900/80 border border-neutral-800 text-xs flex items-center gap-2.5">
                          <div className="w-2 h-2 rounded-full bg-gsap-green animate-pulse" />
                          <div className="flex-1">
                            <span className="text-white font-bold">Uber Receipt: $24.50</span>
                            <div className="text-[10px] text-gsap-green">Auto-categorized &rarr; Transport</div>
                          </div>
                        </div>
                      )}

                      {i === 2 && (
                        <div className="p-3 rounded-xl bg-neutral-900/80 border border-neutral-800 space-y-1.5">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-neutral-400">Monthly Budget</span>
                            <span className="text-gsap-green font-bold">78% Safe</span>
                          </div>
                          <div className="h-1.5 rounded-full bg-neutral-800 overflow-hidden">
                            <div className="h-full bg-gsap-green rounded-full w-[78%]" />
                          </div>
                        </div>
                      )}

                      {i === 3 && (
                        <div className="flex gap-1.5 flex-wrap">
                          <span className="px-2 py-1 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] font-mono text-neutral-300">Chase ••4912</span>
                          <span className="px-2 py-1 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] font-mono text-neutral-300">Amex Gold</span>
                          <span className="px-2 py-1 rounded-md bg-gsap-green/10 border border-gsap-green/20 text-[10px] font-mono text-gsap-green">+3 Synced</span>
                        </div>
                      )}

                      {i === 4 && (
                        <div className="p-2.5 rounded-xl bg-neutral-900/80 border border-neutral-800 flex items-center justify-between text-[11px] font-mono">
                          <span className="text-white font-bold">1 USD</span>
                          <span className="text-neutral-500">&harr;</span>
                          <span className="text-gsap-green font-bold">0.92 EUR</span>
                          <span className="text-neutral-500">&harr;</span>
                          <span className="text-neutral-300 font-bold">0.79 GBP</span>
                        </div>
                      )}

                      {i === 5 && (
                        <div className="p-3 rounded-xl bg-gsap-green/10 border border-gsap-green/20 text-xs flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-gsap-green" />
                          <span className="text-neutral-200 text-[11px]"><strong>AI Action:</strong> Diverted $200 surplus to Savings</span>
                        </div>
                      )}
                    </div>

                    {/* Footer link */}
                    <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-gsap-green opacity-80 group-hover:opacity-100 transition-opacity pt-2">
                      <span>Explore feature</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>





      {/* ─── 5. Security & Trust / How It Works ─── */}
      <section
        id="security"
        className="how-it-works-section py-28 bg-neutral-950 border-t border-neutral-900 relative overflow-hidden scroll-mt-28"
      >
        <div className="absolute inset-0 dot-grid opacity-30 pointer-events-none" />
        <div className="container mx-auto px-4 md:px-8 relative z-10 max-w-7xl">
          {/* Section Header */}
          <div className="text-center mb-20 max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-gsap-green/10 border border-gsap-green/25 text-gsap-green text-xs font-bold uppercase tracking-widest mb-4">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Institutional Grade Security</span>
            </div>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-white mb-5">
              Up and running in{" "}
              <span className="text-gsap-green">60 seconds</span>
            </h2>
            <p className="text-neutral-400 text-base md:text-lg max-w-2xl mx-auto">
              Bank-grade 256-bit encryption with zero stored credentials and 100% read-only account integration.
            </p>
          </div>

          {/* Refined 01, 02, 03 Connected Node Pipeline */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative max-w-6xl mx-auto">
            {/* Glowing Gradient Connector Line */}
            <div className="hidden md:block absolute top-10 left-[18%] right-[18%] h-[2px] bg-gradient-to-r from-gsap-green/20 via-gsap-green/60 to-gsap-green/20 z-0" />

            {howItWorksData.map((step, i) => {
              const timePills = ["~30 Sec Setup", "Instant AI Sync", "Continuous Growth"];
              return (
                <div key={i} className="step-item relative z-10 group flex flex-col items-center text-center">
                  {/* Glowing Node Circle */}
                  <div className="w-20 h-20 rounded-full mb-6 flex items-center justify-center relative group-hover:scale-110 transition-transform duration-300 cursor-default">
                    <div className="absolute inset-0 rounded-full bg-neutral-950 border-2 border-gsap-green/30 group-hover:border-gsap-green group-hover:shadow-[0_0_30px_rgba(136,206,2,0.35)] transition-all duration-300" />
                    <div className="w-12 h-12 rounded-full bg-gsap-green/10 border border-gsap-green/20 flex items-center justify-center relative z-10 group-hover:bg-gsap-green/20 transition-colors">
                      <span className="text-xl font-black text-gsap-green font-mono">{`0${i + 1}`}</span>
                    </div>
                  </div>

                  {/* Clean Content Frame */}
                  <div className="w-full rounded-2xl bg-neutral-900/30 border border-neutral-800/80 hover:border-gsap-green/30 hover:bg-neutral-900/60 p-6 backdrop-blur-sm transition-all duration-300 flex flex-col items-center">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-gsap-green px-2.5 py-0.5 rounded-full bg-gsap-green/10 border border-gsap-green/20 mb-3">
                      {timePills[i]}
                    </span>

                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-gsap-green transition-colors duration-200">
                      {step.title}
                    </h3>
                    <p className="text-neutral-400 text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>




      {/* ─── 6. Reviews / Interactive Customer Spotlight ─── */}
      <TestimonialsSpotlight />



      {/* ─── 7. FAQ Section ─── */}
      <section
        id="faq"
        className="py-28 bg-neutral-950 border-t border-neutral-900 relative overflow-hidden scroll-mt-28"
      >
        <div className="container mx-auto px-4 relative z-10 max-w-4xl">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gsap-green/10 border border-gsap-green/25 text-gsap-green text-xs font-bold uppercase tracking-widest mb-4">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Got Questions?</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
              Frequently Asked <span className="text-gsap-green">Questions</span>
            </h2>
            <p className="text-neutral-400 text-base">
              Everything you need to know about Fintra AI security and features.
            </p>
          </div>

          <div className="space-y-4">
            {faqData.map((faq, i) => (
              <div
                key={i}
                className="faq-item rounded-xl border border-neutral-800 bg-neutral-900/60 overflow-hidden transition-all duration-300 hover:border-neutral-700"
              >
                <button
                  onClick={() => toggleFaq(i)}
                  className="w-full p-6 text-left flex items-center justify-between gap-4 font-bold text-white text-base hover:text-gsap-green transition-colors"
                >
                  <span>{faq.question}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-gsap-green transition-transform duration-300 flex-shrink-0 ${
                      openFaq === i ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-6 text-neutral-400 text-sm leading-relaxed border-t border-neutral-800/60 pt-4">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── 8. CTA Section ─── */}
      <section className="cta-section py-28 bg-black relative overflow-hidden border-t border-neutral-900">
        {/* Glowing ambient background orbs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-gsap-green/10 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute inset-0 dot-grid opacity-30 pointer-events-none" />

        <div className="container mx-auto px-4 md:px-8 relative z-10 max-w-5xl">
          <div className="relative rounded-3xl bg-neutral-950/90 border border-neutral-800/90 p-10 md:p-16 text-center backdrop-blur-2xl shadow-[0_40px_100px_rgba(0,0,0,0.8)] overflow-hidden">
            {/* Glowing top line */}
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-gsap-green to-transparent opacity-80" />

            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gsap-green/10 border border-gsap-green/25 text-gsap-green text-xs font-bold uppercase tracking-widest mb-6">
              ✦ Start for free today
            </div>

            <h2 className="text-4xl sm:text-5xl md:text-6xl font-black text-white mb-6 tracking-tight leading-[1.08] max-w-2xl mx-auto">
              Ready to take control of your{" "}
              <span className="text-gsap-green">financial future?</span>
            </h2>

            <p className="text-neutral-400 font-normal text-base md:text-lg mb-10 max-w-xl mx-auto leading-relaxed">
              Join 50,000+ everyday wealth builders managing their finances smarter with Fintra AI. Setup in under 60 seconds.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
              <Link href="/sign-up">
                <Button

                  size="lg"
                  className="w-full sm:w-auto bg-gsap-green text-black hover:bg-gsap-green/90 font-black text-base px-9 py-6 rounded-xl hover:scale-105 transition-all duration-300 shadow-[0_0_35px_rgba(136,206,2,0.4)]"
                >
                  Start Free Trial
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>

            {/* Checklist */}
            <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-neutral-400 font-mono">
              <span className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-gsap-green" /> No credit card required
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-gsap-green" /> 60-second setup
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-gsap-green" /> Bank-grade 256-bit security
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ─── 9. Footer ─── */}
      <Footer />
    </div>
  );
};




export default LandingPage;
