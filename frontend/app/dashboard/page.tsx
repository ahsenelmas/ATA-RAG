"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type DashboardStatistics = {
  total_documents: number;
  total_chunks: number;
  embedded_chunks: number;
  total_chat_messages: number;
  grounded_messages: number;
  grounded_rate: number;
  total_feedback: number;
  helpful_feedback: number;
  not_helpful_feedback: number;
  positive_feedback_rate: number;
  total_crawl_runs: number;
  total_crawl_errors: number;
  latest_crawl_at: string | null;
};

type RecentChat = {
  id: string;
  session_id: string;
  question: string;
  answer: string;
  language: string | null;
  is_answered: boolean;
  retrieval_score: number | null;
  confidence: number | null;
  latency_ms: number | null;
  created_at: string;
};

type RecentChatsResponse = {
  items: RecentChat[];
};

type FeedbackItem = {
  id: string;
  message_id: string;
  rating: string;
  comment: string | null;
  created_at: string;
  question: string;
  answer: string;
};

type FeedbackResponse = {
  items: FeedbackItem[];
};

type CrawlError = {
  id: string;
  url: string;
  error_type: string;
  error_message: string;
  created_at: string;
};

type CrawlRun = {
  id: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  pages_discovered: number;
  pages_processed: number;
  pages_failed: number;
  pages_updated: number;
  pages_unchanged: number;
  chunks_created: number;
  error_message: string | null;
  errors: CrawlError[];
};

type CrawlRunsResponse = {
  items: CrawlRun[];
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function percentage(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }

  const normalizedValue = value <= 1 ? value * 100 : value;

  return Math.min(100, Math.max(0, Math.round(normalizedValue)));
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Not available";
  }

  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatLatency(latencyMs: number | null): string {
  if (latencyMs === null) {
    return "—";
  }

  if (latencyMs < 1000) {
    return `${latencyMs} ms`;
  }

  return `${(latencyMs / 1000).toFixed(2)} s`;
}

