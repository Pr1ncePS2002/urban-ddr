from difflib import SequenceMatcher
from ..models.schemas import ExtractedDocument, MergedData, AreaObservation

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def _find_or_create_area(areas: dict[str, AreaObservation], area_name: str) -> AreaObservation:
    for existing_name, area in areas.items():
        if _similarity(existing_name, area_name) > 0.8:
            return area
            
    # Normalize to create a readable name
    display_name = area_name.replace("_", " ").title() if "_" in area_name else area_name
    if not display_name:
        display_name = "Unknown Area"
        
    new_area = AreaObservation(
        area=display_name,
        negative_observations=[],
        positive_observations=[],
        thermal_readings=[],
        images=[],
        severity="good",
        source_docs=[]
    )
    areas[display_name] = new_area
    return new_area

def merge_documents(inspection: ExtractedDocument, thermal: ExtractedDocument) -> MergedData:
    areas_dict: dict[str, AreaObservation] = {}
    
    merged = MergedData(
        property_summary="Not Available",
        areas=[],
        inspection_date="Not Available",
        inspector_name="Not Available",
        property_address="Not Available",
        conflicts=[],
        missing_fields=[]
    )
    
    # Process inspection doc
    for page in inspection.pages:
        for img in page.images:
            if img.area_tag:
                area = _find_or_create_area(areas_dict, img.area_tag)
                if img not in area.images:
                    area.images.append(img)
                if "inspection" not in area.source_docs:
                    area.source_docs.append("inspection")
                
                # Use image severity as a baseline
                if img.severity_hint == "poor" or (img.severity_hint == "moderate" and area.severity == "good"):
                    area.severity = img.severity_hint
                    
                if img.observation_tag:
                    obs = img.observation_tag.replace("_", " ").title()
                    if "crack" in img.observation_tag or "gap" in img.observation_tag:
                        if obs not in area.positive_observations:
                            area.positive_observations.append(obs)
                    else:
                        if obs not in area.negative_observations:
                            area.negative_observations.append(obs)

    # Process thermal doc
    for page in thermal.pages:
        for img in page.images:
            if img.area_tag:
                area = _find_or_create_area(areas_dict, img.area_tag)
                if img not in area.images:
                    area.images.append(img)
                if "thermal" not in area.source_docs:
                    area.source_docs.append("thermal")
                
                area.thermal_readings.append({
                    "raw_observation": img.observation_tag,
                    "description": img.description
                })

    merged.areas = list(areas_dict.values())
    return merged
