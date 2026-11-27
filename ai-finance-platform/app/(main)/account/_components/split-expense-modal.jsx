"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  X,
  Plus,
  Trash2,
  Copy,
  Share2,
  CheckCircle2,
  Clock,
  DollarSign,
  MessageSquare,
  Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export function SplitExpenseModal({ transaction, isOpen, onClose }) {
  const [friends, setFriends] = useState([
    { id: "1", name: "Alex", share: 0, settled: false },
    { id: "2", name: "Sam", share: 0, settled: false },
  ]);
  const [newFriendName, setNewFriendName] = useState("");
  const [splitMode, setSplitMode] = useState("EQUAL"); // EQUAL or CUSTOM

  const totalAmount = Number(transaction?.amount) || 0;
  const description = transaction?.description || "Shared Expense";

  // Calculate equal splits whenever friends change or modal opens
  useEffect(() => {
    if (splitMode === "EQUAL" && totalAmount > 0) {
      const totalPeople = friends.length + 1; // friends + current user
      const perPerson = Number((totalAmount / totalPeople).toFixed(2));
      setFriends((prev) =>
        prev.map((f) => ({
          ...f,
          share: perPerson,
        }))
      );
    }
  }, [friends.length, totalAmount, splitMode]);

  if (!isOpen || !transaction) return null;

  const userShare =
    splitMode === "EQUAL"
      ? Number((totalAmount / (friends.length + 1)).toFixed(2))
      : Number((totalAmount - friends.reduce((sum, f) => sum + Number(f.share || 0), 0)).toFixed(2));

  const totalCollected = friends
    .filter((f) => f.settled)
    .reduce((sum, f) => sum + Number(f.share || 0), 0);

  const totalPending = friends
    .filter((f) => !f.settled)
    .reduce((sum, f) => sum + Number(f.share || 0), 0);

  const handleAddFriend = (e) => {
    e.preventDefault();
    if (!newFriendName.trim()) return;
    const newId = Date.now().toString();
    const newCount = friends.length + 2; // +1 new friend, +1 user
    const perPerson = Number((totalAmount / newCount).toFixed(2));

    setFriends((prev) => [
      ...prev.map((f) => ({ ...f, share: perPerson })),
      { id: newId, name: newFriendName.trim(), share: perPerson, settled: false },
    ]);
    setNewFriendName("");
    toast.success(`Added ${newFriendName.trim()} to split.`);
  };

  const handleRemoveFriend = (id) => {
    if (friends.length <= 1) {
      toast.error("You need at least one peer to split an expense.");
      return;
    }
    setFriends((prev) => prev.filter((f) => f.id !== id));
  };

  const handleToggleSettled = (id) => {
    setFriends((prev) =>
      prev.map((f) => (f.id === id ? { ...f, settled: !f.settled } : f))
    );
  };

  const handleUpdateCustomShare = (id, value) => {
    setFriends((prev) =>
      prev.map((f) => (f.id === id ? { ...f, share: Number(value) || 0 } : f))
    );
  };

  const handleCopyPaymentRequest = (friend) => {
    const text = `Hey ${friend.name}! Your share for "${description}" is $${friend.share.toFixed(
      2
    )}. Please settle when free. Thanks!`;
    navigator.clipboard.writeText(text);
    toast.success(`Copied reminder for ${friend.name}!`);
  };

  const handleWhatsAppShare = (friend) => {
    const text = encodeURIComponent(
      `Hey ${friend.name}! Your share for "${description}" is $${friend.share.toFixed(
        2
      )}. Please settle when free. Thanks!`
    );
    window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <Card className="w-full max-w-lg bg-card border-border/70 shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <CardHeader className="flex flex-row items-start justify-between pb-3 border-b border-border/40 space-y-0">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
                <Users className="h-4 w-4" />
              </div>
              <CardTitle className="text-base sm:text-lg font-bold">
                Smart Peer Bill Splitting
              </CardTitle>
            </div>
            <CardDescription className="text-xs text-muted-foreground mt-1">
              Divide &quot;{description}&quot; (${totalAmount.toFixed(2)}) fairly among friends
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 rounded-full text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        {/* Content Area */}
        <CardContent className="space-y-5 pt-4 overflow-y-auto pr-3">
          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-2 text-center p-3 rounded-xl bg-muted/30 border border-border/40 font-mono text-xs">
            <div>
              <span className="text-[10px] text-muted-foreground block font-sans">Your Net Share</span>
              <span className="font-bold text-foreground text-sm">${userShare.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground block font-sans">Pending Recovery</span>
              <span className="font-bold text-amber-500 text-sm">${totalPending.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground block font-sans">Settled Total</span>
              <span className="font-bold text-emerald-500 text-sm">${totalCollected.toFixed(2)}</span>
            </div>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground">
              Calculation Method
            </span>
            <div className="flex items-center gap-1 bg-muted/60 p-1 rounded-lg">
              <button
                type="button"
                onClick={() => setSplitMode("EQUAL")}
                className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  splitMode === "EQUAL"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Split Equally
              </button>
              <button
                type="button"
                onClick={() => setSplitMode("CUSTOM")}
                className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  splitMode === "CUSTOM"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Custom Amounts
              </button>
            </div>
          </div>

          {/* Peer List */}
          <div className="space-y-2.5">
            <label className="text-xs font-semibold text-muted-foreground">
              Participants ({friends.length + 1})
            </label>

            {/* Current User */}
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-border/40 bg-muted/20 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center text-[10px]">
                  You
                </div>
                <span className="font-semibold text-foreground">You (Organizer)</span>
              </div>
              <span className="font-mono font-bold text-foreground">
                ${userShare.toFixed(2)}
              </span>
            </div>

            {/* Friends */}
            {friends.map((friend) => (
              <div
                key={friend.id}
                className="flex items-center justify-between p-2.5 rounded-lg border border-border/40 bg-card hover:border-border transition-colors text-xs gap-2"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <button
                    type="button"
                    onClick={() => handleToggleSettled(friend.id)}
                    className="shrink-0 text-muted-foreground hover:text-foreground"
                    title={friend.settled ? "Mark Pending" : "Mark Settled"}
                  >
                    {friend.settled ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    ) : (
                      <Clock className="h-4 w-4 text-amber-500" />
                    )}
                  </button>
                  <span className={`font-medium truncate ${friend.settled ? "line-through text-muted-foreground" : "text-foreground"}`}>
                    {friend.name}
                  </span>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {splitMode === "CUSTOM" ? (
                    <Input
                      type="number"
                      value={friend.share}
                      onChange={(e) => handleUpdateCustomShare(friend.id, e.target.value)}
                      className="w-20 h-7 text-xs font-mono font-bold text-right"
                    />
                  ) : (
                    <span className="font-mono font-bold text-foreground">
                      ${friend.share.toFixed(2)}
                    </span>
                  )}

                  <Badge
                    variant="outline"
                    onClick={() => handleToggleSettled(friend.id)}
                    className={`cursor-pointer text-[10px] px-1.5 py-0 ${
                      friend.settled
                        ? "text-emerald-500 border-emerald-500/30 bg-emerald-500/10"
                        : "text-amber-500 border-amber-500/30 bg-amber-500/10"
                    }`}
                  >
                    {friend.settled ? "Paid" : "Pending"}
                  </Badge>

                  {/* Share Reminders */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-muted-foreground hover:text-foreground"
                    onClick={() => handleCopyPaymentRequest(friend)}
                    title="Copy request text"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-emerald-500 hover:text-emerald-400 hover:bg-emerald-500/10"
                    onClick={() => handleWhatsAppShare(friend)}
                    title="Send via WhatsApp"
                  >
                    <Share2 className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-muted-foreground hover:text-rose-500"
                    onClick={() => handleRemoveFriend(friend.id)}
                    title="Remove peer"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Add Friend Row */}
          <form onSubmit={handleAddFriend} className="flex gap-2">
            <Input
              type="text"
              placeholder="Add friend name (e.g., Jordan)..."
              value={newFriendName}
              onChange={(e) => setNewFriendName(e.target.value)}
              className="text-xs h-8"
            />
            <Button type="submit" size="sm" variant="outline" className="h-8 text-xs shrink-0 gap-1">
              <Plus className="h-3.5 w-3.5" /> Add
            </Button>
          </form>

          {/* Informational Footer */}
          <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 text-[11px] text-muted-foreground flex items-center gap-2">
            <Sparkles className="h-3.5 w-3.5 text-primary shrink-0" />
            <span>
              Use the WhatsApp or Copy buttons next to each friend to ping them directly with their calculated payment share.
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
