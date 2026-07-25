"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

type ChatSource = {
  title: string;
  section: string | null;
  url: string;
  similarity: number;
  final_score: number;
};

type ChatResponse = {
  message_id: string;
  session_id: string;
  answer: string;
  language: string;
  grounded: boolean;
  sources: ChatSource[];
};

type FeedbackRating = "helpful" | "not_helpful";

type FeedbackStatus =
  | "idle"
  | "sending"
  | "success"
  | "error";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  grounded?: boolean;
  sources?: ChatSource[];
  language?: string;
  feedback?: FeedbackRating;
  feedbackStatus?: FeedbackStatus;
};

const suggestedQuestions = [
  "What is the tuition for Computer Engineering?",
  "What are the admission requirements?",
  "Which programmes are available in English?",
  "How can I apply for a scholarship?",
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const initialQuestionSent = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(
    null,
  );

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>(
    [],
  );
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<
    string | null
  >(null);
  const [error, setError] = useState<string | null>(
    null,
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isLoading, error]);

  const sendQuestion = useCallback(
    async (submittedQuestion?: string) => {
      const finalQuestion = (
        submittedQuestion ?? question
      ).trim();

      if (!finalQuestion || isLoading) {
        return;
      }

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: finalQuestion,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
      ]);

      setQuestion("");
      setError(null);
      setIsLoading(true);

      try {
        const response = await fetch(
          `${API_URL}/api/chat`,
          {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              question: finalQuestion,
              language: null,
              retrieval_limit: 5,
              session_id: sessionId,
            }),
          },
        );

        if (!response.ok) {
          let errorMessage =
            "The assistant could not process your question.";

          try {
            const errorData = (await response.json()) as {
              detail?:
                | string
                | Array<{ msg?: string }>;
            };

            if (typeof errorData.detail === "string") {
              errorMessage = errorData.detail;
            } else if (
              Array.isArray(errorData.detail)
            ) {
              errorMessage =
                errorData.detail
                  .map((item) => item.msg)
                  .filter(Boolean)
                  .join(", ") || errorMessage;
            }
          } catch {
            // Keep the default error message.
          }

          throw new Error(errorMessage);
        }

        const data =
          (await response.json()) as ChatResponse;

        setSessionId(data.session_id);

        const assistantMessage: Message = {
          id: data.message_id,
          role: "assistant",
          content: data.answer,
          grounded: data.grounded,
          sources: data.sources,
          language: data.language,
          feedbackStatus: "idle",
        };

        setMessages((currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ]);
      } catch (requestError) {
        const errorMessage =
          requestError instanceof Error
            ? requestError.message
            : "An unexpected connection error occurred.";

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, question, sessionId],
  );

  useEffect(() => {
    const questionFromUrl =
      searchParams.get("question");

    if (
      !questionFromUrl ||
      initialQuestionSent.current
    ) {
      return;
    }

    initialQuestionSent.current = true;
    void sendQuestion(questionFromUrl);
  }, [searchParams, sendQuestion]);

  const handleSubmit = (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    void sendQuestion();
  };

  const clearConversation = () => {
    setMessages([]);
    setQuestion("");
    setSessionId(null);
    setError(null);
    initialQuestionSent.current = true;

    window.history.replaceState({}, "", "/chat");
  };

  const retryLastQuestion = () => {
    const lastUserMessage = [...messages]
      .reverse()
      .find(
        (message) => message.role === "user",
      );

    if (lastUserMessage) {
      void sendQuestion(lastUserMessage.content);
    }
  };

  const submitFeedback = async (
    messageId: string,
    rating: FeedbackRating,
  ) => {
    setMessages((currentMessages) =>
      currentMessages.map((message) =>
        message.id === messageId
          ? {
              ...message,
              feedbackStatus: "sending",
            }
          : message,
      ),
    );

    try {
      const response = await fetch(
        `${API_URL}/api/feedback`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message_id: messageId,
            rating,
            comment: null,
          }),
        },
      );

      if (!response.ok) {
        let errorMessage =
          "Feedback could not be submitted.";

        try {
          const errorData =
            (await response.json()) as {
              detail?: string;
            };

          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Keep the default error message.
        }

        throw new Error(errorMessage);
      }

      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === messageId
            ? {
                ...message,
                feedback: rating,
                feedbackStatus: "success",
              }
            : message,
        ),
      );
    } catch {
      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === messageId
            ? {
                ...message,
                feedbackStatus: "error",
              }
            : message,
        ),
      );
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#fff7ed] via-white to-[#eff6ff] text-[#0f172a]">
      <header className="border-b border-orange-300 bg-[#0f172a]/95 text-white shadow-xl backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Link
            href="/"
            className="flex items-center gap-3"
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-orange-500 text-sm font-extrabold text-white shadow-lg shadow-orange-500/30">
              ATA
            </div>

            <div>
              <p className="font-bold text-white">
                ATA AI
              </p>

              <p className="text-xs text-orange-200">
                University Assistant
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
              className="rounded-xl px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-orange-300"
            >
              Dashboard
            </Link>

            <button
              type="button"
              onClick={clearConversation}
              className="rounded-xl bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-orange-500/25 transition hover:bg-orange-600"
            >
              New Chat
            </button>
          </nav>
        </div>
      </header>

      <section className="mx-auto flex min-h-[calc(100vh-77px)] max-w-7xl flex-col px-5 py-6 lg:px-8">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-[#0f172a] sm:text-2xl">
                ATA University Assistant
              </h1>

              <span className="hidden rounded-full bg-green-500 px-3 py-1 text-xs font-bold text-white shadow-sm sm:inline">
                Online
              </span>
            </div>

            <p className="mt-1 text-sm text-slate-600">
              Answers grounded in official ATA
              University sources
            </p>
          </div>
        </div>

        <div className="flex flex-1 flex-col overflow-hidden rounded-3xl border-2 border-orange-200 bg-white shadow-[0_25px_70px_rgba(15,23,42,0.14)]">
          <div className="flex-1 overflow-y-auto px-5 py-7 sm:px-8">
            {messages.length === 0 ? (
              <div className="mx-auto flex min-h-[470px] max-w-3xl flex-col items-center justify-center text-center">
                <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-orange-400 to-orange-600 text-2xl text-white shadow-xl shadow-orange-500/30">
                  ✦
                </div>

                <p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-orange-600">
                  Official ATA knowledge
                </p>

                <h2 className="max-w-xl text-3xl font-extrabold leading-tight text-[#0f172a] sm:text-4xl">
                  How can I help you with ATA
                  University?
                </h2>

                <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
                  Ask about programmes, tuition
                  fees, admissions, scholarships and
                  university services.
                </p>

                <div className="mt-8 grid w-full grid-cols-1 gap-3 sm:grid-cols-2">
                  {suggestedQuestions.map(
                    (suggestedQuestion) => (
                      <button
                        key={suggestedQuestion}
                        type="button"
                        disabled={isLoading}
                        onClick={() =>
                          void sendQuestion(
                            suggestedQuestion,
                          )
                        }
                        className="group rounded-2xl border-2 border-orange-100 bg-gradient-to-r from-white to-orange-50 p-4 text-left text-sm font-semibold text-[#0f172a] transition hover:-translate-y-1 hover:border-orange-400 hover:bg-orange-100 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        <span className="flex items-start justify-between gap-3">
                          <span>
                            {suggestedQuestion}
                          </span>

                          <span className="text-orange-500 transition group-hover:translate-x-1">
                            →
                          </span>
                        </span>
                      </button>
                    ),
                  )}
                </div>
              </div>
            ) : (
              <div className="mx-auto flex max-w-3xl flex-col gap-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[90%] rounded-3xl px-5 py-4 text-sm leading-7 sm:max-w-[78%] ${
                        message.role === "user"
                          ? "rounded-br-md bg-gradient-to-br from-[#0f172a] to-[#1e3a5f] text-white shadow-lg"
                          : "rounded-bl-md border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-white text-slate-700 shadow-md"
                      }`}
                    >
                      {message.role ===
                        "assistant" && (
                        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-orange-600">
                            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-200 text-orange-700">
                              A
                            </span>

                            ATA Assistant
                          </div>

                          <span
                            className={`rounded-full px-3 py-1 text-xs font-bold ${
                              message.grounded
                                ? "bg-green-100 text-green-700"
                                : "bg-slate-200 text-slate-700"
                            }`}
                          >
                            {message.grounded
                              ? "Grounded"
                              : "Not grounded"}
                          </span>
                        </div>
                      )}

                      <p className="whitespace-pre-wrap">
                        {message.content}
                      </p>

                      {message.role ===
                        "assistant" &&
                        message.sources &&
                        message.sources.length >
                          0 && (
                          <div className="mt-5">
                            <p className="mb-3 text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                              Sources used ·{" "}
                              {
                                message.sources
                                  .length
                              }
                            </p>

                            <div className="space-y-3">
                              {message.sources.map(
                                (
                                  source,
                                  index,
                                ) => (
                                  <article
                                    key={`${message.id}-${source.url}-${index}`}
                                    className="rounded-2xl border-2 border-orange-200 bg-white p-4 shadow-sm"
                                  >
                                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                                      <div className="min-w-0">
                                        <p className="font-bold text-[#0f172a]">
                                          {
                                            source.title
                                          }
                                        </p>

                                        {source.section && (
                                          <p className="mt-1 text-xs font-medium text-slate-500">
                                            {
                                              source.section
                                            }
                                          </p>
                                        )}

                                        <p className="mt-2 text-xs text-slate-400">
                                          Relevance:{" "}
                                          {Math.round(
                                            source.final_score *
                                              100,
                                          )}
                                          %
                                        </p>
                                      </div>

                                      <a
                                        href={
                                          source.url
                                        }
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="shrink-0 rounded-xl bg-orange-100 px-3 py-2 text-xs font-bold text-orange-700 transition hover:bg-orange-500 hover:text-white"
                                      >
                                        Open source →
                                      </a>
                                    </div>
                                  </article>
                                ),
                              )}
                            </div>
                          </div>
                        )}

                      {message.role ===
                        "assistant" &&
                        (!message.sources ||
                          message.sources
                            .length === 0) && (
                          <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
                            <p className="text-xs font-semibold text-slate-500">
                              No source links were
                              returned for this answer.
                            </p>
                          </div>
                        )}

                      {message.role ===
                        "assistant" && (
                        <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-orange-100 pt-4">
                          <p className="text-xs font-semibold text-slate-500">
                            Was this answer helpful?
                          </p>

                          <button
                            type="button"
                            disabled={
                              message.feedbackStatus ===
                                "sending" ||
                              message.feedbackStatus ===
                                "success"
                            }
                            onClick={() =>
                              void submitFeedback(
                                message.id,
                                "helpful",
                              )
                            }
                            className={`rounded-xl px-3 py-2 text-xs font-bold transition ${
                              message.feedback ===
                              "helpful"
                                ? "bg-green-500 text-white"
                                : "bg-green-100 text-green-700 hover:bg-green-500 hover:text-white"
                            } disabled:cursor-not-allowed disabled:opacity-60`}
                          >
                            👍 Helpful
                          </button>

                          <button
                            type="button"
                            disabled={
                              message.feedbackStatus ===
                                "sending" ||
                              message.feedbackStatus ===
                                "success"
                            }
                            onClick={() =>
                              void submitFeedback(
                                message.id,
                                "not_helpful",
                              )
                            }
                            className={`rounded-xl px-3 py-2 text-xs font-bold transition ${
                              message.feedback ===
                              "not_helpful"
                                ? "bg-red-500 text-white"
                                : "bg-red-100 text-red-700 hover:bg-red-500 hover:text-white"
                            } disabled:cursor-not-allowed disabled:opacity-60`}
                          >
                            👎 Not helpful
                          </button>

                          {message.feedbackStatus ===
                            "sending" && (
                            <span className="text-xs font-medium text-slate-400">
                              Sending...
                            </span>
                          )}

                          {message.feedbackStatus ===
                            "success" && (
                            <span className="text-xs font-bold text-green-600">
                              Feedback saved
                            </span>
                          )}

                          {message.feedbackStatus ===
                            "error" && (
                            <span className="text-xs font-bold text-red-600">
                              Feedback could not be
                              saved
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="rounded-3xl rounded-bl-md border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-white px-5 py-4 shadow-md">
                      <div className="flex items-center gap-3 text-sm font-medium text-slate-700">
                        <div className="flex gap-1">
                          <span className="h-2 w-2 animate-bounce rounded-full bg-orange-500 [animation-delay:-0.3s]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-orange-500 [animation-delay:-0.15s]" />
                          <span className="h-2 w-2 animate-bounce rounded-full bg-orange-500" />
                        </div>

                        Searching official ATA
                        sources...
                      </div>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="rounded-3xl border-2 border-red-200 bg-red-50 p-5 shadow-sm">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-bold text-red-800">
                          The request could not be
                          completed
                        </p>

                        <p className="mt-1 text-sm leading-6 text-red-700">
                          {error}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={retryLastQuestion}
                        className="shrink-0 rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-red-700"
                      >
                        Try again
                      </button>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="border-t-2 border-orange-100 bg-gradient-to-r from-white via-orange-50 to-white px-4 py-4 sm:px-7">
            <form
              onSubmit={handleSubmit}
              className="mx-auto max-w-4xl"
            >
              <div className="flex items-end gap-3 rounded-2xl border-2 border-orange-200 bg-white p-2 shadow-lg transition focus-within:border-orange-500 focus-within:ring-4 focus-within:ring-orange-200">
                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value,
                    )
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();
                      void sendQuestion();
                    }
                  }}
                  rows={1}
                  maxLength={2000}
                  disabled={isLoading}
                  placeholder="Ask about programmes, tuition, admissions..."
                  className="max-h-32 min-h-12 flex-1 resize-none bg-transparent px-4 py-3 text-sm text-[#0f172a] outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
                />

                <button
                  type="submit"
                  disabled={
                    !question.trim() || isLoading
                  }
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 text-lg font-bold text-white shadow-lg shadow-orange-500/30 transition hover:scale-105 hover:from-orange-600 hover:to-orange-700 disabled:cursor-not-allowed disabled:from-slate-300 disabled:to-slate-300 disabled:shadow-none"
                  aria-label="Send question"
                >
                  ↑
                </button>
              </div>

              <div className="mt-3 flex flex-col items-center justify-between gap-1 text-xs text-slate-500 sm:flex-row">
                <p>
                  ATA AI uses official university
                  sources. Verify important
                  information from the provided
                  references.
                </p>

                <p>{question.length}/2000</p>
              </div>
            </form>
          </div>
        </div>
      </section>
    </main>
  );
}