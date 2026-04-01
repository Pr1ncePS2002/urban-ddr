import os
import tempfile
import aiofiles
from .config import settings

JOB_STORE = {}

def get_base_dir() -> str:
    base = settings.local_storage_path
    if base.startswith("/tmp") and os.name == 'nt':
        base = os.path.join(tempfile.gettempdir(), "ddr_jobs")
    os.makedirs(base, exist_ok=True)
    return base

async def save_upload_async(job_id: str, prefix: str, upload_file) -> str:
    base = get_base_dir()
    filepath = os.path.join(base, f"{job_id}_{prefix}_{upload_file.filename}")
    
    content = await upload_file.read()
    async with aiofiles.open(filepath, 'wb') as out_file:
        await out_file.write(content)
        
    return filepath

async def save_result_async(job_id: str, pdf_bytes: bytes) -> str:
    base = get_base_dir()
    filepath = os.path.join(base, f"{job_id}_result.pdf")
    async with aiofiles.open(filepath, 'wb') as out_file:
        await out_file.write(pdf_bytes)
    return filepath

def get_result_path(job_id: str) -> str:
    base = get_base_dir()
    return os.path.join(base, f"{job_id}_result.pdf")

def cleanup_temp_files(job_id: str):
    base = get_base_dir()
    for f in os.listdir(base):
        if f.startswith(job_id) and not f.endswith("_result.pdf"):
            try:
                os.remove(os.path.join(base, f))
            except Exception:
                pass
