import uuid
import os
import logging
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .models.schemas import HealthResponse, JobStatusResponse
from .worker import generate_ddr_task, JOB_STORE
from .storage import save_upload_async, get_result_path

app = FastAPI(title="DDR Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    # Covers Railway (*.up.railway.app) and Vercel (*.vercel.app) preview/prod URLs
    allow_origin_regex=r"https://.*\.(up\.railway\.app|vercel\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

@app.post("/api/generate", response_model=dict)
async def generate_report(
    background_tasks: BackgroundTasks,
    api_key: str = Form(None),
    inspection_pdf: UploadFile = File(...),
    thermal_pdf: UploadFile = File(...),
    llm_provider: str = Form(default="gemini"),
    vision_provider: str = Form(default="gemini"),
    embed_provider: str = Form(default="gemini"),
):
    valid_providers = {"gemini", "openai", "anthropic"}
    for field, value in [("llm_provider", llm_provider), ("embed_provider", embed_provider)]:
        if value not in valid_providers:
            raise HTTPException(400, f"Invalid {field}: {value!r}. Choose from: gemini, openai, anthropic.")
    if not api_key:
        raise HTTPException(400, "An API key is required. Please provide your Gemini, OpenAI, or Anthropic key.")

    if llm_provider == "gemini":
        for k in api_key.split(","):
            if not k.strip().startswith("AIza"):
                raise HTTPException(400, "Invalid Gemini API key format. Gemini keys start with 'AIza'.")
    
    for f in [inspection_pdf, thermal_pdf]:
        if not f.filename.endswith(".pdf"):
            raise HTTPException(400, f"{f.filename} must be a PDF")
        if f.size and f.size > 50 * 1024 * 1024:
            raise HTTPException(400, f"{f.filename} exceeds 50MB limit")
    
    job_id = str(uuid.uuid4())
    
    JOB_STORE[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "error": None,
        "result_url": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    inspection_path = await save_upload_async(job_id, "inspection", inspection_pdf)
    thermal_path = await save_upload_async(job_id, "thermal", thermal_pdf)
    
    job_data = {
        "api_key": api_key,         # NOTE: never logged, never persisted
        "inspection_path": inspection_path,
        "thermal_path": thermal_path,
        "llm_provider": llm_provider,
        "vision_provider": vision_provider,
        "embed_provider": embed_provider,
    }
    
    background_tasks.add_task(generate_ddr_task, job_id, job_data)
    
    return {"job_id": job_id, "status_url": f"/api/job/{job_id}"}

@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    status = JOB_STORE.get(job_id)
    if not status:
        raise HTTPException(404, "Job not found")
    return status

@app.get("/api/download/{job_id}")
async def download_report(job_id: str):
    path = get_result_path(job_id)
    if not path or not os.path.exists(path):
        raise HTTPException(404, "Report not ready")
    return FileResponse(
        path, 
        media_type="application/pdf",
        filename=f"DDR_Report_{job_id[:8]}.pdf"
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "version": "1.0.0"}
