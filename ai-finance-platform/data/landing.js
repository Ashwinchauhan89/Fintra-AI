import {
  BarChart3,
  Receipt,
  PieChart,
  CreditCard,
  Globe,
  Zap,
  Lock,
  TrendingUp,
} from "lucide-react";


// Stats Data — FinTech focused
export const statsData = [
  { value: "50K+",  label: "Active Users",           suffix: "Growing every day" },
  { value: "$2B+",  label: "Transactions Tracked",   suffix: "Across all accounts" },
  { value: "99.9%", label: "Uptime",                 suffix: "Always available" },
  { value: "4.9/5", label: "User Rating",            suffix: "Loved by users" },
];

// Features Data — clean unified Fintra brand colors (Neon Green & White)
export const featuresData = [
  {
    icon: <BarChart3 className="h-8 w-8" />,
    title: "Advanced Analytics",
    tag: "Analytics",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "Get deep insights into your spending patterns with AI-powered analytics that surface opportunities you'd never catch manually.",
  },
  {
    icon: <Receipt className="h-8 w-8" />,
    title: "Smart Receipt Scanner",
    tag: "Gemini AI",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "Snap a photo — our AI instantly extracts amounts, vendors, categories, and tax details from any receipt or invoice in under 0.2s.",
  },
  {
    icon: <PieChart className="h-8 w-8" />,
    title: "Budget Planning",
    tag: "Adaptive",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "Build intelligent, adaptive budgets that adjust to your lifestyle. Get proactive alerts before you overspend.",
  },
  {
    icon: <CreditCard className="h-8 w-8" />,
    title: "Multi-Account Support",
    tag: "Banking",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "Connect checking, savings, credit cards, and investments in one unified dashboard. Full picture, zero friction.",
  },
  {
    icon: <Globe className="h-8 w-8" />,
    title: "Multi-Currency",
    tag: "Global",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "Track expenses across 160+ currencies with real-time exchange rates. Perfect for travelers and global professionals.",
  },
  {
    icon: <Zap className="h-8 w-8" />,
    title: "Automated Insights",
    tag: "Automation",
    color: "#88CE02",
    glow: "rgba(136, 206, 2, 0.18)",
    description:
      "AI continuously monitors your finances and delivers personalized recommendations to help you save and grow effortlessly.",
  },
];



// How It Works
export const howItWorksData = [
  {
    icon: <Lock className="h-6 w-6" />,
    badge: "Instant Sync",
    title: "Connect Your Accounts",
    subtitle: "Plaid & Open Banking APIs",
    description:
      "Securely link checking, savings, credit cards, and investments in under 60 seconds with bank-grade read-only access.",
    highlights: ["256-Bit TLS", "Zero Credentials Stored", "12k+ Banks"],
  },
  {
    icon: <Zap className="h-6 w-6" />,
    badge: "Gemini Vision AI",
    title: "AI Analyzes Everything",
    subtitle: "Real-Time Classification",
    description:
      "Our AI engine automatically categorizes transactions, flags recurring leakages, and scans invoices with 99.8% precision.",
    highlights: ["0.2s OCR Scan", "Smart Deductions", "Pattern Detection"],
  },
  {
    icon: <TrendingUp className="h-6 w-6" />,
    badge: "Autonomous Growth",
    title: "Take Smarter Action",
    subtitle: "Predictive Wealth Engine",
    description:
      "Receive personalized insights, adaptive budget guardrails, and cashflow forecasts to grow your net worth automatically.",
    highlights: ["Surplus Routing", "Overspend Alerts", "Cashflow Runway"],
  },
];


// Testimonials & Proof
export const testimonialsData = [
  {
    name: "Sarah Johnson",
    role: "Founder, Bloom Studio",
    image: "https://randomuser.me/api/portraits/women/75.jpg",
    impact: "Saved $9,600/yr",
    rating: 5,
    quote:
      "Fintra AI identified $800/month in dormant subscriptions and tax write-offs I completely missed. It literally paid for itself on day one.",
  },
  {
    name: "Michael Chen",
    role: "Principal Tech Lead",
    image: "https://randomuser.me/api/portraits/men/75.jpg",
    impact: "15 hrs saved/mo",
    rating: 5,
    quote:
      "The Gemini Vision receipt scanner is astonishingly fast. Snapping receipts at dinner and having them auto-categorized in 0.2s is pure magic.",
  },
  {
    name: "Emily Rodriguez",
    role: "Certified Wealth Advisor",
    image: "https://randomuser.me/api/portraits/women/74.jpg",
    impact: "2.4x Cashflow Precision",
    rating: 5,
    quote:
      "I recommend Fintra AI to all my private wealth clients. The predictive cashflow and anomaly guard set a new gold standard.",
  },
  {
    name: "David Vance",
    role: "Global Startup Founder",
    image: "https://randomuser.me/api/portraits/men/32.jpg",
    impact: "160+ Currencies Synced",
    rating: 5,
    quote:
      "Managing revenue across USD, EUR, and GBP with real-time conversion and zero spreadsheet friction has saved our operations.",
  },
  {
    name: "Elena Rostova",
    role: "Operations Lead, FintechX",
    image: "https://randomuser.me/api/portraits/women/68.jpg",
    impact: "+$14,200 Net Savings",
    rating: 5,
    quote:
      "The proactive anomaly guard caught a duplicate $1,200 SaaS charge before our bank even notified us. Indispensable tool.",
  },
  {
    name: "Marcus Sterling",
    role: "Angel Investor & Partner",
    image: "https://randomuser.me/api/portraits/men/44.jpg",
    impact: "99.9% Autonomous",
    rating: 5,
    quote:
      "Fintra brings hedge-fund grade cashflow telemetry to personal finances. Hands down the slickest and smartest financial software.",
  },
];


// FAQ Data
export const faqData = [
  {
    question: "How does Fintra AI connect to my bank accounts?",
    answer:
      "Fintra AI partners with Plaid and Open Banking to connect read-only feeds with bank-level 256-bit encryption. We never store or have access to your bank login credentials.",
  },
  {
    question: "Is my financial data secure and private?",
    answer:
      "Yes. We are SOC-2 Type II compliant with end-to-end encryption. Your data is strictly private and will never be shared or sold to third parties.",
  },
  {
    question: "How does the AI receipt scanner work?",
    answer:
      "Simply upload or photograph any receipt. Our vision model automatically extracts merchant name, date, tax, and item breakdown, then categorizes it directly into your budget.",
  },
  {
    question: "Can I manage multiple currencies?",
    answer:
      "Yes! Fintra AI supports 160+ world currencies with automatic real-time rate conversion, making it effortless to manage foreign expenses or multi-national assets.",
  },
  {
    question: "Is there a free trial available?",
    answer:
      "Absolutely. You can get started immediately with our free tier or 14-day trial without entering any credit card information.",
  },
];

