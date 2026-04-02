"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Job = {
  id: number;
  job_type: string;
  target_type: string;
  target_id?: number | null;
  status: string;
  params_json?: Record<string, unknown> | null;
  result_json?: Record<string, unknown> | null;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchJobs() {
    try {
      const res = await api.get("/jobs");
      setJobs(res.data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load jobs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchJobs();

    const timer = setInterval(() => {
      fetchJobs();
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  return (
    <main className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Jobs</h1>
        <button
          onClick={fetchJobs}
          className="rounded bg-black px-4 py-2 text-white"
        >
          Refresh
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      <div className="space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="rounded-xl border p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="font-semibold">
                Job #{job.id} · {job.job_type}
              </div>
              <div
                className={
                  job.status === "success"
                    ? "text-green-600 font-medium"
                    : job.status === "failed"
                    ? "text-red-600 font-medium"
                    : job.status === "running"
                    ? "text-yellow-600 font-medium"
                    : "text-gray-600 font-medium"
                }
              >
                {job.status}
              </div>
            </div>

            <div className="text-sm text-gray-700 space-y-1">
              <div>target_type: {job.target_type}</div>
              <div>target_id: {job.target_id ?? "N/A"}</div>
              <div>created_at: {new Date(job.created_at).toLocaleString()}</div>
              <div>
                started_at:{" "}
                {job.started_at ? new Date(job.started_at).toLocaleString() : "N/A"}
              </div>
              <div>
                finished_at:{" "}
                {job.finished_at ? new Date(job.finished_at).toLocaleString() : "N/A"}
              </div>
            </div>

            {job.params_json && (
              <div>
                <div className="text-sm font-medium mb-1">params_json</div>
                <pre className="rounded bg-gray-100 p-3 text-xs overflow-auto">
                  {JSON.stringify(job.params_json, null, 2)}
                </pre>
              </div>
            )}

            {job.result_json && (
              <div>
                <div className="text-sm font-medium mb-1">result_json</div>
                <pre className="rounded bg-gray-100 p-3 text-xs overflow-auto">
                  {JSON.stringify(job.result_json, null, 2)}
                </pre>
              </div>
            )}

            {job.error_message && (
              <div>
                <div className="text-sm font-medium mb-1 text-red-600">error_message</div>
                <pre className="rounded bg-red-50 p-3 text-xs overflow-auto text-red-700">
                  {job.error_message}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}