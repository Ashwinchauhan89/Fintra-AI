import { evaluatePurchaseAffordability } from "@/actions/affordability";
import { AffordabilityEvaluator } from "./_components/affordability-evaluator";
import { HelpCircle, Sparkles, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "Buy or Wait? AI Affordability Decision Studio | Fintra-AI",
  description:
    "Evaluate whether you can safely afford a requested purchase using multi-factor financial intelligence, emergency runway preservation, and cash flow simulations.",
};

export default async function AffordabilityPage() {
  const initialResult = await evaluatePurchaseAffordability({
    itemName: "MacBook Pro M3",
    amount: 1999,
    urgency: "DISCRETIONARY",
    installmentMonths: 0,
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <HelpCircle className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
                Buy or Wait? Affordability Studio
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#88CE02]/15 text-[#88CE02] border border-[#88CE02]/30 flex items-center gap-1">
                  <Sparkles className="h-3 w-3" /> Autonomous Decision Agent
                </span>
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Stress-test real purchases against your verified balances, recurring commitments, and 3-month emergency cushion.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground bg-muted/30 px-3 py-2 rounded-xl border border-border/40">
          <ShieldCheck className="h-4 w-4 text-[#88CE02]" />
          <span>3-Month Emergency Cushion Enforced</span>
        </div>
      </div>

      {/* Main Studio Evaluator */}
      <AffordabilityEvaluator initialResult={initialResult} />
    </div>
  );
}
