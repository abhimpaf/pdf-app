# pdf-app

A command-line tool to shrink PDF file size and convert PDFs to DOCX, JPEG, or PPTX.

## Stack

- **Python 3.9+** — fast to iterate, first-class PDF libraries, single-command packaging.
- **[Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich)** — CLI framework with auto-generated `--help`, typed arguments, and readable progress/output.
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — compression (stream cleanup, image downsampling/re-encoding) and PDF page rendering, without needing external binaries like Ghostscript.
- **[pdf2docx](https://github.com/dothinking/pdf2docx)** — layout-aware PDF → DOCX conversion (preserves text, tables, images).
- **[python-pptx](https://python-pptx.readthedocs.io/)** — assembles PPTX slides from rendered page images.
- **[Pillow](https://python-pillow.org/)** — image encoding for the JPEG export path.

This stack was chosen to avoid any external system dependencies (no Ghostscript/LibreOffice install required) while still giving good compression ratios and accurate conversions, all installable via `pip`. It's pure Python, so the same install works unchanged on Windows, macOS, and Linux.

The interactive menu deliberately uses plain numbered `input()` prompts rather than an arrow-key/raw-terminal picker (e.g. questionary/prompt_toolkit) — those crash on terminals that don't expose a real console buffer, notably Git Bash's mintty on Windows. Numbered prompts work identically in any terminal on any OS.

## Install

### Option A: pipx (needs Python, no repo clone required)

```bash
pipx install "git+https://github.com/abhimpaf/pdf-app.git"
```

This puts a `pdf-app` command on your PATH, runnable from any directory, in an isolated environment that won't conflict with other Python projects.

### Option B: standalone executable (no Python required at all)

Grab the binary for your OS from the project's [GitHub Releases](https://github.com/abhimpaf/pdf-app/releases) page, put it somewhere on your PATH (or just run it from wherever you downloaded it), and run it directly (`./pdf-app` or `pdf-app.exe`). PyInstaller can't cross-compile, so each release only has binaries for the OS(es) they were built on — see `build_scripts/build.sh` to build one yourself for macOS/Linux.

### Local/dev install (from a clone of this repo)

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e .
```

## Usage

Run `pdf-app` with no arguments from any directory to launch the interactive menu:

```
$ pdf-app

What would you like to do?
  1. Compress PDF (reduce file size)
  2. Convert PDF to DOCX (Word)
  3. Convert PDF to JPEG (one image per page)
  4. Convert PDF to PPTX (PowerPoint)
  0. Exit
Enter choice:
```

Pick a tool, then pick a file from a paginated list (5 at a time, with `n`/`p` to page forward/back) of every file in the current directory. Selecting a non-PDF file shows an error and lets you pick again. Output is written next to the input as `<name>-<tool>.<ext>` (e.g. `report-compress.pdf`, `report-to-doc.docx`). After each run you're asked whether to continue or exit.

For scripting, the same actions are also available as direct subcommands:

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

Run `pdf-app <command> --help` for full options on any subcommand.
