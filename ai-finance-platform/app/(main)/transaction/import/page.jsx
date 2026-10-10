import { getUserAccounts } from "@/actions/dashboard";
import { StatementImporter } from "./_components/statement-importer";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Import Bank Statement | Fintra-AI",
  description: "Bulk import transactions from bank CSV statements with automatic ML category detection.",
};

export default async function StatementImportPage() {
  const accounts = await getUserAccounts();

  return (
    <div className="max-w-5xl mx-auto px-5 space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/transaction/create">
          <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to Transaction Form
          </Button>
        </Link>
      </div>

      <div className="flex flex-col gap-1">
        <h1 className="text-4xl sm:text-5xl gradient-title font-bold">
          Import Statement
        </h1>
        <p className="text-muted-foreground text-sm">
          Seamlessly ingest external bank transactions, credit card statements, and CSV exports.
        </p>
      </div>

      <StatementImporter accounts={accounts || []} />
    </div>
  );
}
