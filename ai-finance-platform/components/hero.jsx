"use client";

import React, { useRef, useEffect } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TextPlugin } from "gsap/TextPlugin";
import { GSDevTools } from "@/lib/gsap/GSDevTools";

gsap.registerPlugin(ScrollTrigger, TextPlugin, GSDevTools);

const HeroSection = () => {
  const containerRef = useRef(null);
  const headlineRef = useRef(null);
  const typeTextRef = useRef(null);
  const subheadlineRef = useRef(null);
  const buttonsRef = useRef(null);
  const imageRef = useRef(null);
  const wrapperRef = useRef(null);
  const glow1Ref = useRef(null);
  const glow2Ref = useRef(null);

  useGSAP(
    () => {
      const tl = gsap.timeline();

      // Floating Orbs Animation
      gsap.to(glow1Ref.current, {
        x: "random(-100, 100)",
        y: "random(-100, 100)",
        duration: 8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      gsap.to(glow2Ref.current, {
        x: "random(-150, 150)",
        y: "random(-150, 150)",
        duration: 10,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      // Aggressive Intro animation
      tl.from(headlineRef.current, {
        y: 80,
        rotateX: -90,
        opacity: 0,
        duration: 1.2,
        ease: "elastic.out(1, 0.5)",
      })
        .to(typeTextRef.current, {
          duration: 1.5,
          text: "Intelligence",
          ease: "none",
        })
        .from(
          subheadlineRef.current,
          {
            y: 40,
            opacity: 0,
            duration: 0.8,
            ease: "back.out(1.7)",
          },
          "-=0.6"
        )
        .from(
          buttonsRef.current.children,
          {
            scale: 0.8,
            y: 30,
            opacity: 0,
            duration: 0.6,
            stagger: 0.2,
            ease: "back.out(1.7)",
          },
          "-=0.5"
        );

      // Add GSDevTools to debug the intro timeline
      GSDevTools.create({ animation: tl });
    },
    { scope: containerRef }
  );

  // 3D Mouse Parallax Effect on Image Wrapper
  const handleMouseMove = (e) => {
    if (!wrapperRef.current) return;
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;

    // Calculate rotation between -10 and 10 degrees based on cursor position
    const xPos = (clientX / innerWidth - 0.5) * 20;
    const yPos = (clientY / innerHeight - 0.5) * -20;

    gsap.to(wrapperRef.current, {
      rotationY: xPos,
      rotationX: yPos,
      ease: "power2.out",
      duration: 1
    });
  };

  const handleMouseLeave = () => {
    if (!wrapperRef.current) return;
    gsap.to(wrapperRef.current, {
      rotationY: 0,
      rotationX: 0,
      ease: "power2.out",
      duration: 1
    });
  };

  return (
    <section
      ref={containerRef}
      className="relative pt-40 pb-20 px-4 bg-background text-foreground overflow-hidden"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Background Orbs */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div ref={glow1Ref} className="absolute w-[600px] h-[600px] bg-gsap-green/10 rounded-full blur-[120px] -top-20 -left-20"></div>
        <div ref={glow2Ref} className="absolute w-[500px] h-[500px] bg-[#9cf102]/10 rounded-full blur-[120px] bottom-10 right-20"></div>
      </div>

      <div className="container mx-auto text-center relative z-10">
        <h1 ref={headlineRef} className="text-5xl md:text-8xl lg:text-[105px] pb-6 font-black leading-tight perspective-[1000px] transform-style-3d">
          <span className="text-white block drop-shadow-2xl">Manage Your Finances</span>
          <span className="text-white">with </span>
          <span ref={typeTextRef} className="gradient-title"></span>
          <span className="text-gsap-green animate-pulse">_</span>
        </h1>
        <p ref={subheadlineRef} className="text-xl text-neutral-400 mb-8 max-w-2xl mx-auto drop-shadow-lg">
          An AI-powered financial management platform that helps you track,
          analyze, and optimize your spending with real-time insights.
        </p>
        <div ref={buttonsRef} className="flex justify-center space-x-4 mb-20">
          <Link href="/dashboard">
            <Button size="lg" className="px-8 bg-gsap-green text-black hover:bg-[#9cf102] font-black text-lg hover:shadow-[0_0_30px_rgba(136,206,2,0.6)] hover:scale-105 transition-all duration-300">
              Get Started
            </Button>
          </Link>
          <Link href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank" rel="noopener noreferrer">
            <Button size="lg" variant="outline" className="px-8 border-2 border-gsap-green text-gsap-green hover:bg-gsap-green/10 font-bold text-lg hover:shadow-[0_0_20px_rgba(136,206,2,0.3)] hover:scale-105 transition-all duration-300">
              Watch Demo
            </Button>
          </Link>
        </div>


      </div>
    </section>
  );
};

export default HeroSection;
