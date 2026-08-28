import React from "react";
import Link from "next/link";
import Image from "next/image";

const Footer = () => {
  return (
    <footer className="bg-black relative overflow-hidden border-t border-neutral-900 pt-20 pb-10 text-sm">
      {/* Background Texture */}
      <div className="absolute inset-0 pointer-events-none opacity-20" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.15) 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
      
      <div className="container mx-auto px-6 relative z-10 max-w-6xl">
        
        {/* Status Badge */}
        <div className="mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-neutral-900/80 border border-neutral-800 text-neutral-300 shadow-sm cursor-pointer hover:bg-neutral-800 transition-colors">
            <div className="w-2 h-2 rounded-full bg-gsap-green animate-pulse"></div>
            <span className="font-medium">All systems operational</span>
          </div>
        </div>

        {/* Footer Links Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-8 mb-20">
          
          {/* Column 1 */}
          <div className="flex flex-col gap-10">
            <div>
              <h3 className="text-white font-semibold text-lg tracking-tight mb-5">Platform</h3>
              <ul className="space-y-4 text-neutral-400 font-medium">
                <li><Link href="#" className="hover:text-white transition-colors">Predictive Analytics</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Automated Reporting</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Portfolio Tracker</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Smart Alerts</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg tracking-tight mb-5">Company</h3>
              <ul className="space-y-4 text-neutral-400 font-medium">
                <li><Link href="#" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Contact Us</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Changelog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Support</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
          </div>

          {/* Column 2 */}
          <div className="flex flex-col gap-10">
            <div>
              <h3 className="text-white font-semibold text-lg tracking-tight mb-5">Use cases</h3>
              <ul className="space-y-4 text-neutral-400 font-medium">
                <li><Link href="#" className="hover:text-white transition-colors">Personal Finance</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Startup Burn Rate</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Crypto Tracking</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Tax Preparation</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg tracking-tight mb-5">Community</h3>
              <ul className="space-y-4 text-neutral-400 font-medium">
                <li><Link href="#" className="hover:text-white transition-colors">X (Twitter)</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Github</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Discord</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">LinkedIn</Link></li>
              </ul>
            </div>
          </div>

          {/* Column 3 */}
          <div className="flex flex-col gap-10">
            <div>
              <h3 className="text-white font-semibold text-lg tracking-tight mb-5">Resources</h3>
              <ul className="space-y-4 text-neutral-400 font-medium">
                <li><Link href="#" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Docs</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Fintra vs. Spreadsheets</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">API Reference</Link></li>
              </ul>
            </div>
            
            {/* Brand Logo & Compliance Info */}
            <div className="mt-4 flex items-center gap-4">
              <div className="w-14 h-14 rounded-full overflow-hidden border border-white/20 shadow-inner bg-black flex items-center justify-center flex-shrink-0 hover:scale-105 transition-transform">
                <Image
                  src="/logo.png"
                  alt="Fintra AI Logo"
                  width={56}
                  height={56}
                  className="object-cover w-full h-full"
                />
              </div>
              <div>
                <span className="font-bold text-white text-sm block">Fintra AI</span>
                <p className="text-xs text-neutral-400 max-w-[180px] font-medium leading-relaxed">
                  SOC 2 Type II certified & bank-grade 256-bit encrypted.
                </p>
              </div>
            </div>

          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-neutral-800/80 flex flex-col md:flex-row justify-between items-center gap-4 text-neutral-500 font-medium">
          <p>© {new Date().getFullYear()} Fintra AI Inc. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <span>|</span>
            <Link href="#" className="hover:text-white transition-colors">Terms</Link>
            <span>|</span>
            <Link href="#" className="hover:text-white transition-colors">Security</Link>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
