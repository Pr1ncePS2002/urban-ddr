from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    # Note: This schema is for documentation only.
    # Actual endpoint uses Form() parameters due to file upload.
    api_key: str
    llm_provider: Literal["gemini", "openai"] = "gemini"
    vision_provider: Literal["gemini", "document_ai"] = "gemini"
    embed_provider: Literal["gemini", "openai"] = "gemini"

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued", "extracting", "analyzing_images", 
        "merging", "generating_report", "rendering_pdf",
        "complete", "failed"
    ]
    progress: int = 0           # 0-100
    error: Optional[str] = None # never contains api_key
    result_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class HealthResponse(BaseModel):
    status: str
    version: str

class ExtractedImage(BaseModel):
    page_num: int
    image_index: int
    image_bytes: bytes
    mime_type: str                  # "image/jpeg" or "image/png"
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1
    description: str = ""           # filled by vision.py
    area_tag: str = ""              # filled by vision.py e.g. "hall_ceiling"
    observation_tag: str = ""       # filled by vision.py e.g. "dampness"
    severity_hint: str = ""         # "good" | "moderate" | "poor" | "not_visible" | ""

class ExtractedPage(BaseModel):
    page_num: int
    text_blocks: list[str]          # all text on the page
    tables: list[list[list[str]]]   # list of tables, each table is rows of cells
    images: list[ExtractedImage]

class ExtractedDocument(BaseModel):
    doc_type: str  # "inspection" or "thermal"
    pages: list[ExtractedPage]

class AreaObservation(BaseModel):
    area: str                          # e.g. "Hall (Ground Floor)"
    negative_observations: list[str]   # dampness, seepage, etc.
    positive_observations: list[str]   # tile gaps, cracks (source causes)
    thermal_readings: list[dict]       # [{hotspot, coldspot, location, date}]
    images: list[ExtractedImage]       # all relevant images for this area
    severity: str                      # "good" | "moderate" | "poor"
    source_docs: list[str]             # ["inspection", "thermal"]

class MergedData(BaseModel):
    property_summary: str
    areas: list[AreaObservation]
    inspection_date: str               # "Not Available" if missing
    inspector_name: str                # "Not Available" if missing
    property_address: str              # "Not Available" if missing
    conflicts: list[str]              # list of conflict descriptions
    missing_fields: list[str]         # list of missing information items

class GeneratedDDR(BaseModel):
    property_issue_summary: str
    area_wise_observations: str
    probable_root_cause: str
    severity_assessment: str
    recommended_actions: str
    additional_notes: str
    missing_information: str
    images_by_area: dict[str, list[ExtractedImage]]  # area → images
    generated_at: datetime
    job_id: str
