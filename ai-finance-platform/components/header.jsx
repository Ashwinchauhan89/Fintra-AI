import React from "react";
import { Button } from "./ui/button";
import { PenBox, LayoutDashboard, Sparkles } from "lucide-react";
import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { checkUser } from "@/lib/checkUser";
import Image from "next/image";

const Header = async () => {
  const isClerkConfigured =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("ZXhhbXBs");

  if (isClerkConfigured) {
    await checkUser();
  }

  return (
    <header className="fixed top-4 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none transition-all duration-300">
      <nav className="w-full max-w-6xl bg-white/[0.09] hover:bg-white/[0.12] backdrop-blur-2xl border border-white/[0.18] rounded-full px-5 py-2.5 flex items-center justify-between shadow-[0_16px_40px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.2)] pointer-events-auto transition-all duration-300">
        <Link href="/" className="flex items-center group">
          <div className="relative w-10 h-10 rounded-full overflow-hidden flex items-center justify-center border border-white/20 shadow-inner bg-black group-hover:scale-105 transition-transform">
            <Image
              src="/logo.png"
              alt="Fintra AI Logo"
              width={40}
              height={40}
              className="object-cover w-full h-full"
              priority
            />
          </div>
        </Link>



        {/* Navigation Links */}
        <div className="hidden md:flex items-center space-x-8 text-sm font-medium">
          <Link
            href="/#fintech-studio"
            className="text-neutral-200 hover:text-white transition-colors"
          >
            Interactive Studio
          </Link>
          <Link
            href="/#features"
            className="text-neutral-300 hover:text-white transition-colors"
          >
            Features
          </Link>
          <Link
            href="/#security"
            className="text-neutral-300 hover:text-white transition-colors"
          >
            Security & Trust
          </Link>
          <Link
            href="/#testimonials"
            className="text-neutral-300 hover:text-white transition-colors"
          >
            Reviews
          </Link>
          <Link
            href="/#faq"
            className="text-neutral-300 hover:text-white transition-colors"
          >
            FAQ
          </Link>
        </div>


        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          {isClerkConfigured ? (
            <>
              <SignedIn>
                <Link
                  href="/dashboard"
                  className="text-neutral-200 hover:text-[#88CE02] flex items-center gap-2 transition-colors"
                >
                  <Button
                    variant="outline"
                    className="border-white/20 hover:border-white/40 hover:text-white hover:bg-white/10 font-bold text-white bg-white/5"
                  >
                    <LayoutDashboard size={18} />
                    <span className="hidden md:inline">Dashboard</span>
                  </Button>
                </Link>
                <Link href="/transaction/create">
                  <Button className="flex items-center gap-2 bg-[#88CE02] text-black hover:bg-lime-400 font-extrabold shadow-[0_0_20px_rgba(136,206,2,0.3)]">
                    <PenBox size={18} />
                    <span className="hidden md:inline">Add Transaction</span>
                  </Button>
                </Link>
              </SignedIn>
              <SignedOut>
                <SignInButton forceRedirectUrl="/dashboard">
                  <Button
                    variant="outline"
                    className="border-white/20 text-white hover:text-white hover:border-white/40 hover:bg-white/10 font-bold px-5 bg-white/5"
                  >
                    Login
                  </Button>
                </SignInButton>
                <Link href="/sign-up">
                  <Button className="bg-[#88CE02] text-black hover:bg-lime-400 font-extrabold px-5 shadow-[0_0_20px_rgba(136,206,2,0.3)]">
                    Start Free
                  </Button>
                </Link>
              </SignedOut>
              <SignedIn>
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "w-10 h-10 border-2 border-[#88CE02]",
                    },
                  }}
                />
              </SignedIn>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Link href="/sign-in">
                <Button
                  variant="outline"
                  className="border-white/20 text-white hover:text-white hover:border-white/40 hover:bg-white/10 font-bold px-5 bg-white/5"
                >
                  Login
                </Button>
              </Link>
              <Link href="/sign-up">
                <Button className="bg-[#88CE02] text-black hover:bg-lime-400 font-extrabold px-5 shadow-[0_0_20px_rgba(136,206,2,0.3)]">
                  Start Free
                </Button>
              </Link>
            </div>
          )}

        </div>
      </nav>
    </header>
  );
};

export default Header;
