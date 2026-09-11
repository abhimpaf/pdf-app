from pathlib import Path
from typing import List

import pymupdf


def pdf_to_jpeg(input_path: Path, output_dir: Path, dpi: int = 150, quality: int = 85) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    zoom = dpi / 72  # PDF base unit is 72 DPI
    matrix = pymupdf.Matrix(zoom, zoom)

    output_paths = []
    doc = pymupdf.open(input_path)
    try:
        width = len(str(doc.page_count))
        for index, page in enumerate(doc, start=1):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            page_path = output_dir / f"{input_path.stem}_page{index:0{width}}.jpg"
            pixmap.save(page_path, jpg_quality=quality)
            output_paths.append(page_path)
    finally:
        doc.close()

    return output_paths
