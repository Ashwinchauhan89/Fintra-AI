import { getUserAccounts, getDashboardData } from "@/actions/dashboard";
import { getCurrentBudget } from "@/actions/budget";
import { ExecutiveReport } from "./_components/executive-report";
import { SavingsStreaks } from "./_components/savings-streaks";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Executive Financial Statement & Reports | Fintra-AI",
  description: "Official monthly financial performance statement, habit gamification, and cash flow audit.",
};

export default async function MonthlyReportsPage() {
  const [accounts, transactions, budgetData] = await Promise.all([
    getUserAccounts(),
    getDashboardData(),
    getCurrentBudget(),
  ]);

  return (
    <div className="max-w-6xl mx-auto px-5 space-y-8">
      <div className="flex items-center justify-between print:hidden">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <div className="flex flex-col gap-1 print:hidden">
        <h1 className="text-4xl sm:text-5xl gradient-title font-bold">
          Executive Reports & Statements
        </h1>
        <p className="text-muted-foreground text-sm">
          Printable monthly financial audits, savings habit tracking, and verified statements.
        </p>
      </div>

      {/* Gamification Streaks */}
      <div className="print:hidden">
        <SavingsStreaks accounts={accounts || []} transactions={transactions || []} />
      </div>

      {/* Executive Printable Statement */}
      <ExecutiveReport
        accounts={accounts || []}
        transactions={transactions || []}
        budget={budgetData?.budget}
      />
    </div>
  );
}
