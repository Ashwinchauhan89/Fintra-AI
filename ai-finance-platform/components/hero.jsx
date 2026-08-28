"use client";

import React, { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TextPlugin } from "gsap/TextPlugin";
import { Play, X } from "lucide-react";
import { GSDevTools } from "@/lib/gsap/GSDevTools";

gsap.registerPlugin(ScrollTrigger, TextPlugin, GSDevTools);

/* ─────────────────────────────────────────────────────
   Video Modal — animated bg + YouTube embed
───────────────────────────────────────────────────── */
function VideoModal({ onClose }) {
  const YOUTUBE_VIDEO_ID = "ZW0GnrV02e4"; // ← replace with your video ID
  const EMBED_URL = `https://www.youtube.com/embed/${YOUTUBE_VIDEO_ID}?autoplay=1&rel=0&modestbranding=1&color=white`;

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.88)", backdropFilter: "blur(14px)" }}
      onClick={onClose}
    >
      {/* Animated floating orbs behind modal */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-[500px] h-[500px] rounded-full blur-[130px] animate-float-slow"
          style={{
            background: "radial-gradient(circle, rgba(136,206,2,0.2) 0%, transparent 70%)",
            top: "5%", left: "-8%",
          }}
        />
        <div
          className="absolute w-[400px] h-[400px] rounded-full blur-[110px] animate-float"
          style={{
            background: "radial-gradient(circle, rgba(52,211,153,0.15) 0%, transparent 70%)",
            bottom: "5%", right: "-5%", animationDelay: "2.5s",
          }}
        />
        <div
          className="absolute w-[300px] h-[300px] rounded-full blur-[90px] animate-float-slow"
          style={{
            background: "radial-gradient(circle, rgba(163,230,53,0.12) 0%, transparent 70%)",
            top: "40%", right: "20%", animationDelay: "5s",
          }}
        />
        {/* Dot grid */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)",
            backgroundSize: "28px 28px",
          }}
        />
      </div>

      {/* Modal */}
      <div
        className="modal-animate relative w-full max-w-4xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute -top-11 right-0 flex items-center gap-2 text-neutral-400 hover:text-white text-sm font-medium transition-colors group"
        >
          <span>Close</span>
          <span className="w-7 h-7 rounded-full bg-neutral-800 group-hover:bg-neutral-700 flex items-center justify-center transition-colors">
            <X className="w-4 h-4" />
          </span>
        </button>

        {/* Frame */}
        <div className="rounded-2xl overflow-hidden border border-neutral-800 shadow-[0_0_80px_rgba(136,206,2,0.15),0_40px_100px_rgba(0,0,0,0.8)]">
          {/* Browser chrome */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-neutral-900 border-b border-neutral-800">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
              <span className="ml-3 text-xs text-neutral-500 font-mono hidden sm:block">fintra.ai — Platform Demo</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-gsap-green inline-block animate-pulse" />
              <span className="text-gsap-green font-semibold">Live Demo</span>
            </div>
            <div className="w-12" />
          </div>

          {/* YouTube iframe */}
          <div style={{ aspectRatio: "16/9" }}>
            <iframe
              src={EMBED_URL}
              title="Fintra AI Platform Demo"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full bg-black"
              style={{ border: "none", display: "block" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────
   Hero Section
───────────────────────────────────────────────────── */
const HeroSection = () => {
  const containerRef = useRef(null);
  const headlineRef  = useRef(null);
  const typeTextRef  = useRef(null);
  const subRef       = useRef(null);
  const buttonsRef   = useRef(null);
  const previewRef   = useRef(null);
  const glow1Ref     = useRef(null);
  const glow2Ref     = useRef(null);

  const [videoOpen, setVideoOpen] = useState(false);
  const [hoveringPlay, setHoveringPlay] = useState(false);

  useGSAP(() => {
    const tl = gsap.timeline();

    // Floating orbs
    gsap.to(glow1Ref.current, {
      x: "random(-100, 100)", y: "random(-100, 100)",
      duration: 8, repeat: -1, yoyo: true, ease: "sine.inOut",
    });
    gsap.to(glow2Ref.current, {
      x: "random(-150, 150)", y: "random(-150, 150)",
      duration: 10, repeat: -1, yoyo: true, ease: "sine.inOut",
    });

    // Entrance — sequential timeline
    tl.from(headlineRef.current, {
      y: 80, rotateX: -90, opacity: 0,
      duration: 1.2, ease: "elastic.out(1, 0.5)",
    })
      .to(typeTextRef.current, { duration: 1.5, text: "Intelligence", ease: "none" })
      .from(subRef.current, { y: 40, opacity: 0, duration: 0.8, ease: "back.out(1.7)" }, "-=0.6")
      .from(buttonsRef.current?.children, {
        scale: 0.8, y: 30, opacity: 0,
        duration: 0.6, stagger: 0.2, ease: "back.out(1.7)",
      }, "-=0.5")
      .from(previewRef.current, {
        y: 60,
        scale: 0.94,
        opacity: 0,
        duration: 0.9,
        ease: "power3.out",
      }, "+=0.1");

    // Auto-hide the GSDevTools bar when the intro animation completes
    tl.eventCallback("onComplete", () => {
      // Small delay so user can see it finish, then hide
      gsap.delayedCall(0.5, () => {
        const bar = document.querySelector("#gs-dev-tools");
        if (bar) {
          gsap.to(bar, { opacity: 0, duration: 0.4, onComplete: () => { bar.style.display = "none"; } });
        }
      });
    });

    GSDevTools.create({ animation: tl });
  }, { scope: containerRef });

  // Hide GSDevTools ONLY when user scrolls past the hero section
  useEffect(() => {
    const STYLE_ID = "gsdevtools-hide-style";

    const hideViaCSS = () => {
      if (document.getElementById(STYLE_ID)) return;
      const style = document.createElement("style");
      style.id = STYLE_ID;
      // Fade out
      style.textContent = `.gs-dev-tools { opacity: 0 !important; pointer-events: none !important; transition: opacity 0.4s ease !important; }`;
      document.head.appendChild(style);
      // Then fully remove from layout
      setTimeout(() => {
        const s = document.getElementById(STYLE_ID);
        if (s) s.textContent = `.gs-dev-tools { display: none !important; }`;
      }, 450);
    };

    const showViaCSS = () => {
      document.getElementById(STYLE_ID)?.remove();
    };

    const onScroll = () => {
      if (!containerRef.current) return;
      // Hide when the bottom of the hero section scrolls off the viewport
      const heroBottom = containerRef.current.getBoundingClientRect().bottom;
      if (heroBottom <= 0) {
        hideViaCSS();
      } else {
        showViaCSS(); // restore if user scrolls back up
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      document.getElementById(STYLE_ID)?.remove();
    };
  }, []);



  return (
    <>
      <section
        ref={containerRef}
        className="relative pt-16 md:pt-24 pb-16 px-4 bg-background text-foreground overflow-hidden"
      >
        {/* Background orbs */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <div ref={glow1Ref} className="absolute w-[600px] h-[600px] bg-gsap-green/10 rounded-full blur-[120px] -top-20 -left-20" />
          <div ref={glow2Ref} className="absolute w-[500px] h-[500px] bg-[#9cf102]/10 rounded-full blur-[120px] bottom-10 right-20" />
        </div>

        <div className="container mx-auto text-center relative z-10">

          {/* Headline */}
          <div className="overflow-hidden">
          <h1
            ref={headlineRef}
            className="text-4xl sm:text-5xl md:text-8xl lg:text-[105px] pb-6 font-black leading-tight perspective-[1000px] transform-style-3d"
          >
            <span className="text-white block drop-shadow-2xl">Manage Your Finances</span>
            <span className="text-white">with </span>
            <span ref={typeTextRef} className="gradient-title" />
            <span className="text-gsap-green animate-pulse">_</span>
          </h1>
          </div>

          {/* Subheadline */}
          <p ref={subRef} className="text-xl text-neutral-400 mb-8 max-w-2xl mx-auto drop-shadow-lg">
            An AI-powered financial management platform that helps you track,
            analyze, and optimize your spending with real-time insights.
          </p>

          {/* Buttons */}
          <div ref={buttonsRef} className="flex justify-center items-center gap-4 mb-12">
            {/* Get Started */}
            <Link href="/sign-up">
              <Button
                size="lg"
                className="px-8 bg-gsap-green text-black hover:bg-[#9cf102] font-black text-lg hover:shadow-[0_0_30px_rgba(136,206,2,0.6)] hover:scale-105 transition-all duration-300"
              >
                Get Started
              </Button>
            </Link>


            {/* Play button — shows "Watch Demo" label on hover */}
            <button
              onClick={() => setVideoOpen(true)}
              onMouseEnter={() => setHoveringPlay(true)}
              onMouseLeave={() => setHoveringPlay(false)}
              className="relative flex items-center gap-3 group"
              aria-label="Watch Demo"
            >
              {/* Circle play button */}
              <div className="relative w-14 h-14 flex-shrink-0">
                {/* Ping ring */}
                <div className="absolute inset-0 rounded-full border-2 border-gsap-green/40 scale-110 group-hover:scale-125 group-hover:opacity-0 transition-all duration-500" />
                {/* Outer glow */}
                <div className="absolute inset-0 rounded-full bg-gsap-green/10 group-hover:bg-gsap-green/20 transition-colors duration-300 blur-sm" />
                {/* Main circle */}
                <div className="absolute inset-0 rounded-full border-2 border-gsap-green bg-black group-hover:bg-gsap-green group-hover:shadow-[0_0_30px_rgba(136,206,2,0.6)] transition-all duration-300 flex items-center justify-center">
                  <Play className="w-5 h-5 text-gsap-green group-hover:text-black fill-gsap-green group-hover:fill-black transition-colors duration-300 ml-0.5" />
                </div>
              </div>

              {/* "Watch Demo" label — slides in on hover */}
              <span
                className="text-base font-bold text-white transition-all duration-300 whitespace-nowrap overflow-hidden"
                style={{
                  maxWidth: hoveringPlay ? "140px" : "0px",
                  opacity: hoveringPlay ? 1 : 0,
                  transition: "max-width 0.35s ease, opacity 0.25s ease",
                }}
              >
                Watch Demo
              </span>
            </button>
          </div>

          {/* ── Product Preview Card ── */}
          <div ref={previewRef} className="relative mx-auto max-w-3xl w-full mb-4">
            {/* Glow behind card */}
            <div className="absolute -inset-px rounded-2xl bg-gsap-green/10 blur-2xl pointer-events-none" />
            {/* Card shell */}
            <div className="relative rounded-2xl border border-neutral-800 bg-neutral-950/90 overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.7)]">
              {/* Browser chrome bar */}
              <div className="flex items-center justify-between px-4 py-2.5 bg-neutral-900 border-b border-neutral-800">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-red-500/70" />
                  <span className="w-3 h-3 rounded-full bg-amber-500/70" />
                  <span className="w-3 h-3 rounded-full bg-emerald-500/70" />
                  <span className="ml-3 text-xs text-neutral-500 font-mono hidden sm:block">fintra.ai/dashboard</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-gsap-green animate-pulse" />
                  <span className="text-gsap-green font-semibold">Live</span>
                </div>
                <div className="w-12" />
              </div>

              {/* Dashboard content */}
              <div className="p-4 sm:p-6 grid grid-cols-3 gap-3 sm:gap-4">
                {/* Metric cards */}
                {[
                  { label: "Net Worth", value: "$84,320", delta: "+12.4%", up: true },
                  { label: "Monthly Savings", value: "$3,210", delta: "+8.1%", up: true },
                  { label: "Spending", value: "$1,840", delta: "-3.2%", up: false },
                ].map((m) => (
                  <div key={m.label} className="rounded-xl bg-neutral-900 border border-neutral-800 p-3 sm:p-4">
                    <p className="text-neutral-500 text-[10px] sm:text-xs uppercase tracking-widest mb-1 font-semibold">{m.label}</p>
                    <p className="text-white font-black text-base sm:text-xl tabular-nums">{m.value}</p>
                    <p className={`text-xs font-bold mt-1 ${m.up ? "text-gsap-green" : "text-red-400"}`}>{m.delta}</p>
                  </div>
                ))}
              </div>

              {/* High-Tech Spline Area Graph */}
              <div className="px-4 sm:px-6 pb-4 sm:pb-6">
                <div className="rounded-xl bg-neutral-900/90 border border-neutral-800 p-4 sm:p-5 relative overflow-hidden group">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-bold text-sm">Spending Overview</span>
                      <span className="px-2 py-0.5 rounded-full bg-gsap-green/10 text-gsap-green text-[10px] font-mono font-bold">
                        -14.2% AI Optimized
                      </span>
                    </div>
                    <span className="text-neutral-500 text-xs font-mono">Last 6 months</span>
                  </div>

                  {/* SVG Line & Area Graph */}
                  <div className="relative h-28 sm:h-32 w-full">
                    {/* Background horizontal grid lines */}
                    <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                      <div className="border-b border-dashed border-neutral-600 w-full" />
                      <div className="border-b border-dashed border-neutral-600 w-full" />
                      <div className="border-b border-dashed border-neutral-600 w-full" />
                    </div>

                    <svg className="w-full h-full overflow-visible" viewBox="0 0 500 120" preserveAspectRatio="none">
                      <defs>
                        <linearGradient id="heroGraphGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#88CE02" stopOpacity="0.45" />
                          <stop offset="60%" stopColor="#88CE02" stopOpacity="0.12" />
                          <stop offset="100%" stopColor="#88CE02" stopOpacity="0" />
                        </linearGradient>
                        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                          <feGaussianBlur stdDeviation="4" result="blur" />
                          <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                      </defs>

                      {/* Gradient Fill Area */}
                      <path
                        d="M 0,90 Q 50,75 100,55 T 200,68 T 300,35 T 400,48 T 500,18 L 500,120 L 0,120 Z"
                        fill="url(#heroGraphGradient)"
                      />

                      {/* Main Smooth Glowing Line */}
                      <path
                        d="M 0,90 Q 50,75 100,55 T 200,68 T 300,35 T 400,48 T 500,18"
                        fill="none"
                        stroke="#88CE02"
                        strokeWidth="3"
                        strokeLinecap="round"
                        filter="url(#glow)"
                      />

                      {/* Data Points */}
                      {[
                        { cx: 0, cy: 90, val: "$2.9k" },
                        { cx: 100, cy: 55, val: "$3.4k" },
                        { cx: 200, cy: 68, val: "$3.1k" },
                        { cx: 300, cy: 35, val: "$4.2k" },
                        { cx: 400, cy: 48, val: "$3.6k" },
                        { cx: 500, cy: 18, val: "$1.8k" },
                      ].map((pt, idx) => (
                        <g key={idx} className="cursor-pointer group/point">
                          <circle
                            cx={pt.cx}
                            cy={pt.cy}
                            r="4.5"
                            className="fill-neutral-950 stroke-gsap-green stroke-2 transition-all duration-200 group-hover/point:r-6 group-hover/point:fill-gsap-green"
                          />
                          {idx === 5 && (
                            <circle
                              cx={pt.cx}
                              cy={pt.cy}
                              r="9"
                              className="fill-none stroke-gsap-green stroke-1 animate-ping origin-center"
                            />
                          )}
                        </g>
                      ))}
                    </svg>
                  </div>

                  {/* Month labels */}
                  <div className="flex justify-between mt-3 text-[11px] font-mono text-neutral-500">
                    {["Mar", "Apr", "May", "Jun", "Jul", "Aug"].map((m, i) => (
                      <span key={m} className={`flex-1 text-center ${i === 5 ? "text-gsap-green font-bold" : ""}`}>
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* Video Modal */}
      {videoOpen && <VideoModal onClose={() => setVideoOpen(false)} />}
    </>
  );
};

export default HeroSection;
