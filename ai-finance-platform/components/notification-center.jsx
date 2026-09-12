"use client";

import React, { useState } from "react";
import {
  Bell,
  CheckCheck,
  AlertTriangle,
  Clock,
  TrendingUp,
  ShieldAlert,
  X,
  CreditCard,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

const INITIAL_NOTIFICATIONS = [
  {
    id: "notif-1",
    type: "budget",
    title: "Budget Threshold Warning",
    message: "You've utilized 82% of your monthly Groceries & Dining budget.",
    time: "2 hours ago",
    read: false,
    icon: AlertTriangle,
    color: "text-amber-500 bg-amber-500/10",
  },
  {
    id: "notif-2",
    type: "subscription",
    title: "Upcoming Recurring Bill",
    message: "Netflix Premium ($19.99) is scheduled for auto-debit in 3 days.",
    time: "5 hours ago",
    read: false,
    icon: Clock,
    color: "text-blue-500 bg-blue-500/10",
    link: "/subscriptions",
  },
  {
    id: "notif-3",
    type: "growth",
    title: "Savings Rate Milestone",
    message: "Great discipline! Your savings rate for this period is 28%, beating your goal.",
    time: "1 day ago",
    read: true,
    icon: TrendingUp,
    color: "text-emerald-500 bg-emerald-500/10",
  },
  {
    id: "notif-4",
    type: "security",
    title: "Spending Spike Monitored",
    message: "A single transaction of $145 was approved with no anomalies flagged.",
    time: "2 days ago",
    read: true,
    icon: ShieldAlert,
    color: "text-purple-500 bg-purple-500/10",
  },
];

export function NotificationCenter() {
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleDismiss = (e, id) => {
    e.stopPropagation();
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleItemClick = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="relative rounded-full border-white/20 bg-white/5 hover:bg-white/10 text-white hover:text-white"
          aria-label="Open notifications"
        >
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow">
              {unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-80 sm:w-96 p-0 shadow-2xl rounded-2xl border bg-card/95 backdrop-blur-md overflow-hidden z-50"
      >
        {/* Header */}
        <div className="p-3.5 border-b flex items-center justify-between bg-muted/30">
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm text-foreground">Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0.2">
                {unreadCount} new
              </Badge>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="text-xs text-primary hover:underline flex items-center gap-1 font-medium"
            >
              <CheckCheck className="h-3 w-3" />
              Mark all read
            </button>
          )}
        </div>

        {/* Notifications list */}
        <div className="max-h-[340px] overflow-y-auto divide-y divide-border/40">
          {notifications.length === 0 ? (
            <div className="p-6 text-center text-xs text-muted-foreground">
              No notifications at this time.
            </div>
          ) : (
            notifications.map((notif) => {
              const Icon = notif.icon;
              return (
                <div
                  key={notif.id}
                  onClick={() => handleItemClick(notif.id)}
                  className={`p-3 transition-colors flex items-start gap-3 cursor-pointer hover:bg-muted/40 ${
                    !notif.read ? "bg-primary/5" : ""
                  }`}
                >
                  <div
                    className={`h-7 w-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${notif.color}`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                  </div>

                  <div className="flex-1 min-w-0 space-y-0.5">
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-xs font-semibold truncate ${
                          !notif.read ? "text-foreground font-bold" : "text-muted-foreground"
                        }`}
                      >
                        {notif.title}
                      </span>
                      <span className="text-[10px] text-muted-foreground whitespace-nowrap ml-2">
                        {notif.time}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                      {notif.message}
                    </p>
                    {notif.link && (
                      <Link
                        href={notif.link}
                        className="inline-flex items-center gap-1 text-[11px] text-primary font-medium hover:underline pt-0.5"
                      >
                        View Subscriptions
                        <ChevronRight className="h-3 w-3" />
                      </Link>
                    )}
                  </div>

                  <button
                    onClick={(e) => handleDismiss(e, notif.id)}
                    className="text-muted-foreground/60 hover:text-foreground shrink-0 p-0.5"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="p-2 border-t bg-muted/20 text-center">
          <Link
            href="/subscriptions"
            className="text-xs text-muted-foreground hover:text-foreground font-medium inline-flex items-center gap-1 py-1"
          >
            <CreditCard className="h-3.5 w-3.5 text-primary" />
            Manage Subscriptions & Recurring Bills
          </Link>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
