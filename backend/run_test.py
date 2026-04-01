import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.worker import generate_ddr_task, JOB_STORE

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
api_key = os.environ.get("GOOGLE_API_KEY")

async def test_job():
    job_id = "test_job_123"
    
    # Needs to match main loop behavior
    # Mock JOB_STORE initialized state
    JOB_STORE[job_id] = {
        "job_id": job_id, "status": "queued", "progress": 0
    }
    
    job_data = {
        "api_key": api_key,
        "inspection_path": r"..\test\Sample Report.pdf",
        "thermal_path": r"..\test\Thermal Images.pdf",
        "llm_provider": "gemini",
        "vision_provider": "gemini",
        "embed_provider": "gemini"
    }
    print("Starting generator sequence...")
    await generate_ddr_task(job_id, job_data)
    
    status = JOB_STORE.get(job_id)
    print(f"Final End-to-End Status: {status}")

if __name__ == "__main__":
    asyncio.run(test_job())
