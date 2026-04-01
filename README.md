# DDR Generator

**DDR Generator** is a production-grade AI system that automates the creation of **Detailed Diagnosis Reports (DDR)** for property inspections. Upload an inspection report PDF and a thermal imaging PDF — the system handles everything else: visual analysis, conflict detection, semantic deduplication, and professional PDF generation.

Built with **FastAPI** (backend) and **React + Vite** (frontend), the system is designed around a bring-your-own-key model — users supply their own API key at runtime. No keys are ever stored.

---

## What Problem Does It Solve?

Property inspectors produce two separate documents: a written inspection report and a thermal imaging report. Manually cross-referencing these, removing duplicate observations, and writing a unified diagnosis is time-consuming and error-prone.

DDR Generator automates this entire workflow in under a few minutes using large language models and computer vision.

---

## How It Works — The 7-Stage Pipeline

Every report generation job runs through a fully async pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                        DDR Pipeline                             │
│                                                                 │
│  1. EXTRACT      PyMuPDF + pdfplumber parse text & images       │
│       ↓          from both uploaded PDFs                        │
│  2. ANALYZE      Vision LLM describes every thermal &           │
│       ↓          inspection image in natural language           │
│  3. MERGE        Inspection + thermal documents are             │
│       ↓          combined into a unified structure              │
│  4. CONFLICTS    Contradictions between the two reports         │
│       ↓          are automatically flagged                      │
│  5. DEDUPLICATE  ChromaDB vector similarity removes             │
│       ↓          duplicate observations (threshold: 0.85)       │
│  6. GENERATE     LLM synthesises the final DDR narrative        │
│       ↓          from the cleaned, merged data                  │
│  7. RENDER       WeasyPrint produces a styled, downloadable     │
│                  PDF report                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
  [ React Frontend ]
         │
         │  POST /api/generate (multipart form: pdfs + api_key)
         ▼
  [ FastAPI Backend ]
         │
         ├──► JOB_STORE (in-memory state)
         │
         └──► BackgroundTask
                   │
                   ├── extract_pdf()          ← PyMuPDF / pdfplumber
                   ├── analyze_images()       ← Vision LLM
                   ├── merge_documents()      ← Merger
                   ├── detect_conflicts()     ← Conflict engine
                   ├── deduplicate_obs()      ← ChromaDB embeddings
                   ├── generate_ddr()         ← LLM prompt chain
                   └── render_to_pdf()        ← WeasyPrint

  [ Frontend polls GET /api/job/{id} every 3s ]
  [ Downloads result via GET /api/download/{id} ]
```

---

## Provider Abstraction Layer

A core design principle is that **no pipeline code knows which AI provider it is talking to**. All providers implement the same abstract interface:

```python
class AbstractLLMProvider:
    async def complete(prompt, system) -> str
    async def complete_with_image(prompt, image_bytes, mime_type, system) -> str

class AbstractEmbedProvider:
    async def embed_texts(texts) -> list[list[float]]
    async def embed_image(image_bytes, mime_type) -> list[float]
