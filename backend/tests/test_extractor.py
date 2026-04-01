import os
import fitz
from app.pipeline.extractor import extract_pdf

def test_extract_pdf(tmp_path):
    # Create a minimal valid PDF using PyMuPDF to test extraction
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Test Inspection Text")
    
    pdf_path = str(tmp_path / "test.pdf")
    doc.save(pdf_path)
    doc.close()
    
    result = extract_pdf(pdf_path, "inspection")
    
    assert result.doc_type == "inspection"
    assert len(result.pages) == 1
    assert "Test Inspection Text" in " ".join(result.pages[0].text_blocks)
