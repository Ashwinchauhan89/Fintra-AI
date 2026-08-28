"use client";

import React, { useState } from "react";
import { SignUp } from "@clerk/nextjs";
import Link from "next/link";
import Image from "next/image";
import { ArrowRight, Lock, Mail, User, ShieldCheck, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SignUpPage() {
  const isClerkConfigured =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("ZXhhbXBs");

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (isClerkConfigured) {
    return <SignUp />;
  }

  // Beautiful interactive FinTech sign-up UI for design preview & immediate testing
  return (
    <div className="w-full rounded-3xl bg-neutral-950/90 border border-neutral-800 p-8 sm:p-10 backdrop-blur-2xl shadow-[0_30px_90px_rgba(0,0,0,0.8)] relative overflow-hidden">
      {/* Glowing top line */}
      <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-[#88CE02] to-transparent opacity-80" />

      {/* Header with circular logo */}
      <div className="text-center mb-8">
        <Link href="/" className="inline-block mb-4 group">
          <div className="w-12 h-12 rounded-full overflow-hidden border border-white/20 shadow-inner bg-black flex items-center justify-center mx-auto group-hover:scale-105 transition-transform">
            <Image
              src="/logo.png"
              alt="Fintra AI"
              width={48}
              height={48}
              className="object-cover w-full h-full"
            />
          </div>
        </Link>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Create your account
        </h1>
        <p className="text-neutral-400 text-xs sm:text-sm mt-1.5">
          Start mastering your finances with AI intelligence
        </p>
      </div>

      {/* Google OAuth Button */}
      <Link href="/dashboard" className="w-full block mb-5">
        <button
          type="button"
          className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-neutral-900 border border-neutral-750 text-white font-semibold text-sm hover:bg-neutral-850 hover:border-neutral-600 transition-all duration-200"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#EA4335"
              d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"
            />
            <path
              fill="#4285F4"
              d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
            />
            <path
              fill="#FBBC05"
              d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12.3 0 15.1s.7 5.4 1.9 7.8l3.7-2.9c0-.4 0-.8 0-1.2z"
            />
            <path
              fill="#34A853"
              d="M12 23.5c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.4-6.4-5.2L1.9 16.5C3.7 20.2 7.5 23.5 12 23.5z"
            />
          </svg>
          Sign up with Google
        </button>
      </Link>

      {/* Divider */}
      <div className="relative flex items-center justify-center mb-5">
        <div className="border-t border-neutral-800 w-full" />
        <span className="bg-neutral-950 px-3 text-[11px] font-mono text-neutral-500 uppercase tracking-wider relative z-10">
          or sign up with email
        </span>
      </div>

      {/* Form */}
      <form onSubmit={(e) => { e.preventDefault(); window.location.href = "/dashboard"; }} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-neutral-300 mb-1.5">
            Full name
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Alex Morgan"
              required
              className="w-full bg-neutral-900 border border-neutral-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:outline-none focus:border-[#88CE02] transition-colors"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-neutral-300 mb-1.5">
            Email address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              className="w-full bg-neutral-900 border border-neutral-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:outline-none focus:border-[#88CE02] transition-colors"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-neutral-300 mb-1.5">
            Password
          </label>
          <div className="relative">
            <Lock className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create strong password"
              required
              className="w-full bg-neutral-900 border border-neutral-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:outline-none focus:border-[#88CE02] transition-colors"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 pt-1 text-xs text-neutral-400">
          <Check className="w-3.5 h-3.5 text-[#88CE02]" />
          <span>No credit card required. Free 14-day trial.</span>
        </div>

        <Link href="/dashboard" className="block pt-2">
          <Button
            type="submit"
            className="w-full bg-[#88CE02] text-black hover:bg-[#88CE02]/90 font-extrabold text-sm py-6 rounded-xl shadow-[0_0_25px_rgba(136,206,2,0.35)] transition-all hover:scale-[1.02]"
          >
            Create Free Account
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </Link>
      </form>

      {/* Footer link */}
      <div className="text-center mt-6 text-xs text-neutral-400">
        Already have an account?{" "}
        <Link href="/sign-in" className="text-[#88CE02] font-bold hover:underline">
          Log in
        </Link>
      </div>

      <div className="mt-6 pt-4 border-t border-neutral-900 text-center flex items-center justify-center gap-1.5 text-[11px] text-neutral-500 font-mono">
        <ShieldCheck className="w-3.5 h-3.5 text-[#88CE02]" />
        <span>Bank-Grade 256-Bit Security</span>
      </div>
    </div>
  );
}
