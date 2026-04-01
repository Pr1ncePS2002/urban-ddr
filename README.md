# DDR Generator

DDR Generator is a production-grade AI system that automates the creation of Detailed Diagnosis Reports for property inspections. By uploading an inspection report PDF and a thermal images report PDF, the application merges the data, runs visual analysis and deduplication models, detects data conflicts, and intelligently synthesizes a polished, professional DDR PDF utilizing WeasyPrint.

Built entirely using FastAPI and React/Vite, this system bypasses heavy asynchronous worker infrastructure (like Celery + Redis) by performing the background aggregation and processing entirely in-memory using `FastAPI BackgroundTasks`.

## Architecture

```text
  [ Frontend (Vercel) ]
          │
          ▼
    POST /api/generate (FastAPI)
          ├────────────────┬───────────────┐
          ▼                ▼               ▼
      State Store       Extract        LLM Provider
    (JOB_STORE Dict)   (PyMuPDF)        (Gemini/OpenAI) 
          │                │               │
  GET /api/job/{id} <─── Pipeline ◄────────┘
          │                ├── Vision Parsing
          ▼                ├── Merger & Deduplicator
   GET /api/download       ├── Conflict Detection
                           ├── Prompt Chain Gen
                           └── PDF Render (WeasyPrint)
```

## How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js 20+

### Backend Setup
1. `cd backend`
2. Configure `.env`: Copy `.env.example` to `.env` and specify `LOCAL_STORAGE_PATH=/tmp/ddr_jobs`
3. `pip install -r requirements.txt`
4. Start Server: `uvicorn app.main:app --reload`
*(The API runs at `http://localhost:8000`)*

### Frontend Setup
1. `cd frontend`
2. Configure `.env`: Copy `.env.example` to `.env` and set `VITE_API_URL=http://localhost:8000`
3. Process dependencies: `npm install`
4. Start App: `npm run dev`
*(The site runs at `http://localhost:5173`)*

## How to Deploy

### Backend Deployment (Render)
Connect your repository to Render as a Web Service. The configuration is entirely defined inside `render.yaml`.
- Environment Variable required: None (Defaults handled internally). `API_KEY` is passed directly per request.
- The service will rely on `uvicorn` and Python internally.

### Frontend Deployment (Vercel)
Connect your repository to Vercel. 
- Ensure `VITE_API_URL` is set to your deployed Render URL (e.g. `https://my-backend.onrender.com`).
- Vercel settings are strictly controlled via `vercel.json`.

## Changing Providers

A core feature of DDR Generator is the seamless Provider Abstraction Layer. You can swap models without altering backend code by changing the form submission fields.

`POST /api/generate` specific payload form overrides:
- `llm_provider`: String, either `gemini` (default) or `openai`
- `vision_provider`: String, either `gemini` (default) or `document_ai`
- `embed_provider`: String, either `gemini` (default) or `openai`

Zero backend python modification is necessary to switch to `openai`. The Factory model `get_llm_provider` will automatically route traffic and API credentials.

## API Reference

- `POST /api/generate`: Requires `api_key` string, `inspection_pdf` file, `thermal_pdf` file. Returns `{job_id, status_url}`.
- `GET /api/job/{job_id}`: Poll endpoint returning the current state of execution.
- `GET /api/download/{job_id}`: Used to download binary generated PDF.
- `GET /health`: Sanity check status point.

## Security

**Keys**: The API keys parsed from the request scope are **never** persisted to disk, pushed to logging contexts, or held in permanent memory boundaries. They flow directly into the configured AI provider context and evaporate after the background task terminates.

**Memory Store Warning**: The system tracks jobs via an in-memory dictionary. Backend restarts will purge completed and non-retrieved jobs.
