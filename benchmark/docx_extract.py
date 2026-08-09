"""Extract text from .docx files, interleaving paragraphs and tables."""

import docx
from pathlib import Path
from docx.oxml.ns import qn


def extract_text(docx_path: Path) -> str:
    doc = docx.Document(str(docx_path))
    parts: list[str] = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag
        if tag == "p":
            text = element.text or ""
            # Collect text from all runs
            for run in element.iter(qn("w:t")):
                pass  # element.text already handled by python-docx
            # Use python-docx paragraph object for cleaner extraction
            for para in doc.paragraphs:
                if para._element is element:
                    text = para.text
                    break
            if text.strip():
                # The published modified papers carry a do-not-cite watermark that
                # must not reach the reviewer under test.
                if text.lstrip().startswith("BENCHMARK ARTIFACT"):
                    continue
                parts.append(text.strip())
        elif tag == "tbl":
            for table in doc.tables:
                if table._element is element:
                    parts.append(_format_table(table))
                    break

    return "\n\n".join(parts)


def _format_table(table) -> str:
    rows = []
    for row in table.rows:
        cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
        rows.append(" | ".join(cells))
    if not rows:
        return ""
    return "[TABLE]\n" + "\n".join(rows) + "\n[/TABLE]"
