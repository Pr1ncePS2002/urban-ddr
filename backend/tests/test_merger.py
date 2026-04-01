from app.pipeline.merger import merge_documents
from app.models.schemas import ExtractedDocument, ExtractedPage, ExtractedImage

def test_merge_documents_creates_areas():
    insp_doc = ExtractedDocument(
        doc_type="inspection",
        pages=[
            ExtractedPage(
                page_num=1,
                text_blocks=["Some text here"],
                tables=[],
                images=[
                    ExtractedImage(
                        page_num=1, image_index=0, image_bytes=b"123", mime_type="image/jpeg",
                        bbox=(0,0,0,0), description="desc", area_tag="master_bedroom",
                        observation_tag="dampness", severity_hint="moderate"
                    )
                ]
            )
        ]
    )
    
    thermal_doc = ExtractedDocument(
        doc_type="thermal",
        pages=[
            ExtractedPage(
                page_num=1, text_blocks=[], tables=[],
                images=[
                    ExtractedImage(
                        page_num=1, image_index=0, image_bytes=b"456", mime_type="image/png",
                        bbox=(0,0,0,0), description="coldspot detected", area_tag="master_bedroom",
                        observation_tag="", severity_hint=""
                    )
                ]
            )
        ]
    )
    
    merged = merge_documents(insp_doc, thermal_doc)
    
    assert len(merged.areas) == 1
    area = merged.areas[0]
    # Check normalization
    assert area.area == "Master Bedroom"
    assert "Dampness" in area.negative_observations
    assert any("coldspot" in t["description"] for t in area.thermal_readings)
    assert len(area.images) == 2
