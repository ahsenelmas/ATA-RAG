import Link from "next/link";

const features = [
  {
    title: "Grounded Answers",
    description:
      "Every response is generated from official ATA University content and supported with sources.",
    icon: "✓",
  },
  {
    title: "Multilingual Support",
    description:
      "Ask questions in English, Polish or Turkish and receive clear university information.",
    icon: "A",
  },
  {
    title: "Fast University Search",
    description:
      "Find information about programmes, tuition, admissions and scholarships in seconds.",
    icon: "⌕",
  },
];

const exampleQuestions = [
  "What is the tuition for Computer Engineering?",
  "Which programmes are available in English?",
  "What are the admission requirements?",
];

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-gradient-to-br from-[#fff7ed] via-white to-[#eff6ff] text-[#0f172a]">
      <header className="border-b border-orange-300 bg-[#0f172a]/95 text-white shadow-xl backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-orange-500 text-sm font-extrabold text-white shadow-lg shadow-orange-500/30">
              ATA
            </div>

            <div>
              <p className="font-bold text-white">ATA AI</p>
              <p className="text-xs text-orange-200">
                University Assistant
              </p>
            </div>
          </Link>

          <nav className="flex items-center gap-2">
            <Link
              href="/"
              className="hidden rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-orange-300 sm:block"
            >
              Home
            </Link>

            <Link
              href="/dashboard"
              className="rounded-xl px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-orange-300"
            >
              Dashboard
            </Link>

            <Link
              href="/chat"
              className="rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/25 transition hover:bg-orange-600"
            >
              Ask ATA
            </Link>
          </nav>
        </div>
      </header>

      <section className="relative">
        <div className="absolute -left-32 top-20 h-80 w-80 rounded-full bg-orange-300/20 blur-3xl" />
        <div className="absolute -right-32 top-0 h-96 w-96 rounded-full bg-blue-300/20 blur-3xl" />

        <div className="relative mx-auto grid min-h-[600px] max-w-7xl items-center gap-12 px-5 py-12 lg:grid-cols-2 lg:px-8 lg:py-16">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-4 py-2 text-sm font-bold text-orange-600 shadow-sm">
              <span className="h-2 w-2 rounded-full bg-orange-500" />
              Official ATA University knowledge
            </div>

            <h1 className="max-w-2xl text-4xl font-extrabold leading-[1.08] tracking-tight text-[#0f172a] sm:text-5xl lg:text-[56px]">
              Your intelligent guide to{" "}
              <span className="text-orange-500">ATA University</span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Get fast, transparent and source-grounded answers about
              programmes, tuition fees, admissions, scholarships and
              university services.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/chat"
                className="inline-flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-orange-500 to-orange-600 px-7 py-4 text-base font-bold text-white shadow-xl shadow-orange-500/25 transition hover:-translate-y-1 hover:from-orange-600 hover:to-orange-700"
              >
                Start a Conversation
                <span aria-hidden="true">→</span>
              </Link>

              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center rounded-2xl border-2 border-[#0f172a] bg-white px-7 py-4 text-base font-bold text-[#0f172a] transition hover:-translate-y-1 hover:bg-[#0f172a] hover:text-white"
              >
                View Dashboard
              </Link>
            </div>

            <div className="mt-9 flex flex-wrap gap-x-7 gap-y-3 text-sm font-medium text-slate-600">
              <span className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-green-100 text-xs font-bold text-green-700">
                  ✓
                </span>
                Official sources
              </span>

              <span className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-orange-100 text-xs font-bold text-orange-700">
                  ✓
                </span>
                Multilingual
              </span>

              <span className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                  ✓
                </span>
                Transparent answers
              </span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-6 rounded-[40px] bg-gradient-to-r from-orange-300/30 to-blue-300/30 blur-2xl" />

            <div className="relative overflow-hidden rounded-[32px] border-2 border-orange-200 bg-white shadow-[0_30px_90px_rgba(15,23,42,0.18)]">
              <div className="flex items-center justify-between bg-[#0f172a] px-6 py-5 text-white">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500 font-extrabold shadow-lg shadow-orange-500/30">
                    A
                  </div>

                  <div>
                    <p className="font-bold">ATA University Assistant</p>
                    <p className="text-xs text-orange-200">
                      Official university knowledge
                    </p>
                  </div>
                </div>

                <span className="rounded-full bg-green-500 px-3 py-1 text-xs font-bold text-white">
                  Online
                </span>
              </div>

              <div className="space-y-6 p-6 sm:p-8">
                <div className="flex justify-end">
                  <div className="max-w-[80%] rounded-3xl rounded-br-md bg-gradient-to-br from-[#0f172a] to-[#1e3a5f] px-5 py-4 text-sm leading-7 text-white shadow-lg">
                    What is the tuition for Computer Engineering?
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="max-w-[90%] rounded-3xl rounded-bl-md border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-white px-5 py-5 shadow-md">
                    <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-orange-600">
                      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-200 text-orange-700">
                        A
                      </span>
                      ATA Assistant
                    </div>

                    <p className="text-sm leading-7 text-slate-700">
                      I found the relevant tuition information in the official
                      ATA University sources.
                    </p>

                    <div className="mt-5 rounded-2xl border-2 border-orange-200 bg-white p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="text-xs font-bold uppercase tracking-wide text-slate-400">
                            Source
                          </p>

                          <p className="mt-1 text-sm font-semibold text-[#0f172a]">
                            ATA University tuition information
                          </p>
                        </div>

                        <span className="rounded-full bg-orange-500 px-3 py-1 text-xs font-bold text-white">
                          Grounded
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border-2 border-orange-200 bg-white p-2 shadow-lg">
                  <div className="flex items-center gap-3">
                    <p className="flex-1 px-4 py-3 text-sm text-slate-400">
                      Ask about programmes, tuition, admissions...
                    </p>

                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 font-bold text-white shadow-lg shadow-orange-500/30">
                      ↑
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-orange-100 bg-white/80 py-14 backdrop-blur">
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-orange-600">
              Built for students
            </p>

            <h2 className="mt-3 text-3xl font-extrabold text-[#0f172a] sm:text-4xl">
              University information without the long search
            </h2>

            <p className="mt-4 text-base leading-7 text-slate-600">
              ATA AI combines semantic retrieval and official university
              content to provide clear, useful and traceable answers.
            </p>
          </div>

          <div className="mt-9 grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <article
                key={feature.title}
                className="group rounded-3xl border-2 border-orange-100 bg-gradient-to-br from-white to-orange-50 p-7 shadow-sm transition hover:-translate-y-2 hover:border-orange-300 hover:shadow-xl"
              >
                <div className="flex h-13 w-13 items-center justify-center rounded-2xl bg-[#0f172a] text-xl font-extrabold text-orange-400 shadow-lg">
                  {feature.icon}
                </div>

                <h3 className="mt-6 text-xl font-extrabold text-[#0f172a]">
                  {feature.title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  {feature.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="py-14">
        <div className="mx-auto grid max-w-7xl gap-12 px-5 lg:grid-cols-[0.9fr_1.1fr] lg:items-center lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-orange-600">
              Ask naturally
            </p>

            <h2 className="mt-3 text-3xl font-extrabold leading-tight text-[#0f172a] sm:text-4xl">
              Find the answers you need using simple questions
            </h2>

            <p className="mt-5 text-base leading-8 text-slate-600">
              You do not need to search through multiple university pages.
              Write your question naturally and the assistant will retrieve the
              most relevant ATA information.
            </p>

            <Link
              href="/chat"
              className="mt-7 inline-flex items-center gap-2 font-bold text-orange-600 transition hover:text-orange-700"
            >
              Open the assistant
              <span aria-hidden="true">→</span>
            </Link>
          </div>

          <div className="space-y-4">
            {exampleQuestions.map((question, index) => (
              <Link
                key={question}
                href={`/chat?question=${encodeURIComponent(question)}`}
                className="group flex items-center justify-between rounded-2xl border-2 border-orange-100 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:border-orange-400 hover:shadow-lg"
              >
                <div className="flex items-center gap-4">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-100 text-sm font-extrabold text-orange-600">
                    0{index + 1}
                  </span>

                  <span className="font-semibold text-[#0f172a]">
                    {question}
                  </span>
                </div>

                <span className="text-xl text-orange-500 transition group-hover:translate-x-1">
                  →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 pb-14 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-7 rounded-[32px] bg-[#0f172a] px-7 py-10 text-center text-white shadow-[0_30px_80px_rgba(15,23,42,0.25)] sm:px-10 lg:flex-row lg:text-left">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-orange-400">
              Ready to begin?
            </p>

            <h2 className="mt-3 text-3xl font-extrabold">
              Ask your first ATA University question
            </h2>

            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
              Explore programmes, admissions, tuition fees and university
              services with answers grounded in official content.
            </p>
          </div>

          <Link
            href="/chat"
            className="shrink-0 rounded-2xl bg-orange-500 px-7 py-4 font-bold text-white shadow-xl shadow-orange-500/25 transition hover:-translate-y-1 hover:bg-orange-600"
          >
            Start Chatting →
          </Link>
        </div>
      </section>

      <footer className="border-t border-orange-100 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-5 py-7 text-center text-sm text-slate-500 sm:flex-row sm:text-left lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#0f172a] text-xs font-extrabold text-orange-400">
              ATA
            </div>

            <span>ATA RAG University Assistant</span>
          </div>

          <p>Answers generated from official ATA University sources.</p>
        </div>
      </footer>
    </main>
  );
}