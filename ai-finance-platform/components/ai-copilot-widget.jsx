"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  MessageSquare,
  X,
  Send,
  Bot,
  User,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  TrendingUp,
  ShieldCheck,
  CreditCard,
  Loader2,
  ChevronRight,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { askFinancialCopilot, solvePurchaseAffordability } from "@/actions/ml-predict";

const QUICK_PROMPTS = [
  "How healthy is my emergency runway?",
  "Can I afford to invest $500 this month?",
  "What is the best way to trim monthly expenses?",
];

export function AiCopilotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("chat"); // 'chat' | 'affordability'

  // Chat State
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your Fintra-AI Financial Copilot. Ask me anything about your budget, savings rate, or test if you can afford a major purchase.",
      checklist: [
        "Analyze monthly savings rate and runway",
        "Test big purchases via Affordability Solver",
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Affordability State
  const [itemName, setItemName] = useState("");
  const [itemPrice, setItemPrice] = useState("");
  const [affordResult, setAffordResult] = useState(null);
  const [isAffordLoading, setIsAffordLoading] = useState(false);

  useEffect(() => {
    if (isOpen && activeTab === "chat") {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, activeTab]);

  const handleSendMessage = async (queryToSend) => {
    const text = queryToSend || inputQuery;
    if (!text.trim() || isLoading) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const res = await askFinancialCopilot({
        userQuery: text,
        monthlyIncome: 65000,
        monthlyExpenses: 35000,
        currentBalance: 75000,
      });

      if (res.success && res.data) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: res.data.ai_advisory,
            checklist: res.data.action_checklist,
            context: res.data.deterministic_ml_context,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "I analyzed your financial posture. Based on standard guidelines, keep at least 3 months of expenses in a liquid buffer before allocating more to discretionary items.",
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I had trouble processing that query. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckAffordability = async (e) => {
    e.preventDefault();
    if (!itemName || !itemPrice || isAffordLoading) return;

    setIsAffordLoading(true);
    setAffordResult(null);

    try {
      const res = await solvePurchaseAffordability({
        itemName,
        itemPrice: Number(itemPrice),
        monthlyIncome: 65000,
        monthlyExpenses: 35000,
        currentLiquidSavings: 75000,
        existingMonthlyEmi: 0,
      });

      if (res.success && res.data) {
        setAffordResult(res.data);
      }
    } catch {
      // no-op
    } finally {
      setIsAffordLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Floating Modal */}
      {isOpen && (
        <Card className="w-[92vw] sm:w-[420px] h-[550px] shadow-2xl rounded-2xl border border-primary/20 bg-card/95 backdrop-blur-md flex flex-col overflow-hidden mb-3 animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <CardHeader className="p-3.5 bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border-b flex flex-row items-center justify-between space-y-0">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                  Fintra AI Copilot
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                </CardTitle>
                <CardDescription className="text-[11px]">
                  Hybrid Gemini & ML Advisory
                </CardDescription>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 rounded-full text-muted-foreground hover:text-foreground"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          {/* Navigation Tabs */}
          <div className="flex border-b text-xs font-medium bg-muted/40">
            <button
              onClick={() => setActiveTab("chat")}
              className={`flex-1 py-2 text-center border-b-2 transition-colors flex items-center justify-center gap-1.5 ${
                activeTab === "chat"
                  ? "border-primary text-primary font-semibold bg-background"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <MessageSquare className="h-3.5 w-3.5" />
              Advisory Chat
            </button>
            <button
              onClick={() => setActiveTab("affordability")}
              className={`flex-1 py-2 text-center border-b-2 transition-colors flex items-center justify-center gap-1.5 ${
                activeTab === "affordability"
                  ? "border-primary text-primary font-semibold bg-background"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <CreditCard className="h-3.5 w-3.5" />
              Can I Afford It?
            </button>
          </div>

          {/* Tab 1: Chat Stream */}
          {activeTab === "chat" && (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto p-3.5 space-y-3">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex gap-2.5 ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.role === "assistant" && (
                      <div className="h-6 w-6 rounded-full bg-primary/20 text-primary flex items-center justify-center shrink-0 mt-0.5">
                        <Bot className="h-3.5 w-3.5" />
                      </div>
                    )}
                    <div
                      className={`max-w-[82%] rounded-xl p-3 text-xs leading-relaxed ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground font-medium rounded-tr-none"
                          : "bg-muted/60 text-foreground border border-border/70 rounded-tl-none space-y-2"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>

                      {msg.checklist && msg.checklist.length > 0 && (
                        <div className="pt-1.5 border-t border-border/50 space-y-1">
                          <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block">
                            Key Recommendations:
                          </span>
                          {msg.checklist.map((item, idx) => (
                            <div key={idx} className="flex items-start gap-1.5 text-[11px]">
                              <CheckCircle2 className="h-3 w-3 text-emerald-500 mt-0.5 shrink-0" />
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground p-2">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                    <span>Analyzing financial context...</span>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              {/* Quick suggestions */}
              <div className="px-3 py-1.5 bg-muted/20 border-t flex gap-1.5 overflow-x-auto no-scrollbar">
                {QUICK_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(prompt)}
                    className="text-[10px] whitespace-nowrap bg-muted/60 hover:bg-muted text-muted-foreground hover:text-foreground px-2 py-1 rounded-md transition-colors border"
                  >
                    {prompt}
                  </button>
                ))}
              </div>

              {/* Input bar */}
              <div className="p-3 border-t bg-card flex gap-2 items-center">
                <Input
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask financial questions..."
                  className="text-xs h-9"
                  disabled={isLoading}
                />
                <Button
                  size="icon"
                  className="h-9 w-9 shrink-0"
                  onClick={() => handleSendMessage()}
                  disabled={isLoading || !inputQuery.trim()}
                >
                  <Send className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          )}

          {/* Tab 2: Affordability Solver */}
          {activeTab === "affordability" && (
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  Purchase Affordability Solver
                </h4>
                <p className="text-[11px] text-muted-foreground">
                  Test if a big-ticket purchase compromises your emergency cushion.
                </p>
              </div>

              <form onSubmit={handleCheckAffordability} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[11px] font-medium text-muted-foreground">
                    Item or Goal Name
                  </label>
                  <Input
                    placeholder="e.g. MacBook Pro, Vacation, iPhone 16"
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    className="text-xs h-8"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-medium text-muted-foreground">
                    Estimated Cost ($)
                  </label>
                  <Input
                    type="number"
                    placeholder="e.g. 1500"
                    value={itemPrice}
                    onChange={(e) => setItemPrice(e.target.value)}
                    className="text-xs h-8"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  size="sm"
                  className="w-full text-xs h-8 gap-1.5"
                  disabled={isAffordLoading || !itemName || !itemPrice}
                >
                  {isAffordLoading ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      Evaluating Impact...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-3.5 w-3.5" />
                      Solve Affordability
                    </>
                  )}
                </Button>
              </form>

              {/* Affordability Result */}
              {affordResult && (
                <div className="p-3 rounded-xl bg-muted/40 border space-y-2.5 animate-in fade-in duration-200">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-foreground">
                      {affordResult.item_name}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-bold px-2 py-0.5 ${
                        affordResult.verdict === "AFFORDABLE_CASH"
                          ? "bg-emerald-500/15 text-emerald-600 border-emerald-500/30"
                          : affordResult.verdict === "AFFORDABLE_NO_COST_EMI"
                          ? "bg-amber-500/15 text-amber-600 border-amber-500/30"
                          : "bg-rose-500/15 text-rose-600 border-rose-500/30"
                      }`}
                    >
                      {affordResult.verdict === "AFFORDABLE_CASH"
                        ? "Safe for Full Cash"
                        : affordResult.verdict === "AFFORDABLE_NO_COST_EMI"
                        ? "Safe on 0% EMI"
                        : "Not Advised Currently"}
                    </Badge>
                  </div>

                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {affordResult.ai_copilot_advice}
                  </p>

                  <div className="pt-2 border-t text-[11px] grid grid-cols-2 gap-2 text-muted-foreground">
                    <div className="p-2 bg-background/60 rounded border">
                      <span className="block text-[10px]">Current Runway</span>
                      <span className="font-semibold text-foreground font-mono">
                        {affordResult.impact_on_emergency_fund?.current_runway_months} mos
                      </span>
                    </div>
                    <div className="p-2 bg-background/60 rounded border">
                      <span className="block text-[10px]">Post-Purchase</span>
                      <span className="font-semibold text-foreground font-mono">
                        {affordResult.impact_on_emergency_fund?.post_purchase_runway_months} mos
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>
      )}

      {/* Floating Toggle Trigger */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        size="lg"
        className="rounded-full h-12 px-4 shadow-xl bg-gradient-to-r from-primary to-primary/90 text-primary-foreground flex items-center gap-2 hover:scale-105 transition-transform"
      >
        <Sparkles className="h-5 w-5 text-amber-300 animate-pulse" />
        <span className="font-semibold text-sm">AI Copilot</span>
      </Button>
    </div>
  );
}
