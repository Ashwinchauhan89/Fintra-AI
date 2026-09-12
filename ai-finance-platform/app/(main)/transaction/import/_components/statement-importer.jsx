"use client";

import React, { useState, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Trash2,
  Download,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { defaultCategories, categoryColors } from "@/data/categories";
import { bulkImportTransactions } from "@/actions/transaction";

// Keyword auto-categorization mapping
const CATEGORY_RULES = [
  { cat: "food", words: ["swiggy", "zomato", "restaurant", "cafe", "mcdonalds", "burger", "starbucks", "pizza", "dining"] },
  { cat: "groceries", words: ["grocery", "supermarket", "walmart", "trader", "costco", "blinkit", "zepto", "instamart", "fresh"] },
  { cat: "transportation", words: ["uber", "ola", "lyft", "metro", "fuel", "petrol", "diesel", "shell", "flight", "airline", "train"] },
  { cat: "housing", words: ["rent", "maintenance", "mortgage", "landlord", "lease", "society"] },
  { cat: "utilities", words: ["electricity", "water", "wifi", "broadband", "verizon", "airtel", "jio", "gas"] },
  { cat: "entertainment", words: ["netflix", "spotify", "hulu", "cinema", "movie", "apple music", "youtube", "disney", "steam"] },
  { cat: "shopping", words: ["amazon", "flipkart", "clothing", "apparel", "zara", "h&m", "retail", "store", "electronics"] },
  { cat: "healthcare", words: ["pharmacy", "doctor", "hospital", "clinic", "medicine", "dental", "cvs", "walgreens"] },
  { cat: "education", words: ["course", "udemy", "coursera", "college", "tuition", "books", "university"] },
  { cat: "salary", words: ["salary", "payroll", "stipend", "wages", "employer", "deposit"] },
];

function inferCategory(desc = "", type = "EXPENSE") {
  if (type === "INCOME") return "salary";
  const lower = desc.toLowerCase();
  for (const rule of CATEGORY_RULES) {
    if (rule.words.some((w) => lower.includes(w))) {
      return rule.cat;
    }
  }
  return "other-expense";
}

export function StatementImporter({ accounts = [] }) {
  const router = useRouter();
  const fileInputRef = useRef(null);
  const [selectedAccountId, setSelectedAccountId] = useState(
    accounts.find((a) => a.isDefault)?.id || accounts[0]?.id || ""
  );
  const [parsedTransactions, setParsedTransactions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [fileName, setFileName] = useState("");

  // Parse CSV text
  const parseCSV = (text) => {
    const lines = text.split(/\r\n|\n/).filter((l) => l.trim().length > 0);
    if (lines.length < 2) {
      toast.error("CSV file does not contain enough data rows.");
      return [];
    }

    const rawHeaders = lines[0].split(",").map((h) => h.trim().toLowerCase().replace(/['"]/g, ""));

    // Identify header positions
    let dateIdx = rawHeaders.findIndex((h) => h.includes("date"));
    let descIdx = rawHeaders.findIndex((h) =>
      h.includes("desc") || h.includes("narrat") || h.includes("particular") || h.includes("merchant") || h.includes("memo") || h.includes("detail")
    );
    let amountIdx = rawHeaders.findIndex((h) => h.includes("amount") || h.includes("total"));
    let debitIdx = rawHeaders.findIndex((h) => h.includes("debit") || h.includes("withdrawal"));
    let creditIdx = rawHeaders.findIndex((h) => h.includes("credit") || h.includes("deposit"));
    let typeIdx = rawHeaders.findIndex((h) => h.includes("type"));
    let catIdx = rawHeaders.findIndex((h) => h.includes("category"));

    // Fallbacks if not recognized
    if (dateIdx === -1) dateIdx = 0;
    if (descIdx === -1) descIdx = 1;
    if (amountIdx === -1 && debitIdx === -1 && creditIdx === -1) amountIdx = 2;

    const parsed = [];

    for (let i = 1; i < lines.length; i++) {
      // Basic CSV split respecting quotes
      const row = lines[i].match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || lines[i].split(",");
      if (!row || row.length < 2) continue;

      const cleanCol = (idx) => (idx >= 0 && row[idx] ? row[idx].replace(/['"]/g, "").trim() : "");

      const rawDate = cleanCol(dateIdx);
      const rawDesc = cleanCol(descIdx) || "Imported Statement Item";

      let amount = 0;
      let type = "EXPENSE";

      if (debitIdx >= 0 && creditIdx >= 0) {
        const debitVal = parseFloat(cleanCol(debitIdx).replace(/[^0-9.-]+/g, ""));
        const creditVal = parseFloat(cleanCol(creditIdx).replace(/[^0-9.-]+/g, ""));
        if (!isNaN(creditVal) && creditVal > 0) {
          amount = creditVal;
          type = "INCOME";
        } else if (!isNaN(debitVal) && debitVal > 0) {
          amount = debitVal;
          type = "EXPENSE";
        }
      } else if (amountIdx >= 0) {
        const cleanAmtStr = cleanCol(amountIdx).replace(/[^0-9.-]+/g, "");
        const rawAmt = parseFloat(cleanAmtStr);
        if (!isNaN(rawAmt)) {
          amount = Math.abs(rawAmt);
          if (rawAmt < 0) {
            type = "EXPENSE";
          } else if (typeIdx >= 0) {
            const rawType = cleanCol(typeIdx).toUpperCase();
            type = rawType.includes("INC") || rawType.includes("CR") ? "INCOME" : "EXPENSE";
          }
        }
      }

      if (amount <= 0) continue;

      const dateObj = new Date(rawDate);
      const validDate = isNaN(dateObj.getTime())
        ? new Date().toISOString().split("T")[0]
        : dateObj.toISOString().split("T")[0];

      const explicitCat = catIdx >= 0 ? cleanCol(catIdx) : "";
      const category = explicitCat || inferCategory(rawDesc, type);

      parsed.push({
        id: `row-${i}-${Date.now()}`,
        date: validDate,
        description: rawDesc,
        amount,
        type,
        category,
      });
    }

    return parsed;
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setIsProcessing(true);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result;
        if (typeof content === "string") {
          const results = parseCSV(content);
          if (results.length > 0) {
            setParsedTransactions(results);
            toast.success(`Successfully parsed ${results.length} transactions.`);
          } else {
            toast.error("No valid transactions could be parsed from this file.");
          }
        }
      } catch (err) {
        toast.error("Failed to parse statement: " + err.message);
      } finally {
        setIsProcessing(false);
      }
    };
    reader.readAsText(file);
  };

  const handleCategoryChange = (id, newCat) => {
    setParsedTransactions((prev) =>
      prev.map((t) => (t.id === id ? { ...t, category: newCat } : t))
    );
  };

  const handleRemoveRow = (id) => {
    setParsedTransactions((prev) => prev.filter((t) => t.id !== id));
  };

  const handleExecuteImport = async () => {
    if (!selectedAccountId) {
      toast.error("Please select a target account for the import.");
      return;
    }
    if (parsedTransactions.length === 0) {
      toast.error("No transactions to import.");
      return;
    }

    setIsImporting(true);
    try {
      const res = await bulkImportTransactions({
        accountId: selectedAccountId,
        transactions: parsedTransactions,
      });

      if (res.success) {
        toast.success(`Imported ${res.count} transactions successfully!`);
        router.push(`/account/${selectedAccountId}`);
      } else {
        toast.error(res.error || "Failed to import transactions");
      }
    } catch (err) {
      toast.error(err.message || "An error occurred during import");
    } finally {
      setIsImporting(false);
    }
  };

  const downloadSampleCSV = () => {
    const sample = `Date,Description,Amount,Type\n2026-09-01,Tech Corp Payroll Salary,4500.00,INCOME\n2026-09-02,Trader Joe's Supermarket,142.50,EXPENSE\n2026-09-03,Uber Ride Transit,24.80,EXPENSE\n2026-09-04,Netflix Subscription,19.99,EXPENSE\n2026-09-05,Amazon Electronics Purchase,115.00,EXPENSE\n2026-09-06,Electric Utility Bill,85.20,EXPENSE\n`;
    const blob = new Blob([sample], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fintra_sample_statement.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Sample statement downloaded.");
  };

  const { totalInflow, totalOutflow } = useMemo(() => {
    let inflow = 0;
    let outflow = 0;
    parsedTransactions.forEach((t) => {
      if (t.type === "INCOME") inflow += t.amount;
      else outflow += t.amount;
    });
    return { totalInflow: inflow, totalOutflow: outflow };
  }, [parsedTransactions]);

  return (
    <div className="space-y-6">
      {/* Account Selection & Actions Header */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-xl font-bold flex items-center gap-2">
                <Upload className="h-5 w-5 text-primary" />
                Bank Statement & CSV Importer
              </CardTitle>
              <CardDescription>
                Harmonize multi-bank statements, auto-tag categories, and import in bulk
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={downloadSampleCSV}
                className="text-xs gap-1.5"
              >
                <Download className="h-3.5 w-3.5" />
                Sample CSV
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="w-full sm:w-72 space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">
                Target Bank Account
              </label>
              <Select
                value={selectedAccountId}
                onValueChange={setSelectedAccountId}
                disabled={accounts.length === 0}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts.map((acc) => (
                    <SelectItem key={acc.id} value={acc.id}>
                      {acc.name} (${Number(acc.balance).toFixed(2)})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Dropzone Trigger */}
            <div className="flex-1 w-full">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-primary/50 hover:bg-muted/20 transition-all text-center"
              >
                <FileText className="h-8 w-8 text-muted-foreground" />
                <div>
                  <span className="text-sm font-semibold text-foreground">
                    {fileName ? fileName : "Choose a CSV or Bank Statement file"}
                  </span>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Supports exports from Chase, HDFC, Wells Fargo, ICICI, Revolut, etc.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Preview Section */}
      {parsedTransactions.length > 0 && (
        <Card className="animate-in fade-in duration-200">
          <CardHeader className="pb-3 border-b flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="text-lg font-bold flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-500" />
                Previewing {parsedTransactions.length} Transactions
              </CardTitle>
              <CardDescription>
                Review details, modify categories if desired, then proceed to import
              </CardDescription>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-xs font-medium space-x-2">
                <span className="text-emerald-500 font-bold">
                  +${totalInflow.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
                <span className="text-muted-foreground">|</span>
                <span className="text-rose-500 font-bold">
                  -${totalOutflow.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              <Button
                onClick={handleExecuteImport}
                disabled={isImporting}
                className="gap-1.5 font-semibold text-xs h-9 px-4 shadow"
              >
                {isImporting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    Confirm Import
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-muted/50 border-b text-muted-foreground font-semibold">
                <tr>
                  <th className="p-3">Date</th>
                  <th className="p-3">Description</th>
                  <th className="p-3">Auto Category</th>
                  <th className="p-3 text-right">Amount</th>
                  <th className="p-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {parsedTransactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-muted/30 transition-colors">
                    <td className="p-3 font-mono text-muted-foreground whitespace-nowrap">
                      {tx.date}
                    </td>
                    <td className="p-3 font-medium text-foreground max-w-[280px] truncate">
                      {tx.description}
                    </td>
                    <td className="p-3">
                      <Select
                        value={tx.category}
                        onValueChange={(val) => handleCategoryChange(tx.id, val)}
                      >
                        <SelectTrigger className="h-7 text-xs w-[140px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {defaultCategories.map((c) => (
                            <SelectItem key={c.id} value={c.id} className="text-xs">
                              {c.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                    <td
                      className={`p-3 text-right font-mono font-semibold whitespace-nowrap ${
                        tx.type === "INCOME" ? "text-emerald-500" : "text-rose-500"
                      }`}
                    >
                      {tx.type === "INCOME" ? "+" : "-"}${tx.amount.toFixed(2)}
                    </td>
                    <td className="p-3 text-center">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-muted-foreground hover:text-rose-500"
                        onClick={() => handleRemoveRow(tx.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
