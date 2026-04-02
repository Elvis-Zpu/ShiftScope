"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type SearchLog = {
  id: number;
  dataset_id: number;
  dataset_version_id: number;
  query_text: string;
  top_k: number;
  scorer: string;
  result_count: number;
  created_at: string;
};

export default function SearchLogsPage() {
  const [logs, setLogs] = useState<SearchLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchLogs() {
    try {
      const res = await api.get("/search-logs");
      setLogs(res.data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load search logs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <main className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Search Logs</h1>
        <button
          onClick={fetchLogs}
          className="rounded bg-black px-4 py-2 text-white"
        >
          Refresh
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      <div className="space-y-4">
        {logs.map((log) => (
          <div key={log.id} className="rounded-xl border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <div className="font-semibold">Search #{log.id}</div>
              <div className="text-sm text-gray-600">
                {new Date(log.created_at).toLocaleString()}
              </div>
            </div>

            <div className="text-sm">
              <strong>Query:</strong> {log.query_text}
            </div>
            <div className="text-sm">
              <strong>Dataset:</strong> {log.dataset_id}
            </div>
            <div className="text-sm">
              <strong>Dataset Version:</strong> {log.dataset_version_id}
            </div>
            <div className="text-sm">
              <strong>Top K:</strong> {log.top_k}
            </div>
            <div className="text-sm">
              <strong>Scorer:</strong> {log.scorer}
            </div>
            <div className="text-sm">
              <strong>Result Count:</strong> {log.result_count}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}