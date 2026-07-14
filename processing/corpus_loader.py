"""D-009 grön tooling: PDF-extraktion + sliding-window-chunkning.

_extract_text() och _chunk() är fristående funktioner (D-009), återanvändbara
oavsett korpus. chunk_size/overlap/min_chars är ändringsbara defaults (config.py),
inte låsta värden.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import config


def _extract_text(pdf_path: str | Path) -> str:
    """Extraherar all text ur en PDF, sida för sida, via pdfplumber."""
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)


def _chunk(
    text: str,
    chunk_size: int = config.CHUNK_SIZE_DEFAULT,
    overlap: int = config.CHUNK_OVERLAP_DEFAULT,
    min_chars: int = config.MIN_CHARS_DEFAULT,
) -> list[str]:
    """Sliding-window-chunkning på tecken. Kastar chunkar kortare än min_chars
    (typiskt svansen av ett dokument)."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    step = chunk_size - overlap
    if step <= 0:
        raise ValueError("overlap måste vara mindre än chunk_size")

    chunks: list[str] = []
    start = 0
    while start < len(text):
        piece = text[start : start + chunk_size]
        if len(piece) >= min_chars:
            chunks.append(piece)
        start += step
    return chunks


@dataclass
class ChunkRecord:
    text: str
    source_file: str
    chunk_index: int


def load_corpus(source_dir: str | Path) -> list[ChunkRecord]:
    """Extraherar + chunkar källfilerna i source_dir. Om PDF:er finns används
    de som kanonisk källa (via _extract_text(), pdfplumber, D-009) — eventuella
    .txt-filer i samma mapp (t.ex. Korpus 1/3:s pdftotext-biprodukter i
    manifesten) ignoreras då, för att inte dubbelräkna samma innehåll. Om INGA
    PDF:er finns läses .txt-filer direkt (redan plaintext, ingen extraktion att
    göra — Korpus 2:s RFC-filer). Båda vägarna chunkas med samma _chunk().
    Ordning = filnamnssortering, för reproducerbarhet."""
    source_dir = Path(source_dir)
    records: list[ChunkRecord] = []

    pdf_paths = sorted(source_dir.glob("*.pdf"))

    if pdf_paths:
        for pdf_path in pdf_paths:
            text = _extract_text(pdf_path)
            for i, chunk_text in enumerate(_chunk(text)):
                records.append(
                    ChunkRecord(text=chunk_text, source_file=pdf_path.name, chunk_index=i)
                )
    else:
        for txt_path in sorted(source_dir.glob("*.txt")):
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
            for i, chunk_text in enumerate(_chunk(text)):
                records.append(
                    ChunkRecord(text=chunk_text, source_file=txt_path.name, chunk_index=i)
                )

    return records
