import { getUserAccounts } from "@/actions/dashboard";
import { defaultCategories } from "@/data/categories";
import { AddTransactionForm } from "../_components/transaction-form";
import { getTransaction } from "@/actions/transaction";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";

export default async function AddTransactionPage({ searchParams }) {
  const accounts = await getUserAccounts();
  const editId = searchParams?.edit;

  let initialData = null;
  if (editId) {
    const transaction = await getTransaction(editId);
    initialData = transaction;
  }

  return (
    <div className="max-w-3xl mx-auto px-5">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-8">
        <h1 className="text-5xl gradient-title ">Add Transaction</h1>
        {!editId && (
          <Link href="/transaction/import">
            <Button variant="outline" className="gap-2 text-xs font-semibold shadow-sm">
              <Upload className="h-4 w-4 text-primary" />
              Import CSV / Statement
            </Button>
          </Link>
        )}
      </div>
      <AddTransactionForm
        accounts={accounts}
        categories={defaultCategories}
        editMode={!!editId}
        initialData={initialData}
      />
    </div>
  );
}
