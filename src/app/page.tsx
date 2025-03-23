"use client";

import { signIn } from "next-auth/react";

export default function HomePage() {
  return (
    <main className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl font-bold mb-6">Senior Assassin Website</h1>
      <button
        onClick={() => signIn("google", { callbackUrl: "/success" })}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Sign In with Google
      </button>
    </main>
  );
}