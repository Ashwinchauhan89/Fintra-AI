import React from "react";
import { Button } from "./ui/button";
import { PenBox, LayoutDashboard } from "lucide-react";
import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { checkUser } from "@/lib/checkUser";
import Image from "next/image";

const Header = async () => {
  await checkUser();

  return (
    <header className="fixed top-0 w-full bg-black/80 backdrop-blur-md z-50 border-b border-neutral-800">
      <nav className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/">
          <Image
            src={"/logo.png"}
            alt="Fintra - AI Logo"
            width={200}
            height={60}
            className="h-12 w-auto object-contain brightness-0 invert"
          />
        </Link>

        {/* Navigation Links - Different for signed in/out users */}
        <div className="hidden md:flex items-center space-x-8">
          <SignedOut>
            <a href="#features" className="text-neutral-400 hover:text-gsap-green font-medium transition-colors">
              Features
            </a>
            <a
              href="#testimonials"
              className="text-neutral-400 hover:text-gsap-green font-medium transition-colors"
            >
              Testimonials
            </a>
          </SignedOut>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-4">
          <SignedIn>
            <Link
              href="/dashboard"
              className="text-neutral-400 hover:text-gsap-green flex items-center gap-2 transition-colors"
            >
              <Button variant="outline" className="border-neutral-700 hover:border-gsap-green hover:text-gsap-green hover:bg-gsap-green/10">
                <LayoutDashboard size={18} />
                <span className="hidden md:inline">Dashboard</span>
              </Button>
            </Link>
            <Link href="/transaction/create">
              <Button className="flex items-center gap-2 bg-gsap-green text-black hover:bg-[#9cf102] font-bold">
                <PenBox size={18} />
                <span className="hidden md:inline">Add Transaction</span>
              </Button>
            </Link>
          </SignedIn>
          <SignedOut>
            <SignInButton forceRedirectUrl="/dashboard">
              <Button variant="outline" className="border-neutral-700 text-neutral-300 hover:text-gsap-green hover:border-gsap-green hover:bg-gsap-green/10">
                Login
              </Button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-10 h-10 border-2 border-gsap-green",
                },
              }}
            />
          </SignedIn>
        </div>
      </nav>
    </header>
  );
};

export default Header;
