"""Convert a .docx manuscript to a text-faithful PDF for APIs that require PDF input.

We render from the SAME text extraction (docx_extract.extract_text) that the LLM
providers receive, so every system under benchmark sees identical manuscript
content. This sacrifices original page layout (no Word/LibreOffice available) in
favor of content-equality and is a deliberate methodological choice — the inserted
errors are textual/numeric (including table cells), all of which survive extraction.
"""

from pathlib import Path

from fpdf import FPDF

from docx_extract import extract_text

# Unicode TTF so statistical symbols (χ², β, ±, Greek, etc.) survive.
_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def text_to_pdf(text: str, out_path: Path) -> Path:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("ArialUni", "", _FONT_PATH)
    pdf.set_font("ArialUni", size=10)

    epw = pdf.w - 2 * pdf.l_margin
    text = text.replace("\t", " ")
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        # multi_cell wraps long paragraphs; markers like [TABLE] pass through as text.
        pdf.multi_cell(epw, 5, block)
        pdf.ln(2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path


def docx_to_pdf(docx_path: Path, out_path: Path) -> Path:
    return text_to_pdf(extract_text(docx_path), out_path)


if __name__ == "__main__":
    import sys
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    docx_to_pdf(src, dst)
    print(f"Wrote {dst} ({dst.stat().st_size} bytes)")
