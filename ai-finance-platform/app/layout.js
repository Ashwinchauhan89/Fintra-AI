import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";
import { ClerkProvider } from "@clerk/nextjs";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/theme-provider";
import SmoothScroll from "@/components/smooth-scroll";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Fintra - AI",
  description: "One stop Finance Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
        <head>
          <link rel="icon" href="/logo-sm.png" sizes="any" />
        </head>
        <body className={`${inter.className}`}>
          <ClerkProvider>
            <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem
            disableTransitionOnChange
          >
            <Header />
            <SmoothScroll>
              <main className="min-h-screen pt-24">{children}</main>
              
              <footer className="bg-blue-50 py-12 dark:bg-background border-t">
                <div className="container mx-auto px-4 text-center text-gray-600 dark:text-gray-400">
                  <p>Made with 💗 by Ashwin Chauhan</p>
                </div>
              </footer>
            </SmoothScroll>
            <Toaster richColors />
            </ThemeProvider>
          </ClerkProvider>
        </body>
      </html>
  );
}
