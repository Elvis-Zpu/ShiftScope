"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type EvalRun = {
  id: number;
  dataset_id: number;
  dataset_version_id: number;
  run_name: string;
  scorer: string;
  top_k: number;
  metrics_json?: {
    num_queries?: number;
    hits_at_k?: number;
    recall_at_k?: number;
    mrr?: number;
  } | null;
  notes?: string | null;
  created_at: string;
};

type FailureCase = {
  id: number;
  eval_run_id: number;
  query_text: string;
  expected_item_key: string;
  failure_type: string;
  details_json?: Record<string, unknown> | null;
  created_at: string;
};

const defaultQueries = [
  { query: "red car", expected_item_key: "item-1" },
  { query: "white dog", expected_item_key: "item-2" },
  { query: "ramen egg", expected_item_key: "item-3" },
];

export default function EvalPage() {
  const [datasetId, setDatasetId] = useState("1");
  const [runName, setRunName] = useState("baseline-eval-ui");
  const [topK, setTopK] = useState("3");
  const [queriesText, setQueriesText] = useState(
    JSON.stringify(defaultQueries, null, 2)
  );

  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [failures, setFailures] = useState<FailureCase[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(true);
  const [runningEval, setRunningEval] = useState(false);
  const [error, setError] = useState("");

  async function fetchRuns() {
    try {
      const res = await api.get("/eval/runs");
      setRuns(res.data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load eval runs.");
    } finally {
      setLoadingRuns(false);
    }
  }

  async function fetchFailures(evalRunId: number) {
    try {
      const res = await api.get(`/eval/runs/${evalRunId}/failures`);
      setFailures(res.data);
      setSelectedRunId(evalRunId);
    } catch (err) {
      console.error(err);
      setError("Failed to load failure cases.");
    }
  }

  async function handleRunEval(e: React.FormEvent) {
    e.preventDefault();
    setRunningEval(true);
    setError("");

    try {
      const parsedQueries = JSON.parse(queriesText);

      await api.post("/eval/runs/text-baseline", {
        dataset_id: Number(datasetId),
        run_name: runName,
        top_k: Number(topK),
        queries: parsedQueries,
      });

      await fetchRuns();
    } catch (err) {
      console.error(err);
      setError("Failed to run evaluation. Check JSON format.");
    } finally {
      setRunningEval(false);
    }
  }

  useEffect(() => {
    fetchRuns();
  }, []);

  return (
    <main className="p-8 space-y-8">
      <h1 className="text-2xl font-bold">Evaluation</h1>

      <form onSubmit={handleRunEval} className="space-y-4 border rounded-xl p-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Dataset ID</label>
          <input
            value={datasetId}
            onChange={(e) => setDatasetId(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Run Name</label>
          <input
            value={runName}
            onChange={(e) => setRunName(e.target.value)}
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

        <div className="space-y-2">
          <label className="block text-sm font-medium">
            Queries JSON
          </label>
          <textarea
            value={queriesText}
            onChange={(e) => setQueriesText(e.target.value)}
            rows={12}
            className="border rounded px-3 py-2 w-full font-mono text-sm"
          />
        </div>

        <button
          type="submit"
          disabled={runningEval}
          className="rounded bg-black px-4 py-2 text-white"
        >
          {runningEval ? "Running..." : "Run Eval"}
        </button>
      </form>

      {error && <p className="text-red-600">{error}</p>}

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Eval Runs</h2>
          <button
            onClick={fetchRuns}
            className="rounded bg-black px-4 py-2 text-white"
          >
            Refresh
          </button>
        </div>

        {loadingRuns && <p>Loading...</p>}

        <div className="space-y-4">
          {runs.map((run) => (
            <div key={run.id} className="border rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="font-semibold">
                  Run #{run.id} · {run.run_name}
                </div>
                <button
                  onClick={() => fetchFailures(run.id)}
                  className="underline"
                >
                  View Failures
                </button>
              </div>

              <div className="text-sm text-gray-700 space-y-1">
                <div>dataset_id: {run.dataset_id}</div>
                <div>dataset_version_id: {run.dataset_version_id}</div>
                <div>scorer: {run.scorer}</div>
                <div>top_k: {run.top_k}</div>
                <div>created_at: {new Date(run.created_at).toLocaleString()}</div>
              </div>

              <pre className="rounded bg-gray-100 p-3 text-xs overflow-auto">
                {JSON.stringify(run.metrics_json, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">
          Failures {selectedRunId ? `(Run #${selectedRunId})` : ""}
        </h2>

        <div className="space-y-4">
          {failures.map((failure) => (
            <div key={failure.id} className="border rounded-xl p-4 space-y-2">
              <div className="font-semibold">
                {failure.failure_type}
              </div>
              <div className="text-sm">query_text: {failure.query_text}</div>
              <div className="text-sm">
                expected_item_key: {failure.expected_item_key}
              </div>
              <pre className="rounded bg-gray-100 p-3 text-xs overflow-auto">
                {JSON.stringify(failure.details_json, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}