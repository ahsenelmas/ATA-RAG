export default function DashboardPage() {
    return (
        <main className="min-h-screen bg-gray-50 p-6">
            <div className="mx-auto max-w-6xl">
                <h1 className="text-3xl font-bold text-gray-900">
                    ATA RAG Dashboard
                </h1>

                <div className="mt-6 grid gap-4 md:grid-cols-3">
                    <DashboardCard title="Documents" value="0" />
                    <DashboardCard title="Chunks" value="0" />
                    <DashboardCard title="Questions" value="0" />
                </div>
            </div>
        </main>
    );
}

function DashboardCard({
    title,
    value,
}: {
    title: string;
    value: string;
}) {
    return (
        <div className="rounded-xl border bg-white p-6">
            <p className="text-sm text-gray-500">{title}</p>
            <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
        </div>
    );
}
