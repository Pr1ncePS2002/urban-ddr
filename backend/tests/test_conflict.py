from app.pipeline.conflict import detect_conflicts
from app.models.schemas import MergedData, AreaObservation, ExtractedImage

def test_conflict_detection_rules():
    area1 = AreaObservation(
        area="Hall",
        negative_observations=["no leakage observed"],
        positive_observations=[],
        thermal_readings=[{"raw_observation": "", "description": "severe coldspot"}],
        images=[],
        severity="good",
        source_docs=[]
    )
    
    area2 = AreaObservation(
        area="Kitchen",
        negative_observations=["dampness on wall"],
        positive_observations=[],
        thermal_readings=[], # no thermal images
        images=[],
        severity="good",
        source_docs=[]
    )
    
    merged = MergedData(
        property_summary="Not Available",
        areas=[area1, area2],
        inspection_date="Not Available",
        inspector_name="Not Available",
        property_address="Not Available",
        conflicts=[],
        missing_fields=[]
    )
    
    result = detect_conflicts(merged)
    
    # Rule 1
    assert any("coldspot" in c.lower() for c in result.conflicts)
    
    # Rule 2 (Dampness but no thermal images added to missing fields)
    assert any("Thermal image" in str(m) for m in result.missing_fields)
    
    # Rule 4 (Missing fields from the root doc variables)
    assert "property_address" in result.missing_fields
