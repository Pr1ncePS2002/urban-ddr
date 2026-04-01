import logging
import traceback
from datetime import datetime
from .storage import JOB_STORE, cleanup_temp_files, save_result_async
from .providers.registry import get_llm_provider, get_embed_provider
from .pipeline.extractor import extract_pdf
from .pipeline.vision import analyze_images
from .pipeline.merger import merge_documents
from .pipeline.conflict import detect_conflicts
from .pipeline.deduplicator import collect_all_observations, deduplicate_observations, apply_deduped_observations
from .pipeline.report_gen import generate_ddr
from .pipeline.pdf_renderer import render_to_pdf

logger = logging.getLogger(__name__)

def update_job_status(job_id: str, status: str, progress: int = 0, error: str = None, result_url: str = None):
    job = JOB_STORE.get(job_id, {})
    job["status"] = status
    if progress:
        job["progress"] = progress
    if error is not None:
        job["error"] = error
    if result_url:
        job["result_url"] = result_url
    job["updated_at"] = datetime.utcnow()
    JOB_STORE[job_id] = job

async def generate_ddr_task(job_id: str, job_data: dict):
    """
    SECURITY NOTE: api_key is passed in job_data but NEVER logged, 
    stored to disk, or included in any error messages.
    """
    try:
        update_job_status(job_id, "extracting", 10)
        
        inspection_doc = extract_pdf(job_data["inspection_path"], "inspection")
        thermal_doc = extract_pdf(job_data["thermal_path"], "thermal")
        update_job_status(job_id, "analyzing_images", 25)
        
        llm = get_llm_provider(job_data["llm_provider"], job_data["api_key"])
        embed = get_embed_provider(job_data["embed_provider"], job_data["api_key"])
        
        inspection_doc = await analyze_images(inspection_doc, llm)
        thermal_doc = await analyze_images(thermal_doc, llm)
        update_job_status(job_id, "merging", 45)
        
        merged = merge_documents(inspection_doc, thermal_doc)
        merged = detect_conflicts(merged)
        all_obs = collect_all_observations(merged)
        deduped_obs = await deduplicate_observations(all_obs, embed, job_id)
        merged = apply_deduped_observations(merged, deduped_obs)
        update_job_status(job_id, "generating_report", 65)
        
        ddr = await generate_ddr(merged, llm, job_id)
        update_job_status(job_id, "rendering_pdf", 85)
        
        pdf_bytes = await render_to_pdf(ddr)
        
        await save_result_async(job_id, pdf_bytes)
        update_job_status(job_id, "complete", 100, result_url=f"/api/download/{job_id}")
        
    except Exception as e:
        api_key = job_data.get("api_key", "")
        safe_error = str(e).replace(api_key, "[REDACTED]") if api_key else str(e)
        logger.error(f"Job {job_id} failed: {safe_error}")
        update_job_status(job_id, "failed", error=safe_error)
        
    finally:
        cleanup_temp_files(job_id)
