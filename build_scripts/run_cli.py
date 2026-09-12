"""PyInstaller entry point -- kept outside the `pdfapp` package so the
frozen build has one unambiguous script to target."""

from pdfapp.cli import app

if __name__ == "__main__":
    app()
