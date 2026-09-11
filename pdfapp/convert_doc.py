from pathlib import Path

from pdf2docx import Converter


def pdf_to_docx(input_path: Path, output_path: Path) -> Path:
    converter = Converter(str(input_path))
    try:
        converter.convert(str(output_path))
    finally:
        converter.close()
    return output_path
