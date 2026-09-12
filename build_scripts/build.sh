#!/usr/bin/env bash
# Builds a single-file standalone executable (no Python required to run it).
# Run this on each OS you want a binary for -- PyInstaller cannot cross-compile,
# so a build done on Windows only produces a Windows .exe, macOS only a macOS
# binary, Linux only a Linux binary.
set -euo pipefail
cd "$(dirname "$0")/.."

python -m pip install --quiet -e ".[dev]" pyinstaller

python -m PyInstaller \
  --onefile --name pdf-app --console \
  --paths . \
  --collect-all pptx \
  --collect-all pymupdf \
  --collect-all fitz \
  --collect-all pdf2docx \
  --distpath build_scripts/dist \
  --workpath build_scripts/work \
  --specpath build_scripts \
  build_scripts/run_cli.py

echo "Built: build_scripts/dist/pdf-app(.exe)"
