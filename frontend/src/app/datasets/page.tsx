"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Dataset = {
  id: number;
  name: string;
  description?: string | null;
  modality_type: string;
  created_at: string;
};

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchDatasets() {
      try {
        const res = await api.get("/datasets");
        setDatasets(res.data);
      } catch (err) {
        setError("Failed to load datasets.");
      } finally {
        setLoading(false);
      }
    }

    fetchDatasets();
  }, []);

  return (
    <main className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">Datasets</h1>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      <div className="space-y-4">
        {datasets.map((dataset) => (
          <div key={dataset.id} className="border rounded-xl p-4">
            <div className="font-semibold">
              {dataset.id}. {dataset.name}
            </div>
            <div className="text-sm text-gray-600">{dataset.description || "No description"}</div>
            <div className="text-sm mt-2">Modality: {dataset.modality_type}</div>
            <div className="text-sm">Created: {new Date(dataset.created_at).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </main>
  );
}