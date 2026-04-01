import Link from "next/link";

export default function HomePage() {
  return (
    <main className="p-8 space-y-4">
      <h1 className="text-3xl font-bold">ShiftScope Console</h1>
      <p className="text-gray-600">Minimal frontend for dataset browsing and text search.</p>

      <div className="flex gap-4">
        <Link href="/datasets" className="underline">
          Datasets
        </Link>
        <Link href="/search" className="underline">
          Search
        </Link>
      </div>
    </main>
  );
}