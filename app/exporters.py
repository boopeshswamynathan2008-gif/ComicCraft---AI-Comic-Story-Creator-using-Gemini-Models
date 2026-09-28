from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fpdf import FPDF
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def clean_text(value) -> str:
    """
    Convert text into characters that the default FPDF Helvetica font
    can safely handle.
    """
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def find_image_file(image_path: str):
    """
    Convert the browser/static image URL into an actual
    file path on the computer.
    """

    if not image_path:
        return None

    image_path = str(image_path).strip()

    # Example:
    # /static/panels/panel_1_xxxxx.png
    image_path = image_path.lstrip("/")

    absolute_path = (PROJECT_ROOT / image_path).resolve()

    # Security check: make sure the image remains inside the project
    try:
        absolute_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return None

    if absolute_path.exists() and absolute_path.is_file():
        return absolute_path

    return None


def export_comic_pdf(
    panels: List[Dict[str, object]],
    output_dir: str = "static/exports",
) -> str:

    # Create export folder
    output_path = PROJECT_ROOT / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Unique filename
    filename = (
        f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    )

    output_file = output_path / filename

    # Create PDF
    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # -----------------------------
    # TITLE PAGE
    # -----------------------------

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        20
    )

    pdf.cell(
        0,
        12,
        "ComicCraft Story",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(5)

    # -----------------------------
    # PANELS
    # -----------------------------

    for index, panel in enumerate(panels, start=1):

        # Start a new page for every panel.
        # This makes the PDF cleaner.
        pdf.add_page()

        # Panel title
        title = clean_text(
            panel.get("title") or f"Panel {index}"
        )

        pdf.set_font(
            "Helvetica",
            "B",
            16
        )

        pdf.cell(
            0,
            10,
            title,
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.ln(3)

        # -----------------------------
        # IMAGE
        # -----------------------------

        image_path = str(
            panel.get("image") or ""
        )

        image_file = find_image_file(image_path)

        if image_file:

            try:
                # Check/convert image using Pillow.
                # This prevents many FPDF image errors.
                with Image.open(image_file) as img:

                    # Convert images with transparency/RGBA
                    # into RGB.
                    if img.mode not in ("RGB", "L"):
                        converted_image = (
                            image_file.parent
                            / f"_pdf_{image_file.stem}.jpg"
                        )

                        rgb_image = img.convert("RGB")

                        rgb_image.save(
                            converted_image,
                            "JPEG",
                            quality=95
                        )

                        pdf_image = converted_image

                    else:
                        pdf_image = image_file

                # Add image
                pdf.image(
                    str(pdf_image),
                    x=15,
                    w=180,
                )

                pdf.ln(8)

            except Exception as image_error:

                print(
                    f"PDF image error for panel {index}: "
                    f"{image_error}"
                )

                pdf.set_font(
                    "Helvetica",
                    "",
                    10
                )

                pdf.multi_cell(
                    0,
                    7,
                    "Image could not be added to this panel."
                )

        else:

            print(
                f"PDF image not found for panel {index}: "
                f"{image_path}"
            )

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            pdf.multi_cell(
                0,
                7,
                "Image not available."
            )

        # -----------------------------
        # NARRATION
        # -----------------------------

        narration = clean_text(
            panel.get("narration") or ""
        )

        if narration:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.cell(
                0,
                8,
                "Narration:",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            pdf.multi_cell(
                0,
                7,
                narration
            )

            pdf.ln(2)

        # -----------------------------
        # DIALOGUE
        # -----------------------------

        dialogue = clean_text(
            panel.get("dialogue") or ""
        )

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.cell(
                0,
                8,
                "Dialogue:",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            pdf.multi_cell(
                0,
                7,
                dialogue
            )

    # -----------------------------
    # SAVE PDF
    # -----------------------------

    pdf.output(str(output_file))

    print(
        f"PDF successfully created: {output_file}"
    )

    # Return browser URL
    return "/" + str(
        output_file.relative_to(PROJECT_ROOT)
    ).replace("\\", "/")

