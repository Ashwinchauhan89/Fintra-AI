import { currentUser } from "@clerk/nextjs/server";
import { db } from "./prisma";

export const checkUser = async () => {
  if (
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("ZXhhbXBs")
  ) {
    return null;
  }

  const user = await currentUser();

  if (!user) {
    return null;
  }

  try {
    const email =
      user.primaryEmailAddress?.emailAddress ||
      user.emailAddresses?.[0]?.emailAddress;

    if (!email) {
      throw new Error("Authenticated user has no email address");
    }

    const name = [user.firstName, user.lastName]
      .filter((part) => typeof part === "string" && part.trim())
      .join(" ")
      .trim() || null;

    return db.user.upsert({
      where: { clerkUserId: user.id },
      update: {
        name,
        imageUrl: user.imageUrl || null,
        email,
      },
      create: {
        clerkUserId: user.id,
        name,
        imageUrl: user.imageUrl || null,
        email,
      },
    });
  } catch (error) {
    console.error("Failed to provision authenticated user:", error);
    throw new Error("Unable to initialize user profile");
  }
};
