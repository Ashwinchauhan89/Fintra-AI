"use client";

import React, { useRef, useEffect } from "react";
import { usePathname } from "next/navigation";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ScrollSmoother } from "@/lib/gsap/ScrollSmoother";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, ScrollSmoother, useGSAP);
}

export default function SmoothScroll({ children }) {
  const smoother = useRef(null);
  const pathname = usePathname();

  // Clear hash on initial page load so refreshes start at the top
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Reset scroll restoration so refresh starts at top
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }

    const hash = window.location.hash;
    if (hash) {
      // Clean hash from URL bar so subsequent refreshes stay at the top
      window.history.replaceState(null, "", window.location.pathname);
    }
  }, []);

  // Handle cross-page navigation with hash
  useEffect(() => {
    if (typeof window === "undefined") return;
    const hash = window.location.hash;
    if (hash && smoother.current) {
      const targetElement = document.querySelector(hash);
      if (targetElement) {
        setTimeout(() => {
          if (smoother.current) {
            smoother.current.scrollTo(targetElement, true, "top 110px");
          }
          // Clean the hash so refreshing won't lock user to the section
          window.history.replaceState(null, "", window.location.pathname);
        }, 300);
      }
    }
  }, [pathname]);

  useGSAP(() => {
    smoother.current = ScrollSmoother.create({
      wrapper: "#smooth-wrapper",
      content: "#smooth-content",
      smooth: 1.2,
      effects: true,
      normalizeScroll: false,
      ignoreMobileResize: true,
    });

    const handleAnchorClick = (e) => {
      const anchor = e.target.closest('a[href*="#"]');
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (!href) return;

      const hashIndex = href.indexOf("#");
      if (hashIndex !== -1) {
        const hash = href.slice(hashIndex);
        const path = href.slice(0, hashIndex);

        // If we are currently on the homepage, smoothly scroll without polluting the URL hash
        if (window.location.pathname === "/" && (path === "" || path === "/")) {
          const targetElement = document.querySelector(hash);
          if (targetElement && smoother.current) {
            e.preventDefault();
            smoother.current.scrollTo(targetElement, true, "top 110px");
          }
        }
      }
    };

    document.addEventListener("click", handleAnchorClick);
    return () => {
      document.removeEventListener("click", handleAnchorClick);
    };
  }, []);

  return (
    <div id="smooth-wrapper">
      <div id="smooth-content">{children}</div>
    </div>
  );
}
