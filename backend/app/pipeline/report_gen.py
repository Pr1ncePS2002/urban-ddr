from datetime import datetime
import json
import logging
from ..models.schemas import MergedData, GeneratedDDR
from ..providers.base import AbstractLLMProvider

logger = logging.getLogger(__name__)

async def generate_ddr(merged: MergedData, llm: AbstractLLMProvider, job_id: str) -> GeneratedDDR:
    system_prompt = """You are a professional building inspection report writer for UrbanRoof Private Limited. 
Write in clear, client-friendly language. Avoid excessive technical jargon. Be factual — only report what is present in the provided data. If data is missing, write 'Not Available'. Never invent facts. Use simple paragraphs, not bullet points unless listing items explicitly.

You must return ONLY a valid JSON object matching the following structure:
{
    "property_issue_summary": "2-3 paragraph executive summary of the property's health condition (include property details, overall condition assessment, number of areas inspected, critical issues).",
    "area_wise_observations": "For each area, a structured paragraph describing negative side (symptoms) and positive side (source). Include thermal readings.",
    "probable_root_cause": "For each affected area, explain probable root cause connecting source to impact. Reference thermal data.",
    "severity_assessment": "A severity assessment table for each area. Use levels: Good, Moderate, Poor. Include 1-sentence justification.",
    "recommended_actions": "Practical repair treatments for areas requiring action (Poor/Moderate). What to do, materials, urgency.",
    "additional_notes": "Additional observations, warnings, or notes. State conflicts if they exist.",
    "missing_information": "List unavailable information or unresolved data conflicts."
}"""

    # Serialize all merged data for the prompt
    payload_data = {
        "property_address": merged.property_address,
        "inspection_date": merged.inspection_date,
        "inspector_name": merged.inspector_name,
        "areas": [
            {
                "area": a.area, 
                "severity": a.severity,
                "negative_observations": a.negative_observations,
                "positive_observations": a.positive_observations,
                "thermal_readings": a.thermal_readings
            } for a in merged.areas
        ],
        "conflicts": merged.conflicts,
        "missing_fields": list(merged.missing_fields)
    }

    prompt = f"Generate the report sections based on this data:\n{json.dumps(payload_data)}"
    
    try:
        response_text = await llm.complete(prompt=prompt, system=system_prompt)
        
        # Clean markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        data = json.loads(response_text.strip())
        
    except Exception as e:
        logger.error(f"Failed to generate DDR sections or parse JSON. Error: {e}")
        # Fallback to an error state DDR
        data = {
            "property_issue_summary": "Report generation failed due to an API error.",
            "area_wise_observations": "Not Available.",
            "probable_root_cause": "Not Available.",
            "severity_assessment": "Not Available.",
            "recommended_actions": "Not Available.",
            "additional_notes": "Not Available.",
            "missing_information": "Not Available."
        }

    images_by_area = {a.area: a.images for a in merged.areas}

    return GeneratedDDR(
        property_issue_summary=data.get("property_issue_summary", "Not Available."),
        area_wise_observations=data.get("area_wise_observations", "Not Available."),
        probable_root_cause=data.get("probable_root_cause", "Not Available."),
        severity_assessment=data.get("severity_assessment", "Not Available."),
        recommended_actions=data.get("recommended_actions", "Not Available."),
        additional_notes=data.get("additional_notes", "Not Available."),
        missing_information=data.get("missing_information", "Not Available."),
        images_by_area=images_by_area,
        generated_at=datetime.utcnow(),
        job_id=job_id
    )
