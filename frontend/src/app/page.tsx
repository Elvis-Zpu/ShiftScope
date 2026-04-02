import Link from "next/link";

export default function HomePage() {
  return (
    <main className="p-8 space-y-4">
      <h1 className="text-3xl font-bold">ShiftScope Console</h1>
      <p className="text-gray-600">
        Minimal frontend for datasets, search, jobs, evaluation, and search logs.
      </p>

      <div className="flex gap-4">
        <Link href="/datasets" className="underline">Datasets</Link>
        <Link href="/search" className="underline">Search</Link>
        <Link href="/jobs" className="underline">Jobs</Link>
        <Link href="/eval" className="underline">Eval</Link>
        <Link href="/search-logs" className="underline">Search Logs</Link>
      </div>
    </main>
  );
}