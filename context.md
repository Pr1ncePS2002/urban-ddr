# Project Context: DDR Generator

## Executive Summary
DDR Generator is a production-grade AI system that automates the creation of Detailed Diagnosis Reports (DDR) for property inspections. The application processes and merges an inspection report PDF along with a thermal images report PDF, performs visual analysis, removes duplicate observations using embeddings/LLMs, detects data conflicts, and intelligently synthesizes a polished, professional DDR PDF utilizing WeasyPrint.

## High-Level Architecture
The system consists of two primary applications:
1. **Frontend (React/Vite)**
2. **Backend (FastAPI)**

The backend is built around a lightweight, asynchronous job-processing architecture using `FastAPI BackgroundTasks` alongside an in-memory state store (`JOB_STORE`) to eliminate the need for heavy external queues like Celery or Redis.

### System Flow
1. **Upload**: User uploads two PDFs via the frontend (Vite/React).
2. **Accept (Job Queueing)**: FastAPI backend validates files and API keys, stores metadata in an in-memory `JOB_STORE` dictionary, creates a background task, and returns a tracking `job_id`.
3. **Pipeline Execution (Background task)**:
   - *Extraction*: Text, images, and tabular data extracted via `PyMuPDF` and `pdfplumber`.
   - *Vision Analysis*: LLM capabilities employed to interpret embedded inspection and thermal images.
   - *Merger & Deduplication*: Information is merged between the two documents. Semantic deduplication is executed via ChromaDB and LLM embedding providers.
   - *Conflict Detection*: Analyzes conflicting metrics or visual indications.
   - *Generation & Render*: The final report structure is generated via the LLM and rendered to PDF utilizing `weasyprint`.
4. **Polling/Download**: The frontend continuously polls `/api/job/{job_id}` until completion, then fetches the document.

## Codebase Structure
The project is rooted at `c:\Users\psing\Desktop\Urban`.

### `/backend`
- `app/main.py`: The FastAPI server entry point. Defines CORS, `/api/generate`, `/api/job/{}`, and `/api/download/{}` endpoints.
- `app/worker.py`: Contains the `generate_ddr_task` function orchestrating the core pipeline steps sequentially.
- `app/models/schemas.py`: Pydantic object schemas governing data exchange and validation.
- `app/pipeline/`: Contains all modular logical blocks for document processing: `extractor.py`, `vision.py`, `merger.py`, `conflict.py`, `deduplicator.py`, `report_gen.py`, `pdf_renderer.py`.
- `app/providers/`: Encapsulates AI providers in an interchangeable Factory pattern (`registry.py`, `base.py`, `gemini.py`, `openai_provider.py`). Support for Gemini and OpenAI allows swapping models without altering the pipeline logic.
- `requirements.txt`: Key libraries include `fastapi`, `google-generativeai`, `openai`, `PyMuPDF`, `pdfplumber`, `chromadb`, and `weasyprint`.

### `/frontend`
- React template powered by Vite (`package.json`, `vite.config.js`). 
- Core view located in `/src` featuring interactive components like `UploadForm.jsx`, `ReportViewer.jsx`, `JobStatus.jsx`, and `ProviderBadge.jsx`.
- Styles generally powered by vanilla setups (`index.css`), adhering to a modern frontend application flow.

## Deployment Details
- **Backend**: Can be deployed as a Render Web Service (configured via `render.yaml`).
- **Frontend**: Suited for Vercel deployment (configured via `vercel.json`). Contains rules to proxy or rewrite routes to the API depending on CORS configurations.
- **Security**: Raw API Keys are transmitted from the frontend via the request form. The backend parses but **never persists** these keys; they are passed down through memory explicitly, preventing keys from landing in permanent stores or logs.

## Setup Instructions
1. Run backend by configuring `.env` locally (from `.env.example`).
2. Utilize `pip install -r requirements.txt` and launch the API locally on port 8000 via Uvicorn.
3. Configure frontend `.env` with `VITE_API_URL`, run `npm install`, and launch the web server on port 5173.
