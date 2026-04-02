# ShiftScope: End-to-End Multimodal Retrieval Infrastructure

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-blue)
![Redis](https://img.shields.io/badge/Redis-queue-red)
![MinIO](https://img.shields.io/badge/MinIO-object--storage-orange)
![Next.js](https://img.shields.io/badge/Next.js-frontend-black)
![Status](https://img.shields.io/badge/status-active-success)

ShiftScope is an end-to-end infrastructure system for multimodal retrieval. It supports the full retrieval lifecycle: dataset ingestion, versioned storage, asynchronous artifact generation, index construction, online search, offline evaluation, and failure analysis.

The project is designed around a simple principle:

> Retrieval systems should not only return results.  
> They should also be reproducible, traceable, and diagnosable.

Unlike a simple search demo, ShiftScope treats dataset lineage, asynchronous pipelines, evaluation runs, and failure cases as first-class system entities.

---

## Demo

### Current UI
- **Datasets**: inspect datasets and uploaded versions
- **Search**: run text-based retrieval over the latest registered index
- **Jobs**: monitor asynchronous embedding/index jobs
- **Eval**: launch evaluation runs and inspect failure cases

### Screenshots
_To be added later_

```text
docs/screenshots/datasets.png
docs/screenshots/search.png
docs/screenshots/jobs.png
docs/screenshots/eval.png
Demo Flow
Create a dataset
Upload a dataset version
Submit embedding and index jobs
Run text search
Launch evaluation
Inspect metrics and failures
Project Motivation

Many small AI retrieval projects stop at “the model can search.”
ShiftScope is built to answer a harder question:

Which dataset version produced this result?
Which index artifact is currently active?
How do retrieval results change after rebuilding the index?
Which query types systematically fail?
How can retrieval behavior be inspected instead of guessed?

ShiftScope exists to make retrieval systems operationally legible.

Solution Architecture
Core Pipeline
1. Create Dataset
   ↓
2. Upload Dataset Version
   ↓
3. Store raw file in MinIO
   ↓
4. Parse file into DataItem rows
   ↓
5. Submit asynchronous embedding job
   ↓
6. Generate embedding artifact
   ↓
7. Submit asynchronous index job
   ↓
8. Build index artifact and register Index
   ↓
9. Run online retrieval via /search/text
   ↓
10. Log search events
   ↓
11. Launch offline evaluation run
   ↓
12. Store metrics and failure cases
   ↓
13. Inspect results through frontend console
Design Goals
Versioned Data Flow
All retrieval results should be traceable to concrete dataset and index artifacts.
Asynchronous Processing
Expensive stages are executed as jobs rather than synchronous API calls.
Evaluation-Aware Retrieval
Retrieval quality is measured through evaluation runs instead of hand-picked examples.
Failure-Centric Analysis
The system stores failure cases to support structured debugging and iteration.
Technical Implementation
Technology Stack
Backend: FastAPI, SQLAlchemy
Database: PostgreSQL
Object Storage: MinIO
Task Queue: Redis + Celery
Frontend: Next.js, TypeScript, Tailwind CSS
Local Deployment: Docker Compose
Current Retrieval Strategy

The current system uses a lightweight lexical baseline:

uploaded dataset versions are parsed into DataItem rows;
index jobs build a JSON-based lexical index artifact;
/search/text loads the latest registered index artifact;
query terms are matched against indexed tokens and ranked by overlap.

This baseline is intentionally simple. It establishes the infrastructure loop first, so the retrieval backend can later be upgraded to dense embeddings and FAISS without changing the surrounding platform design.

Repository Structure
ShiftScope/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── datasets.py
│   │   │   ├── dataset_versions.py
│   │   │   ├── jobs.py
│   │   │   ├── indexes.py
│   │   │   ├── search.py
│   │   │   └── eval.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   │   ├── dataset.py
│   │   │   ├── dataset_version.py
│   │   │   ├── data_item.py
│   │   │   ├── job.py
│   │   │   ├── index.py
│   │   │   ├── search_log.py
│   │   │   ├── eval_run.py
│   │   │   └── failure_case.py
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workers/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── datasets/
│       │   ├── search/
│       │   ├── jobs/
│       │   └── eval/
│       └── lib/
│           └── api.ts
├── infra/
│   └── docker-compose.yml
├── docs/
│   ├── design.md
│   └── screenshots/
└── README.md
API Surface
Dataset Management
POST /datasets — create a dataset
GET /datasets — list datasets
GET /datasets/{id} — retrieve dataset metadata
Dataset Versions and Ingestion
POST /datasets/{dataset_id}/versions — upload a new dataset version
GET /datasets/{dataset_id}/versions — list versions
GET /datasets/{dataset_id}/items — list parsed items from the latest dataset version
Asynchronous Jobs
POST /jobs/embed — submit embedding artifact generation job
POST /jobs/index — submit index construction job
GET /jobs — list jobs
GET /jobs/{job_id} — inspect a single job
Index Management
GET /indexes — list registered index artifacts
Retrieval
POST /search/text — run text retrieval over the latest index
Evaluation
POST /eval/runs/text-baseline — run evaluation on a query set
GET /eval/runs — list evaluation runs
GET /eval/runs/{id} — get a single evaluation run
GET /eval/runs/{id}/failures — inspect failure cases
Data Model
Core Data Layer
Dataset
└── DatasetVersion
    └── DataItem
Processing and Evaluation Layer
Job
Index
SearchLog
EvalRun
FailureCase
Artifact Flow
Dataset Upload
    ↓
DatasetVersion
    ↓
DataItem Parsing
    ↓
Embed Job
    ↓
Embedding Artifact
    ↓
Index Job
    ↓
Index Artifact + Index Record
    ↓
Search API
    ↓
SearchLog
    ↓
EvalRun
    ↓
FailureCase
Frontend Console

ShiftScope currently provides a minimal engineering console with four pages:

Datasets — browse datasets and uploaded versions
Search — run retrieval queries and inspect returned results
Jobs — monitor asynchronous pipeline execution
Eval — launch evaluation runs and inspect failures

The frontend is intentionally simple. It is designed to expose system behavior rather than optimize for visual polish.

Example Dataset Format

Current dataset version uploads expect a JSON list of items:

[
  {
    "item_key": "item-1",
    "text_content": "A red vintage car parked on a quiet street.",
    "image_path": "images/car1.jpg",
    "metadata_json": {
      "category": "vehicle",
      "color": "red"
    },
    "split": "index"
  },
  {
    "item_key": "item-2",
    "text_content": "A small white dog sitting on a wooden chair.",
    "image_path": "images/dog1.jpg",
    "metadata_json": {
      "category": "animal",
      "color": "white"
    },
    "split": "index"
  }
]
Getting Started
1. Clone the repository
git clone <your-repo-url>
cd ShiftScope
2. Start infrastructure services
docker compose -f infra/docker-compose.yml up -d

This starts:

PostgreSQL
Redis
MinIO
3. Start backend
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload

Backend will be available at:

http://127.0.0.1:8000
http://127.0.0.1:8000/docs
4. Start Celery worker
cd backend
# activate venv first
celery -A app.workers.celery_app.celery_app worker --loglevel=info -P solo
5. Start frontend
cd frontend
npm install
npm run dev

Frontend will be available at:

http://localhost:3000
6. Open MinIO console
http://localhost:9001

Default credentials:

username: minioadmin
password: minioadmin