import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";
import { ClerkProvider } from "@clerk/nextjs";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/theme-provider";
import SmoothScroll from "@/components/smooth-scroll";
import Footer from "@/components/footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Fintra - AI",
  description: "One stop Finance Platform",
};

export default function RootLayout({ children }) {
  const isClerkConfigured =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("ZXhhbXBs");

  const layoutContent = (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <Header />
      <SmoothScroll>
        <main className="min-h-screen pt-28">{children}</main>
      </SmoothScroll>

      <Toaster richColors />

    </ThemeProvider>
  );

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/logo-sm.png" sizes="any" />
      </head>
      <body className={`${inter.className}`}>
        {isClerkConfigured ? (
          <ClerkProvider>{layoutContent}</ClerkProvider>
        ) : (
          layoutContent
        )}
      </body>
    </html>
  );
}
