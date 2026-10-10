import { getUserSubscriptions } from "@/actions/subscription";
import { SubscriptionTracker } from "./_components/subscription-tracker";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Subscription Tracker | Fintra-AI",
  description: "Monitor recurring bills, active subscriptions, and projected annual cash commitments.",
};

export default async function SubscriptionsPage() {
  const result = await getUserSubscriptions();

  return (
    <div className="max-w-6xl mx-auto px-5 space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <div className="flex flex-col gap-1">
        <h1 className="text-4xl sm:text-5xl gradient-title font-bold">
          Recurring Subscriptions
        </h1>
        <p className="text-muted-foreground text-sm">
          Track, audit, and optimize monthly recurring commitments and software subscriptions.
        </p>
      </div>

      <SubscriptionTracker initialData={result?.data} />
    </div>
  );
}
