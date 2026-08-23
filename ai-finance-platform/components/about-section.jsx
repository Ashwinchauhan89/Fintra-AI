"use client";

import React, { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { 
  Cloud, 
  BookOpen, 
  Send, 
  Activity, 
  Globe, 
  ShieldCheck 
} from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

const companies = [
  { name: "Cloud", icon: Cloud },
  { name: "GITBOOK", icon: BookOpen },
  { name: "Resend", icon: Send },
  { name: "AVOCA", icon: Activity },
  { name: "Tripadvisor", icon: Globe },
  { name: "BÆRSKIN", icon: ShieldCheck },
  // Duplicate for infinite scroll effect
  { name: "Cloud", icon: Cloud },
  { name: "GITBOOK", icon: BookOpen },
  { name: "Resend", icon: Send },
  { name: "AVOCA", icon: Activity },
  { name: "Tripadvisor", icon: Globe },
  { name: "BÆRSKIN", icon: ShieldCheck },
];

const AboutSection = () => {
  const sectionRef = useRef(null);
  const textRef = useRef(null);
  const marqueeRef = useRef(null);

  useGSAP(
    () => {
      // Infinite Marquee Animation
      gsap.to(marqueeRef.current, {
        xPercent: -50,
        ease: "none",
        duration: 20,
        repeat: -1,
      });

      // Text Reveal Animation on Scroll
      const lines = gsap.utils.toArray(".about-text-line");
      
      gsap.from(lines, {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 85%",
          end: "center center",
          scrub: 1,
        },
        y: 40,
        opacity: 0,
        rotationX: -45,
        stagger: 0.2,
        transformOrigin: "left center",
        ease: "power2.out"
      });
      
      // Subtle background particle/texture movement
      gsap.to(".about-texture", {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top bottom",
          end: "bottom top",
          scrub: 2,
        },
        y: 150,
        rotation: 15,
        opacity: 0.4
      });
    },
    { scope: sectionRef }
  );

  return (
    <section ref={sectionRef} className="py-32 bg-black relative overflow-hidden border-t border-neutral-900">
      
      {/* Background Texture/Glow simulating the particle effect in the image */}
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1/2 h-full pointer-events-none opacity-20">
        <div className="about-texture absolute -right-20 top-0 w-[600px] h-[600px] bg-gradient-to-tr from-gsap-green/20 to-transparent rounded-full blur-[100px]"></div>
        {/* Simulating a subtle dotted texture */}
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        
        {/* Trusted By / Marquee Section */}
        <div className="mb-40 overflow-hidden relative">
          {/* Fade edges */}
          <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none"></div>
          <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none"></div>
          
          <div ref={marqueeRef} className="flex whitespace-nowrap items-center w-[200%]">
            {companies.map((company, i) => (
              <div key={i} className="flex items-center justify-center gap-2 w-1/6 text-neutral-500 hover:text-white transition-colors duration-300">
                <company.icon size={28} />
                <span className="font-bold text-2xl tracking-wide">{company.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Large Typography About Section */}
        <div ref={textRef} className="max-w-5xl mx-auto md:mx-0 perspective-[1000px]">
          <div className="text-4xl md:text-6xl lg:text-7xl font-medium tracking-tight text-white leading-[1.15]">
            <div className="about-text-line transform-style-3d">
              How you manage finances will change.
            </div>
            <div className="about-text-line text-neutral-500 transform-style-3d mb-8">
              How you track them shouldn&apos;t.
            </div>
            <div className="about-text-line transform-style-3d text-3xl md:text-5xl lg:text-6xl text-neutral-300 leading-tight">
              Fintra AI moves predictive intelligence and
            </div>
            <div className="about-text-line transform-style-3d text-3xl md:text-5xl lg:text-6xl text-neutral-300 leading-tight">
              automated reporting out of complex spreadsheets
            </div>
            <div className="about-text-line transform-style-3d text-3xl md:text-5xl lg:text-6xl text-neutral-300 leading-tight">
              and into a unified dashboard, so what you plan today
            </div>
            <div className="about-text-line transform-style-3d text-3xl md:text-5xl lg:text-6xl text-neutral-300 leading-tight">
              scales effortlessly for tomorrow.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};




export default AboutSection;
