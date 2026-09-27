import { getUserGoals } from "@/actions/goals";
import { GoalTracker } from "./_components/goal-tracker";
import { Target, Sparkles } from "lucide-react";

export const metadata = {
  title: "Financial Goals & Sinking Funds | Fintra-AI",
  description: "Track and accelerate your financial milestones, sinking funds, and emergency cushions with intelligent pacing.",
};

export default async function GoalsPage() {
  const result = await getUserGoals();

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <Target className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
                Financial Goals & Sinking Funds
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#88CE02]/15 text-[#88CE02] border border-[#88CE02]/30 flex items-center gap-1">
                  <Sparkles className="h-3 w-3" /> Smart Pacing
                </span>
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Automate your milestone timelines, monitor required monthly contributions, and protect long-term cushions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Tracker Widget */}
      <GoalTracker initialData={result?.data} />
    </div>
  );
}
