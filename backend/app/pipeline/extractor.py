import fitz  # PyMuPDF
import pdfplumber
import io
from ..models.schemas import ExtractedDocument, ExtractedPage, ExtractedImage

def extract_pdf(pdf_path: str, doc_type: str) -> ExtractedDocument:
    """Extracts text, images, and tables from a PDF using PyMuPDF and pdfplumber."""
    doc = fitz.open(pdf_path)
    extracted_pages = []

    with pdfplumber.open(pdf_path) as plumber_pdf:
        for page_num in range(len(doc)):
            page = doc[page_num]
            plumber_page = plumber_pdf.pages[page_num]

            # 1. Text blocks
            text_blocks = []
            dict_data = page.get_text("dict")
            for block in dict_data.get("blocks", []):
                if block.get("type") == 0:  # text block
                    text = " ".join([span["text"] for line in block.get("lines", []) for span in line.get("spans", [])])
                    if text.strip():
                        text_blocks.append(text.strip())

            # 2. Tables
            raw_tables = plumber_page.extract_tables()
            tables = []
            if raw_tables:
                for table in raw_tables:
                    clean_table = []
                    for row in table:
                        clean_row = [cell if cell is not None else "" for cell in row]
                        clean_table.append(clean_row)
                    tables.append(clean_table)

            # 3. Images
            extracted_images = []
            image_list = page.get_images(full=True)[:2] # Cap at 2 per page to protect free-tier API quotas
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                
                rects = page.get_image_rects(xref)
                bbox = (0.0, 0.0, 0.0, 0.0)
                if rects:
                    bbox = (rects[0].x0, rects[0].y0, rects[0].x1, rects[0].y1)

                mime_type = f"image/{ext}" if ext in ["png", "jpeg", "jpg"] else "image/jpeg"

                extracted_images.append(
                    ExtractedImage(
                        page_num=page_num + 1,
                        image_index=img_index,
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                        bbox=bbox
                    )
                )

            extracted_pages.append(
                ExtractedPage(
                    page_num=page_num + 1,
                    text_blocks=text_blocks,
                    tables=tables,
                    images=extracted_images
                )
            )

    doc.close()
    return ExtractedDocument(doc_type=doc_type, pages=extracted_pages)
