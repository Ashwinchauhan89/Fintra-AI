import arcjet, { createMiddleware, detectBot, shield } from "@arcjet/next";
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/account(.*)",
  "/transaction(.*)",
]);

const isClerkConfigured =
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
  !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("ZXhhbXBs");

const isArcjetConfigured =
  process.env.ARCJET_KEY &&
  !process.env.ARCJET_KEY.includes("dummy");

// Create Arcjet middleware
const aj = arcjet({
  key: process.env.ARCJET_KEY || "dummy",
  rules: [
    shield({
      mode: "DRY_RUN",
    }),
    detectBot({
      mode: "DRY_RUN",
      allow: [
        "CATEGORY:SEARCH_ENGINE",
        "GO_HTTP",
      ],
    }),
  ],
});

// Create base Clerk middleware
const clerk = clerkMiddleware(async (auth, req) => {
  const { userId } = await auth();

  if (!userId && isProtectedRoute(req)) {
    const { redirectToSignIn } = await auth();
    return redirectToSignIn();
  }

  return NextResponse.next();
});

export default function middleware(req) {
  if (!isClerkConfigured) {
    if (isProtectedRoute(req)) {
      return NextResponse.redirect(new URL("/sign-in", req.url));
    }
    if (isArcjetConfigured) {
      return createMiddleware(aj)(req);
    }
    return NextResponse.next();
  }
  return createMiddleware(aj, clerk)(req);
}


export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)|api/inngest).*)",
    "/(api(?!/inngest)|trpc)(.*)",
    "/__clerk/:path*",
  ],
};
