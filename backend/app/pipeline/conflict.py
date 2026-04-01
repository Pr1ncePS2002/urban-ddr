from ..models.schemas import MergedData

def detect_conflicts(merged: MergedData) -> MergedData:
    conflicts = []
    missing_fields = []
    
    # RULE 4: Missing required fields for DDR
    if merged.property_address == "Not Available":
        missing_fields.append("property_address")
    if merged.inspection_date == "Not Available":
        missing_fields.append("inspection_date")
    if merged.inspector_name == "Not Available":
        missing_fields.append("inspector_name")
    # For year_of_construction and previous_repairs, we assume they are "Not Available" by default unless extracted
    missing_fields.extend(["year_of_construction", "previous_repairs"])

    for area in merged.areas:
        obs_text = " ".join(area.negative_observations + area.positive_observations).lower()
        
        # Helper: check if we have any thermal image here
        has_thermal_images = any("thermal" in img.mime_type or len(area.thermal_readings) > 0 for img in area.images)
        thermal_descriptions = " ".join(t.get("description", "").lower() for t in area.thermal_readings)
        
        # RULE 1: Thermal-visual mismatch
        if "coldspot" in thermal_descriptions and "no leakage" in obs_text:
            conflicts.append(f"Area {area.area}: Inspection reports 'no leakage' but thermal image shows coldspot.")
            
        # RULE 2: Missing thermal data
        if ("damp" in obs_text or "seepage" in obs_text) and not has_thermal_images:
            missing_fields.append(f"Thermal image for {area.area} (dampness reported)")
            
        # RULE 3: Severity inconsistency
        # If visual image says "poor" but we have no negative obs 
        # (effectively "good" in a checklist)
        has_poor_image = any(img.severity_hint == "poor" for img in area.images)
        if has_poor_image and not area.negative_observations:
             conflicts.append(f"Area {area.area}: Image severity is 'poor' but no negative issues reported in text.")

    merged.conflicts.extend(conflicts)
    merged.missing_fields.extend(set(missing_fields)) # unique items
    
    return merged