```

### Supported Providers

| Role | Gemini | OpenAI | Anthropic |
|---|---|---|---|
| LLM (text) | `gemini-2.0-flash` | `gpt-4o` | `claude-3-5-sonnet-20241022` |
| LLM (vision) | ✓ | ✓ | ✓ |
| Embeddings | `text-embedding-004` | `text-embedding-3-small` | ✗ (delegates to Gemini/OpenAI) |

Switching providers requires **zero backend code changes** — users select their provider in the UI and supply the matching key.

### Anthropic Embedding Strategy

Anthropic has no native embedding API. When Anthropic is selected as the LLM provider, the system uses a **describe-then-embed** strategy: Claude describes the image in natural language, and then a Gemini or OpenAI embedding model vectorises that description.

---

## Multi-Key Round-Robin Retry

The backend implements `RoundRobinLLMProvider` and `RoundRobinEmbedProvider`. You can supply multiple comma-separated API keys (e.g. `AIza...,AIza...`). The system:

1. Distributes requests across all keys in rotation
2. Detects `429 / quota exhausted / rate limit` errors automatically
3. Skips to the next key without failing the job
4. After all keys in a cycle are exhausted, backs off for **33 seconds** then retries
5. Retries up to **5× per key** before giving up

This makes the system resilient to free-tier quota limits across multiple accounts.

> **Recommendation:** Use a **paid API key**. A 20-page DDR report makes 30–80+ LLM calls and dozens of embedding calls. Free-tier keys will hit quota limits mid-pipeline and cause the job to fail.

---

## API Key Security

- Keys are transmitted over HTTPS and held **in-memory only** for the duration of the job
- Never written to disk, never logged, never stored in any database
- If an error occurs, the key is automatically **redacted** from the error message before it reaches any log
- Jobs expire from memory after **1 hour** (configurable via `job_ttl_seconds`)

---

## API Reference

### `POST /api/generate`
Starts a new report generation job.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `api_key` | string | ✓ | Your Gemini, OpenAI, or Anthropic API key |
| `inspection_pdf` | file | ✓ | Inspection report PDF (max 50 MB) |
| `thermal_pdf` | file | ✓ | Thermal images PDF (max 50 MB) |
| `llm_provider` | string | — | `gemini` (default), `openai`, `anthropic` |
| `vision_provider` | string | — | `gemini` (default), `openai`, `anthropic` |
| `embed_provider` | string | — | `gemini` (default), `openai` |

**Response:**
```json
{ "job_id": "uuid", "status_url": "/api/job/uuid" }
```

---

### `GET /api/job/{job_id}`
Poll for job progress.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "extracting | analyzing_images | merging | generating_report | rendering_pdf | complete | failed",
  "progress": 65,
  "error": null,
  "result_url": "/api/download/uuid"
}
```

---

### `GET /api/download/{job_id}`
Download the generated PDF report. Returns `application/pdf`.

---

### `GET /health`
Health check endpoint. Returns `{ "status": "ok", "version": "1.0.0" }`.

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 20+

### Backend

```bash
cd backend
cp .env.example .env          # set LOCAL_STORAGE_PATH=/tmp/ddr_jobs
pip install -r requirements.txt
uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend
cp .env.example .env          # set VITE_API_URL=http://localhost:8000
npm install
npm run dev
# UI available at http://localhost:5173
```

---

## Configuration Reference

All backend settings live in `backend/app/config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEYS` | `None` | Comma-separated Gemini keys (server-side fallback) |
| `OPENAI_API_KEY` | `None` | OpenAI key (server-side fallback) |
| `ANTHROPIC_API_KEY` | `None` | Anthropic key (server-side fallback) |
| `GEMINI_LLM_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `OPENAI_LLM_MODEL` | `gpt-4o` | OpenAI model name |
| `ANTHROPIC_LLM_MODEL` | `claude-3-5-sonnet-20241022` | Anthropic model name |
| `DEDUP_SIMILARITY_THRESHOLD` | `0.85` | ChromaDB cosine similarity cutoff |
| `MAX_PDF_SIZE_MB` | `50` | Maximum upload size per file |
| `JOB_TTL_SECONDS` | `3600` | How long completed jobs stay in memory |
| `LOCAL_STORAGE_PATH` | `/tmp/ddr_jobs` | Where uploaded and result files are stored |

Server-side keys are optional — if not set, users must supply their own key via the UI. User-supplied keys always take priority over server-side keys.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Lucide Icons |
| Backend | FastAPI, Python 3.11, Uvicorn |
| PDF Parsing | PyMuPDF, pdfplumber |
| PDF Rendering | WeasyPrint |
| Vector Store | ChromaDB |
| LLM / Vision | Google Gemini, OpenAI GPT-4o, Anthropic Claude |
| Image Processing | Pillow |
| HTTP Client | httpx, aiofiles |

---

## Known Limitations

- **In-memory job store** — `JOB_STORE` is a Python dict. Backend restarts will purge all in-progress and completed jobs. For production scale, replace with Redis.
- **Single process** — Background tasks run inside the FastAPI process. For high concurrency, move to Celery + Redis workers.
- **Ephemeral storage** — Result PDFs are stored in `/tmp`. On platforms with ephemeral filesystems (most cloud containers), files are lost on restart. Mount a persistent volume or use GCS/S3.
- **Anthropic embeddings** — Anthropic has no embedding API; a Gemini or OpenAI key is required for the embed step when using Anthropic as the LLM.
