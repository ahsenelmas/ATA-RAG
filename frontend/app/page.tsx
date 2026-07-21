import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50">
      <section className="max-w-2xl px-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900">
          ATA RAG Assistant
        </h1>

        <p className="mt-4 text-lg text-gray-600">
          Ask questions about Akademia Techniczno-Artystyczna programmes,
          admissions, tuition fees, scholarships, and university services.
        </p>

        <div className="mt-8 flex justify-center gap-4">
          <Link
            href="/chat"
            className="rounded-lg bg-gray-900 px-6 py-3 text-white"
          >
            Open Chat
          </Link>

          <Link
            href="/dashboard"
            className="rounded-lg border border-gray-300 px-6 py-3 text-gray-900"
          >
            Dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
