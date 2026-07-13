"use client";

import React, { useRef } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TextPlugin } from "gsap/TextPlugin";

gsap.registerPlugin(ScrollTrigger, TextPlugin);

const HeroSection = () => {
  const containerRef = useRef(null);
  const headlineRef = useRef(null);
  const typeTextRef = useRef(null);
  const subheadlineRef = useRef(null);
  const buttonsRef = useRef(null);
  const imageRef = useRef(null);

  useGSAP(
    () => {
      const tl = gsap.timeline();

      // Intro animation
      tl.from(headlineRef.current, {
        y: 50,
        opacity: 0,
        duration: 0.8,
        ease: "power4.out",
      })
        .to(typeTextRef.current, {
          duration: 1.5,
          text: "Intelligence",
          ease: "none",
        })
        .from(
          subheadlineRef.current,
          {
            y: 30,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out",
          },
          "-=0.4"
        )
        .from(
          buttonsRef.current.children,
          {
            y: 20,
            opacity: 0,
            duration: 0.6,
            stagger: 0.2,
            ease: "power2.out",
          },
          "-=0.4"
        );

      // Scroll animation for image
      gsap.fromTo(
        imageRef.current,
        {
          rotateX: 15,
          scale: 0.9,
          y: 50,
        },
        {
          rotateX: 0,
          scale: 1,
          y: 0,
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 20%",
            end: "bottom top",
            scrub: 1,
          },
        }
      );
    },
    { scope: containerRef }
  );

  return (
    <section ref={containerRef} className="pt-40 pb-20 px-4 bg-background text-foreground overflow-hidden">
      <div className="container mx-auto text-center">
        <h1 ref={headlineRef} className="text-5xl md:text-8xl lg:text-[105px] pb-6 font-black leading-tight">
          <span className="text-white">Manage Your Finances <br /> with </span>
          <span ref={typeTextRef} className="gradient-title"></span>
          <span className="text-gsap-green animate-pulse">_</span>
        </h1>
        <p ref={subheadlineRef} className="text-xl text-neutral-400 mb-8 max-w-2xl mx-auto">
          An AI-powered financial management platform that helps you track,
          analyze, and optimize your spending with real-time insights.
        </p>
        <div ref={buttonsRef} className="flex justify-center space-x-4 mb-16">
          <Link href="/dashboard">
            <Button size="lg" className="px-8 bg-gsap-green text-black hover:bg-[#9cf102] font-bold">
              Get Started
            </Button>
          </Link>
          <Link href="https://www.youtube.com/roadsidecoder">
            <Button size="lg" variant="outline" className="px-8 border-gsap-green text-gsap-green hover:bg-gsap-green/10 font-bold">
              Watch Demo
            </Button>
          </Link>
        </div>
        <div className="hero-image-wrapper mt-5 md:mt-0 perspective-[1000px]">
          <div ref={imageRef} className="hero-image rounded-xl border border-neutral-800 shadow-[0_0_50px_rgba(136,206,2,0.1)]">
            <Image
              src="/banner.png"
              width={1280}
              height={720}
              alt="Dashboard Preview"
              className="rounded-lg mx-auto"
              priority
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
