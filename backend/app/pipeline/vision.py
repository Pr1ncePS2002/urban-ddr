import json
import logging
import asyncio
from ..models.schemas import ExtractedDocument, ExtractedImage
from ..providers.base import AbstractLLMProvider

logger = logging.getLogger(__name__)

# Semaphore to cap concurrent requests
_vision_semaphore = asyncio.Semaphore(4)

async def _analyze_single_image(img: ExtractedImage, doc_type: str, system_prompt: str, provider: AbstractLLMProvider):
    try:
        async with _vision_semaphore:
            logger.info(f"Analyzing {doc_type} image {img.image_index} layout with Vision Model...")
            response_text = await provider.complete_with_image(
                prompt="Analyze this image and return the required JSON.",
                image_bytes=img.image_bytes,
                mime_type=img.mime_type,
                system=system_prompt
            )
            # Short sleep to prevent flooding all 4 keys instantly when moving to next batch
            await asyncio.sleep(2)
        
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
        
        data = json.loads(response_text.strip())
        
        img.description = data.get("description", "")
        img.area_tag = data.get("area_tag", "")
        img.observation_tag = data.get("observation_tag", "")
        
        sev = data.get("severity_hint", "")
        if sev in ["good", "moderate", "poor", "not_visible"]:
            img.severity_hint = sev
        else:
            img.severity_hint = ""
            
    except Exception as e:
        logger.warning(f"Failed to analyze image on page {img.page_num}: {e}")
        img.description = ""
        img.area_tag = ""
        img.observation_tag = ""
        img.severity_hint = ""

async def analyze_images(doc: ExtractedDocument, provider: AbstractLLMProvider) -> ExtractedDocument:
    system_prompt = """You are a structural inspection assistant. Analyse this image from a 
building inspection report. Return ONLY valid JSON with these exact keys:
description (string, 1-2 sentences describing what you see),
area_tag (string, snake_case location e.g. hall_ceiling, master_bedroom_bathroom),
observation_tag (string, snake_case issue e.g. dampness, tile_gap, crack, efflorescence),
severity_hint (string, exactly one of: good, moderate, poor, not_visible),
is_thermal (boolean, true if this is a thermal/infrared image),
temperature_range (string, e.g. '22.3-28.8°C' if thermal, else null)"""

    tasks = []
    for page in doc.pages:
        for img in page.images:
            tasks.append(_analyze_single_image(img, doc.doc_type, system_prompt, provider))
            
    if tasks:
        await asyncio.gather(*tasks)

    return doc
