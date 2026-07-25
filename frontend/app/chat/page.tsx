import { Suspense } from "react";
import ChatPageClient from "./ChatPageClient";

function ChatLoading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#fff7ed] via-white to-[#eff6ff]">
      <div className="rounded-3xl border-2 border-orange-200 bg-white px-8 py-6 text-center shadow-xl">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-500 text-xl text-white">
          ✦
        </div>

        <p className="mt-4 font-bold text-[#0f172a]">
          Loading ATA Assistant...
        </p>
      </div>
    </main>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<ChatLoading />}>
      <ChatPageClient />
    </Suspense>
  );
}