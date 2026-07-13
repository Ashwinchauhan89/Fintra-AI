"use client";

import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Image from "next/image";
import {
  featuresData,
  howItWorksData,
  statsData,
  testimonialsData,
} from "@/data/landing";
import HeroSection from "@/components/hero";
import Link from "next/link";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const LandingPage = () => {
  const mainRef = useRef(null);

  useGSAP(
    () => {
      // Global Progress Bar
      gsap.to(".progress-bar", {
        scrollTrigger: {
          trigger: document.documentElement,
          start: "top top",
          end: "bottom bottom",
          scrub: 0.3,
        },
        scaleX: 1,
        ease: "none",
        transformOrigin: "left center"
      });

      // Stats Animation
      gsap.from(".stat-item", {
        scrollTrigger: {
          trigger: ".stats-section",
          start: "top 80%",
        },
        y: 30,
        opacity: 0,
        duration: 0.6,
        stagger: 0.2,
      });

      // Horizontal Scroll for Features (Pinning)
      let featureCards = gsap.utils.toArray(".feature-card-wrapper");
      
      gsap.to(featureCards, {
        xPercent: -100 * (featureCards.length - 1),
        ease: "none",
        scrollTrigger: {
          trigger: ".features-scroll-container",
          pin: true,
          scrub: 1,
          snap: 1 / (featureCards.length - 1),
          end: () => "+=" + document.querySelector(".features-scroll-container").offsetWidth
        }
      });

      // How It Works Animation
      gsap.from(".step-item", {
        scrollTrigger: {
          trigger: ".how-it-works-section",
          start: "top 80%",
        },
        x: -50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.3,
      });

      // Testimonials Animation
      gsap.from(".testimonial-card", {
        scrollTrigger: {
          trigger: ".testimonials-section",
          start: "top 80%",
        },
        scale: 0.9,
        opacity: 0,
        duration: 0.6,
        stagger: 0.2,
      });

      // Parallax for CTA shapes
      gsap.to(".cta-shape-1", {
        scrollTrigger: {
          trigger: ".cta-section",
          start: "top bottom",
          end: "bottom top",
          scrub: 1,
        },
        y: -150,
      });

      gsap.to(".cta-shape-2", {
        scrollTrigger: {
          trigger: ".cta-section",
          start: "top bottom",
          end: "bottom top",
          scrub: 1,
        },
        y: 150,
      });
    },
    { scope: mainRef }
  );

  return (
    <div ref={mainRef} className="min-h-screen bg-background text-foreground selection:bg-gsap-green selection:text-black">
      {/* Progress Bar */}
      <div className="progress-bar fixed top-0 left-0 w-full h-1 bg-gsap-green z-[100] scale-x-0"></div>

      {/* Hero Section */}
      <HeroSection />

      {/* Stats Section */}
      <section className="stats-section py-20 bg-neutral-950 border-t border-neutral-900">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {statsData.map((stat, index) => (
              <div key={index} className="stat-item text-center">
                <div className="text-4xl md:text-5xl font-black text-gsap-green mb-2">
                  {stat.value}
                </div>
                <div className="text-neutral-400 font-medium uppercase tracking-wider text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section (Pinned Horizontal Scroll) */}
      <section id="features" className="features-scroll-container h-screen bg-black flex items-center overflow-hidden">
        <div className="container mx-auto px-4 flex-shrink-0 w-full md:w-1/3">
          <h2 className="text-4xl md:text-6xl font-black mb-6 leading-tight">
            Everything you need to <span className="text-gsap-green">manage your finances</span>
          </h2>
          <p className="text-neutral-400 text-lg md:pr-10">Scroll horizontally to explore our powerful AI-driven features designed to keep your wealth growing.</p>
        </div>
        
        <div className="flex h-full items-center pl-10 pr-[50vw]">
          {featuresData.map((feature, index) => (
            <div key={index} className="feature-card-wrapper w-[350px] md:w-[450px] h-[400px] mx-4 flex-shrink-0">
              <Card className="h-full p-8 bg-neutral-900 border-neutral-800 hover:border-gsap-green transition-colors duration-300 flex flex-col justify-center">
                <CardContent className="space-y-6 pt-4">
                  <div className="text-gsap-green scale-150 transform origin-left mb-6">{feature.icon}</div>
                  <h3 className="text-3xl font-bold text-white">{feature.title}</h3>
                  <p className="text-neutral-400 text-lg leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section py-32 bg-neutral-950">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-black text-center mb-24">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-16 md:gap-12 relative">
            {/* Connecting line for desktop */}
            <div className="hidden md:block absolute top-10 left-1/6 right-1/6 h-[2px] bg-neutral-800 z-0 w-2/3 mx-auto"></div>
            
            {howItWorksData.map((step, index) => (
              <div key={index} className="step-item text-center relative z-10">
                <div className="w-24 h-24 bg-neutral-900 text-gsap-green rounded-full flex items-center justify-center mx-auto mb-8 border border-gsap-green shadow-[0_0_40px_rgba(136,206,2,0.15)] text-3xl font-black">
                  {index + 1}
                </div>
                <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
                <p className="text-neutral-400 text-lg px-4">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section py-32 bg-black border-t border-neutral-900">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-black text-center mb-20">
            What Our Users Say
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonialsData.map((testimonial, index) => (
              <Card key={index} className="testimonial-card p-8 bg-neutral-900 border-neutral-800">
                <CardContent className="pt-4 h-full flex flex-col justify-between">
                  <p className="text-neutral-300 text-left italic text-lg leading-relaxed mb-8">"{testimonial.quote}"</p>
                  <div className="flex items-center">
                    <Image
                      src={testimonial.image}
                      alt={testimonial.name}
                      width={56}
                      height={56}
                      className="rounded-full ring-2 ring-gsap-green"
                    />
                    <div className="ml-5 text-left">
                      <div className="font-bold text-lg">{testimonial.name}</div>
                      <div className="text-md text-gsap-green font-medium">
                        {testimonial.role}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section py-32 bg-gsap-green relative overflow-hidden">
        {/* Abstract shapes in the background with parallax class */}
        <div className="absolute top-0 left-0 w-full h-full opacity-20 pointer-events-none">
          <div className="cta-shape-1 absolute top-0 -left-20 w-80 h-80 rounded-full bg-black blur-3xl"></div>
          <div className="cta-shape-2 absolute bottom-0 right-10 w-96 h-96 rounded-full bg-black blur-3xl"></div>
        </div>
        
        <div className="container mx-auto px-4 text-center relative z-10">
          <h2 className="text-5xl md:text-7xl font-black text-black mb-8 tracking-tight">
            Ready to Take Control?
          </h2>
          <p className="text-black/70 font-medium text-xl mb-12 max-w-2xl mx-auto">
            Join thousands of users who are already managing their finances
            smarter with Fintra AI.
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-black text-gsap-green hover:bg-neutral-900 font-black text-xl px-12 py-8 hover:scale-110 transition-transform duration-300 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
            >
              Start Free Trial
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
