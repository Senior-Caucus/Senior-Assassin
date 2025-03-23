// src/lib/auth.ts
import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      // Print the user object to see what it contains
      console.log(user.email); // Log the email to see it

      // Only allow emails that end with @stuy.edu and have a '5' in the local part
      if (!user.email) return false;

      const [localPart, domain] = user.email.split("@");
      if (domain === "stuy.edu" && localPart.includes("5")) {
        console.log("Accepted sign in for:", user.email);
        return true;
      }
      return false; // Reject sign in
    },
    async session({ session }) {
      // Can modify the session object here if needed
      return session;
    },
  },
  // Manually handling "error" and "success" pages in the App Router,
  // but we can still specify custom pages
  pages: {
    signIn: "/",
    error: "/error", // we will create /error/page.tsx
  },
};