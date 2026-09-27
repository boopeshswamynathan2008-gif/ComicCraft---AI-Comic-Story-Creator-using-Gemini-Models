from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fpdf import FPDF


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def export_comic_pdf(panels: List[Dict[str, object]], output_dir: str = "static/exports") -> str:
    output_path = PROJECT_ROOT / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    filename = f"comic_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_file = output_path / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "ComicCraft Story", ln=True)

    for panel in panels:
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 14)
        title = str(panel.get("title") or "Panel")
        pdf.cell(0, 10, title, ln=True)

        image_path = str(panel.get("image") or "")
        if image_path:
            image_file = image_path.lstrip("/")
            absolute = (PROJECT_ROOT / image_file).resolve()
            if absolute.exists():
                pdf.image(str(absolute), x=10, y=pdf.get_y(), w=190)
                pdf.ln(80)

        pdf.set_font("Helvetica", "", 11)
        narration = str(panel.get("narration") or "")
        dialogue = str(panel.get("dialogue") or "")
        if narration:
            pdf.multi_cell(0, 8, f"Narration: {narration}")
        if dialogue:
            pdf.multi_cell(0, 8, f"Dialogue: {dialogue}")

    pdf.output(str(output_file))
    return "/" + str(output_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
