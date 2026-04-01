"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type SearchResultItem = {
  item_id: number;
  item_key: string;
  text_content?: string | null;
  image_path?: string | null;
  metadata_json?: Record<string, unknown> | null;
  score: number;
};

type SearchResponse = {
  query: string;
  dataset_id: number;
  dataset_version_id: number;
  scorer: string;
  top_k: number;
  results: SearchResultItem[];
};

export default function SearchPage() {
  const [datasetId, setDatasetId] = useState("1");
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState("3");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<SearchResponse | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await api.post("/search/text", {
        dataset_id: Number(datasetId),
        query,
        top_k: Number(topK),
      });
      setResult(res.data);
    } catch (err) {
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">Text Search</h1>

      <form onSubmit={handleSearch} className="space-y-4 border rounded-xl p-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Dataset ID</label>
          <input
            value={datasetId}
            onChange={(e) => setDatasetId(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Query</label>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. red car"
            className="border rounded px-3 py-2 w-full"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Top K</label>
          <input
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          />
        </div>

        <button
          type="submit"
          className="rounded bg-black text-white px-4 py-2"
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p className="text-red-600">{error}</p>}

      {result && (
        <section className="space-y-4">
          <div className="border rounded-xl p-4">
            <div><strong>Scorer:</strong> {result.scorer}</div>
            <div><strong>Dataset Version:</strong> {result.dataset_version_id}</div>
            <div><strong>Returned:</strong> {result.results.length}</div>
          </div>

          <div className="space-y-4">
            {result.results.map((item) => (
              <div key={item.item_id} className="border rounded-xl p-4">
                <div className="font-semibold">
                  {item.item_key} (score: {item.score})
                </div>
                <div className="text-sm mt-2">{item.text_content}</div>
                <div className="text-sm text-gray-600 mt-2">
                  image_path: {item.image_path || "N/A"}
                </div>
                <pre className="text-xs mt-3 bg-gray-100 p-3 rounded overflow-auto">
                  {JSON.stringify(item.metadata_json, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}