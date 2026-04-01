import base64
import logging
from ..models.schemas import GeneratedDDR, ExtractedImage

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"WeasyPrint not available: {e}")
    WEASYPRINT_AVAILABLE = False

def _image_to_base64(img: ExtractedImage) -> str:
    encoded = base64.b64encode(img.image_bytes).decode('utf-8')
    return f"data:{img.mime_type};base64,{encoded}"

def _build_html(ddr: GeneratedDDR) -> str:
    # Build HTML string matching UrbanRoof branding (#F5A623 amber, #1A1A2E dark)
    
    def safe_text(t: str) -> str:
        if not t: return ""
        return t.replace('\n', '<br>')
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-right {{
                    content: counter(page);
                }}
            }}
            body {{
                font-family: system-ui, -apple-system, sans-serif;
                color: #333;
                line-height: 1.6;
            }}
            .header {{
                background-color: #1A1A2E;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #F5A623;
                margin: 0;
            }}
            h2 {{
                color: #1A1A2E;
                border-bottom: 3px solid #F5A623;
                padding-bottom: 5px;
                margin-top: 40px;
                page-break-after: avoid;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f8f9fa;
            }}
            .image-section {{
               page-break-inside: avoid;
            }}
            .image-grid {{
                display: flex;
                flex-wrap: wrap;
            }}
            .image-card {{
                display: inline-block;
                width: 48%;
                margin: 1%;
                vertical-align: top;
            }}
            .image-card img {{
                max-width: 100%;
                border: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>UrbanRoof Private Limited</h1>
            <h2>Detailed Diagnosis Report (DDR)</h2>
            <p>Generated: {ddr.generated_at.strftime("%Y-%m-%d %H:%M")}</p>
        </div>
        
        <h2>1. Property Issue Summary</h2>
        <div>{safe_text(ddr.property_issue_summary)}</div>
        
        <h2>2. Area-wise Observations</h2>
        <div>{safe_text(ddr.area_wise_observations)}</div>
        
        <h2>3. Probable Root Cause</h2>
        <div>{safe_text(ddr.probable_root_cause)}</div>
        
        <h2>Images by Area</h2>
    """
    
    for area, images in ddr.images_by_area.items():
        if not images:
            continue
        html += f"<div class='image-section'><h3>{area}</h3><div class='image-grid'>"
        for img in images:
            html += f"""
            <div class='image-card'>
                <img src="{_image_to_base64(img)}" />
            </div>
            """
        html += "</div></div>"

    html += f"""
        <h2>4. Severity Assessment</h2>
        <div>{safe_text(ddr.severity_assessment)}</div>
        
        <h2>5. Recommended Actions</h2>
        <div>{safe_text(ddr.recommended_actions)}</div>
        
        <h2>6. Additional Notes</h2>
        <div>{safe_text(ddr.additional_notes)}</div>
        
        <h2>7. Missing or Unclear Information</h2>
        <div>{safe_text(ddr.missing_information)}</div>
    </body>
    </html>
    """
    return html

async def render_to_pdf(ddr: GeneratedDDR) -> bytes:
    """Returns PDF bytes. Never writes to disk except /tmp."""
    html_content = _build_html(ddr)
    if WEASYPRINT_AVAILABLE:
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    else:
        logger.warning("WeasyPrint not found. Returning raw HTML as bytes instead of PDF for local test fallback.")
        return html_content.encode('utf-8')