export default function DashboardPage() {
  const [statistics, setStatistics] =
    useState<DashboardStatistics | null>(null);

  const [recentChats, setRecentChats] = useState<RecentChat[]>([]);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [crawlRuns, setCrawlRuns] = useState<CrawlRun[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [
        statisticsResponse,
        recentChatsResponse,
        feedbackResponse,
        crawlsResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/api/dashboard/statistics`, {
          cache: "no-store",
        }),
        fetch(`${API_URL}/api/dashboard/recent-chats?limit=8`, {
          cache: "no-store",
        }),
        fetch(`${API_URL}/api/dashboard/feedback?limit=6`, {
          cache: "no-store",
        }),
        fetch(`${API_URL}/api/dashboard/crawls?limit=5`, {
          cache: "no-store",
        }),
      ]);

      if (!statisticsResponse.ok) {
        throw new Error("Dashboard statistics could not be loaded.");
      }

      if (!recentChatsResponse.ok) {
        throw new Error("Recent chats could not be loaded.");
      }

      if (!feedbackResponse.ok) {
        throw new Error("Feedback data could not be loaded.");
      }

      if (!crawlsResponse.ok) {
        throw new Error("Crawl information could not be loaded.");
      }

      const statisticsData =
        (await statisticsResponse.json()) as DashboardStatistics;

      const recentChatsData =
        (await recentChatsResponse.json()) as RecentChatsResponse;

      const feedbackData =
        (await feedbackResponse.json()) as FeedbackResponse;

      const crawlsData =
        (await crawlsResponse.json()) as CrawlRunsResponse;

      setStatistics(statisticsData);
      setRecentChats(recentChatsData.items);
      setFeedback(feedbackData.items);
      setCrawlRuns(crawlsData.items);
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "An unexpected dashboard error occurred.";

      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  const groundedRate = percentage(statistics?.grounded_rate ?? 0);

  const positiveFeedbackRate = percentage(
    statistics?.positive_feedback_rate ?? 0,
  );

  const latestCrawl = crawlRuns[0] ?? null;

  const averageLatency =
    recentChats.length > 0
      ? Math.round(
          recentChats.reduce(
            (total, chat) => total + (chat.latency_ms ?? 0),
            0,
          ) /
            recentChats.filter((chat) => chat.latency_ms !== null)
              .length || 0,
        )
      : 0;

  const metrics = [
    {
      title: "Documents",
      value: formatNumber(statistics?.total_documents ?? 0),
      subtitle: "Official ATA pages",
      icon: "D",
    },
    {
      title: "Total Chunks",
      value: formatNumber(statistics?.total_chunks ?? 0),
      subtitle: "Knowledge-base chunks",
      icon: "C",
    },
    {
      title: "Embedded Chunks",
      value: formatNumber(statistics?.embedded_chunks ?? 0),
      subtitle: "Searchable vector records",
      icon: "E",
    },
    {
      title: "Questions",
      value: formatNumber(statistics?.total_chat_messages ?? 0),
      subtitle: "Stored chat messages",
      icon: "Q",
    },
    {
      title: "Grounded Rate",
      value: `${groundedRate}%`,
      subtitle: `${formatNumber(
        statistics?.grounded_messages ?? 0,
      )} grounded answers`,
      icon: "G",
    },
    {
      title: "Average Latency",
      value:
        averageLatency > 0
          ? formatLatency(averageLatency)
          : "—",
      subtitle: "From recent questions",
      icon: "T",
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#fff7ed] via-white to-[#eff6ff] text-[#0f172a]">
      <header className="border-b border-orange-300 bg-[#0f172a]/95 text-white shadow-xl backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-orange-500 text-sm font-extrabold text-white shadow-lg shadow-orange-500/30">
              ATA
            </div>

            <div>
              <p className="font-bold text-white">ATA AI</p>
              <p className="text-xs text-orange-200">
                RAG Dashboard
              </p>
            </div>
          </Link>

          <nav className="flex items-center gap-2">
            <Link
              href="/"
              className="hidden rounded-xl px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-orange-300 sm:block"
            >
              Home
            </Link>

            <Link
              href="/dashboard"
              className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-orange-300"
            >
              Dashboard
            </Link>

            <Link
              href="/chat"
              className="rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/25 transition hover:bg-orange-600"
            >
              Open Chat
            </Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-orange-600">
              Live system overview
            </p>

            <h1 className="mt-2 text-3xl font-extrabold text-[#0f172a] sm:text-4xl">
              ATA RAG Dashboard
            </h1>

            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
              Live knowledge-base statistics, recent chats,
              feedback and scraper activity.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-3 rounded-2xl border-2 border-green-200 bg-green-50 px-4 py-3 shadow-sm">
              <span className="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_0_5px_rgba(34,197,94,0.15)]" />

              <div>
                <p className="text-sm font-bold text-green-800">
                  System online
                </p>

                <p className="text-xs text-green-700">
                  Backend connected
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => void loadDashboard()}
              disabled={isLoading}
              className="rounded-2xl bg-[#0f172a] px-5 py-3 text-sm font-bold text-white shadow-lg transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Refreshing..." : "Refresh data"}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-7 rounded-3xl border-2 border-red-200 bg-red-50 p-5 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-bold text-red-800">
                  Dashboard data could not be loaded
                </p>

                <p className="mt-1 text-sm text-red-700">
                  {error}
                </p>
              </div>

              <button
                type="button"
                onClick={() => void loadDashboard()}
                className="rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-red-700"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        <div className="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {metrics.map((metric) => (
            <article
              key={metric.title}
              className="group rounded-3xl border-2 border-orange-100 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-orange-300 hover:shadow-xl"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-500">
                    {metric.title}
                  </p>

                  <p className="mt-3 text-4xl font-extrabold text-[#0f172a]">
                    {isLoading ? "..." : metric.value}
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    {metric.subtitle}
                  </p>
                </div>

                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#0f172a] text-lg font-extrabold text-orange-400 shadow-lg transition group-hover:bg-orange-500 group-hover:text-white">
                  {metric.icon}
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-3xl border-2 border-orange-100 bg-white p-6 shadow-sm sm:p-7">
            <div>
              <h2 className="text-xl font-extrabold text-[#0f172a]">
                Grounding and feedback
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Live answer quality and user feedback statistics
              </p>
            </div>

            <div className="mt-7 space-y-6">
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-700">
                    Grounded answers
                  </p>

                  <p className="text-sm font-extrabold text-[#0f172a]">
                    {groundedRate}%
                  </p>
                </div>

                <div className="h-3 overflow-hidden rounded-full bg-orange-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-orange-400 to-orange-600"
                    style={{ width: `${groundedRate}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-700">
                    Positive feedback
                  </p>

                  <p className="text-sm font-extrabold text-[#0f172a]">
                    {positiveFeedbackRate}%
                  </p>
                </div>

                <div className="h-3 overflow-hidden rounded-full bg-orange-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-green-400 to-green-600"
                    style={{
                      width: `${positiveFeedbackRate}%`,
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2 sm:grid-cols-4">
                <div className="rounded-2xl bg-green-50 p-4">
                  <p className="text-xs font-bold uppercase text-green-700">
                    Helpful
                  </p>

                  <p className="mt-2 text-2xl font-extrabold text-green-700">
                    {statistics?.helpful_feedback ?? 0}
                  </p>
                </div>

                <div className="rounded-2xl bg-red-50 p-4">
                  <p className="text-xs font-bold uppercase text-red-700">
                    Not helpful
                  </p>

                  <p className="mt-2 text-2xl font-extrabold text-red-700">
                    {statistics?.not_helpful_feedback ?? 0}
                  </p>
                </div>

                <div className="rounded-2xl bg-orange-50 p-4">
                  <p className="text-xs font-bold uppercase text-orange-700">
                    Feedback
                  </p>

                  <p className="mt-2 text-2xl font-extrabold text-orange-700">
                    {statistics?.total_feedback ?? 0}
                  </p>
                </div>

                <div className="rounded-2xl bg-blue-50 p-4">
                  <p className="text-xs font-bold uppercase text-blue-700">
                    Grounded
                  </p>

                  <p className="mt-2 text-2xl font-extrabold text-blue-700">
                    {statistics?.grounded_messages ?? 0}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-3xl bg-[#0f172a] p-6 text-white shadow-[0_25px_70px_rgba(15,23,42,0.2)] sm:p-7">
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-orange-400">
              Scraper status
            </p>

            <h2 className="mt-4 text-3xl font-extrabold">
              {latestCrawl?.status ?? "No crawl recorded"}
            </h2>

            <p className="mt-3 text-sm leading-7 text-slate-300">
              Latest crawl:{" "}
              {formatDate(
                latestCrawl?.started_at ??
                  statistics?.latest_crawl_at ??
                  null,
              )}
            </p>

            <div className="mt-7 grid grid-cols-2 gap-4">
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs uppercase text-slate-400">
                  Crawl runs
                </p>

                <p className="mt-2 text-2xl font-extrabold text-orange-400">
                  {statistics?.total_crawl_runs ?? 0}
                </p>
              </div>

              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs uppercase text-slate-400">
                  Crawl errors
                </p>

                <p className="mt-2 text-2xl font-extrabold text-red-400">
                  {statistics?.total_crawl_errors ?? 0}
                </p>
              </div>

              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs uppercase text-slate-400">
                  Pages processed
                </p>

                <p className="mt-2 text-2xl font-extrabold text-green-400">
                  {latestCrawl?.pages_processed ?? 0}
                </p>
              </div>

              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs uppercase text-slate-400">
                  Chunks created
                </p>

                <p className="mt-2 text-2xl font-extrabold text-blue-400">
                  {latestCrawl?.chunks_created ?? 0}
                </p>
              </div>
            </div>
          </section>
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <section className="overflow-hidden rounded-3xl border-2 border-orange-100 bg-white shadow-sm">
            <div className="border-b border-orange-100 px-6 py-5">
              <h2 className="text-xl font-extrabold text-[#0f172a]">
                Recent questions
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Latest questions stored by the backend
              </p>
            </div>

            {recentChats.length === 0 && !isLoading ? (
              <div className="px-6 py-10 text-center text-sm text-slate-500">
                No recent chat messages were found.
              </div>
            ) : (
              <div className="divide-y divide-orange-100">
                {recentChats.map((chat) => (
                  <article
                    key={chat.id}
                    className="px-6 py-5 transition hover:bg-orange-50"
                  >
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <p className="font-bold text-[#0f172a]">
                          {chat.question}
                        </p>

                        <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-600">
                          {chat.answer}
                        </p>

                        <div className="mt-3 flex flex-wrap gap-3 text-xs font-medium text-slate-500">
                          <span>
                            Language:{" "}
                            {(chat.language ?? "unknown").toUpperCase()}
                          </span>

                          <span>
                            Latency: {formatLatency(chat.latency_ms)}
                          </span>

                          <span>
                            Retrieval:{" "}
                            {chat.retrieval_score !== null
                              ? `${Math.round(
                                  chat.retrieval_score * 100,
                                )}%`
                              : "—"}
                          </span>

                          <span>{formatDate(chat.created_at)}</span>
                        </div>
                      </div>

                      <span
                        className={`w-fit shrink-0 rounded-full px-3 py-1 text-xs font-bold ${
                          chat.is_answered
                            ? "bg-green-100 text-green-700"
                            : "bg-orange-100 text-orange-700"
                        }`}
                      >
                        {chat.is_answered ? "Answered" : "Pending"}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-3xl border-2 border-orange-100 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-extrabold text-[#0f172a]">
              Latest feedback
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Most recent user ratings and comments
            </p>

            <div className="mt-6 space-y-4">
              {feedback.length === 0 && !isLoading ? (
                <div className="rounded-2xl bg-slate-50 p-5 text-sm text-slate-500">
                  No feedback has been submitted yet.
                </div>
              ) : (
                feedback.map((item) => (
                  <article
                    key={item.id}
                    className="rounded-2xl border-2 border-orange-100 bg-orange-50 p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-bold ${
                          item.rating.toLowerCase() === "helpful"
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {item.rating}
                      </span>

                      <span className="text-xs text-slate-400">
                        {formatDate(item.created_at)}
                      </span>
                    </div>

                    <p className="mt-3 text-sm font-bold text-[#0f172a]">
                      {item.question}
                    </p>

                    {item.comment && (
                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        {item.comment}
                      </p>
                    )}
                  </article>
                ))
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}