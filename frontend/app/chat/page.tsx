export default function ChatPage() {
    return (
        <main className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-4xl">
                <h1 className="text-3xl font-bold text-gray-900">ATA Chat</h1>

                <div className="mt-6 min-h-[500px] rounded-xl border bg-white p-6">
                    <p className="text-gray-500">
                        Chat messages will appear here.
                    </p>
                </div>

                <div className="mt-4 flex gap-3">
                    <input
                        type="text"
                        placeholder="Ask a question about AkademiaTA..."
                        className="flex-1 rounded-lg border px-4 py-3"
                    />

                    <button
                        type="button"
                        className="rounded-lg bg-gray-900 px-6 py-3 text-white"
                    >
                        Send
                    </button>
                </div>
            </div>
        </main>
    );
}
