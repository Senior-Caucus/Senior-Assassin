import NextAuth from "next-auth"
import { authOptions } from "@/lib/auth" // We'll define this below

const handler = NextAuth(authOptions);

// Because we're in the App Router, we export the handler for both GET & POST:
export { handler as GET, handler as POST };