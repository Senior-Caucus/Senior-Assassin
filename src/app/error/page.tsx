"use client";

import { useSearchParams } from "next/navigation";

export default function ErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  return (
    <main className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl font-bold text-red-600 mb-4">Sign In Error</h1>
      {error && <p className="text-red-500">Error: {error}</p>}
      <p className="mt-2">
        Sorry, you are not authorized or something went wrong. Please try again.
      </p>
    </main>
  );
}