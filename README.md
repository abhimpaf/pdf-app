# pdf-app

A command-line tool to shrink PDF file size and convert PDFs to DOCX, JPEG, or PPTX.

## Stack

- **Python 3.9+** — fast to iterate, first-class PDF libraries, single-command packaging.
- **[Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)** — CLI framework with auto-generated `--help`, typed arguments, and readable progress/output.
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — compression (stream cleanup, image downsampling/re-encoding) and PDF page rendering, without needing external binaries like Ghostscript.
- **[pdf2docx](https://github.com/dothinking/pdf2docx)** — layout-aware PDF → DOCX conversion (preserves text, tables, images).
- **[python-pptx](https://python-pptx.readthedocs.io/)** — assembles PPTX slides from rendered page images.
- **[Pillow](https://python-pillow.org/)** — image encoding for the JPEG export path.

This stack was chosen to avoid any external system dependencies (no Ghostscript/LibreOffice install required) while still giving good compression ratios and accurate conversions, all installable via `pip`.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -e .
```

## Usage

```bash
# Shrink a PDF (levels: low, medium, high)
pdf-app compress input.pdf -o output.pdf --level medium

# Convert to Word
pdf-app to-doc input.pdf -o output.docx

# Convert to JPEG (one image per page)
pdf-app to-jpeg input.pdf -o ./output_images --dpi 150

# Convert to PowerPoint (one slide per page)
pdf-app to-ppt input.pdf -o output.pptx
```

Run `pdf-app --help` or `pdf-app <command> --help` for full options.
