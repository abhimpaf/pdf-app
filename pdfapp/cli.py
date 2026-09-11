from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from pdfapp.utils import default_output_path, human_size, require_pdf

app = typer.Typer(
    name="pdf-app",
    help="Reduce PDF file size and convert PDFs to DOCX, JPEG, or PPTX.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def compress(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="PDF file to compress."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output PDF path."),
    level: str = typer.Option("medium", "--level", "-l", help="Compression level: low, medium, high."),
):
    """Shrink a PDF's file size by downsampling images and cleaning up structure."""
    from pdfapp.compress import compress_pdf

    require_pdf(input_path)
    output_path = output or default_output_path(input_path, "_compressed", ".pdf")

    with console.status(f"Compressing at '{level}' level..."):
        result = compress_pdf(input_path, output_path, level=level)

    console.print(f"[green]Saved:[/green] {output_path}")
    console.print(
        f"{human_size(result.input_size)} -> {human_size(result.output_size)} "
        f"([bold]{result.ratio:.0%} smaller[/bold])"
    )


@app.command(name="to-doc")
def to_doc(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="PDF file to convert."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output .docx path."),
):
    """Convert a PDF to an editable Word (.docx) document."""
    from pdfapp.convert_doc import pdf_to_docx

    require_pdf(input_path)
    output_path = output or default_output_path(input_path, "", ".docx")

    with console.status("Converting to DOCX..."):
        pdf_to_docx(input_path, output_path)

    console.print(f"[green]Saved:[/green] {output_path}")


@app.command(name="to-jpeg")
def to_jpeg(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="PDF file to convert."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Directory for output JPEGs."),
    dpi: int = typer.Option(150, "--dpi", help="Rendering resolution."),
    quality: int = typer.Option(85, "--quality", "-q", help="JPEG quality (1-100)."),
):
    """Convert each PDF page to a JPEG image."""
    from pdfapp.convert_image import pdf_to_jpeg

    require_pdf(input_path)
    out_dir = output_dir or input_path.with_name(f"{input_path.stem}_jpeg")

    with console.status("Converting to JPEG..."):
        paths = pdf_to_jpeg(input_path, out_dir, dpi=dpi, quality=quality)

    console.print(f"[green]Saved {len(paths)} page(s) to:[/green] {out_dir}")


@app.command(name="to-ppt")
def to_ppt(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="PDF file to convert."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output .pptx path."),
    dpi: int = typer.Option(150, "--dpi", help="Rendering resolution for slide images."),
):
    """Convert a PDF into a PowerPoint (.pptx), one slide per page."""
    from pdfapp.convert_ppt import pdf_to_pptx

    require_pdf(input_path)
    output_path = output or default_output_path(input_path, "", ".pptx")

    with console.status("Converting to PPTX..."):
        pdf_to_pptx(input_path, output_path, dpi=dpi)

    console.print(f"[green]Saved:[/green] {output_path}")


if __name__ == "__main__":
    app()
