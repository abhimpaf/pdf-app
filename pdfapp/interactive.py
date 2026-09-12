from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from rich.console import Console

console = Console()

PAGE_SIZE = 5


@dataclass
class Tool:
    key: str  # also used as the output-filename suffix, e.g. "-compress"
    label: str
    run: Callable[[Path], Path]


def _tool_registry() -> List[Tool]:
    # Imports are local so `pdf-app --help` stays fast and doesn't pull in
    # every conversion library just to print the menu.
    from pdfapp.compress import compress_pdf
    from pdfapp.convert_doc import pdf_to_docx
    from pdfapp.convert_image import pdf_to_jpeg
    from pdfapp.convert_ppt import pdf_to_pptx
    from pdfapp.utils import default_output_path

    def run_compress(path: Path) -> Path:
        output = default_output_path(path, "-compress", ".pdf")
        compress_pdf(path, output, level="medium")
        return output

    def run_to_doc(path: Path) -> Path:
        output = default_output_path(path, "-to-doc", ".docx")
        pdf_to_docx(path, output)
        return output

    def run_to_jpeg(path: Path) -> Path:
        output_dir = path.with_name(f"{path.stem}-to-jpeg")
        pdf_to_jpeg(path, output_dir, dpi=150, quality=85)
        return output_dir

    def run_to_ppt(path: Path) -> Path:
        output = default_output_path(path, "-to-ppt", ".pptx")
        pdf_to_pptx(path, output, dpi=150)
        return output

    return [
        Tool("compress", "Compress PDF (reduce file size)", run_compress),
        Tool("to-doc", "Convert PDF to DOCX (Word)", run_to_doc),
        Tool("to-jpeg", "Convert PDF to JPEG (one image per page)", run_to_jpeg),
        Tool("to-ppt", "Convert PDF to PPTX (PowerPoint)", run_to_ppt),
    ]


def list_directory_files(directory: Path) -> List[Path]:
    return sorted((p for p in directory.iterdir() if p.is_file()), key=lambda p: p.name.lower())


def paginate(files: List[Path], page: int, page_size: int = PAGE_SIZE):
    """Pure pagination helper, kept separate from I/O so it's testable.

    Returns (chunk, total_pages, has_prev, has_next).
    """
    total_pages = max((len(files) - 1) // page_size + 1, 1)
    start = page * page_size
    chunk = files[start : start + page_size]
    return chunk, total_pages, page > 0, start + page_size < len(files)


def _prompt(text: str) -> str:
    return input(text).strip()


def _confirm(text: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = _prompt(f"{text} {suffix} ").lower()
    if answer == "":
        return default
    return answer in ("y", "yes")


def _select_tool(tools: List[Tool]) -> Optional[Tool]:
    """Numbered menu: plain input(), not an arrow-key picker.

    A raw-mode picker (e.g. questionary/prompt_toolkit) throws on terminals
    that don't expose a real console buffer -- notably Git Bash's mintty on
    Windows -- so this deliberately sticks to input()+numbers, which works
    identically on every OS and terminal.
    """
    while True:
        console.print("\n[bold]What would you like to do?[/bold]")
        for i, tool in enumerate(tools, start=1):
            console.print(f"  {i}. {tool.label}")
        console.print("  0. Exit")

        choice = _prompt("Enter choice: ")
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(tools):
            return tools[int(choice) - 1]
        console.print("[red]Invalid choice, please try again.[/red]")


def _select_file(directory: Path) -> Optional[Path]:
    """Paginated file picker: lists every file in `directory`, 5 per page."""
    files = list_directory_files(directory)

    if not files:
        console.print(f"[yellow]No files found in {directory}[/yellow]")
        return None

    page = 0
    while True:
        chunk, total_pages, has_prev, has_next = paginate(files, page)

        console.print(f"\n[bold]Select a file[/bold] (page {page + 1}/{total_pages}):")
        for i, path in enumerate(chunk, start=1):
            console.print(f"  {i}. {path.name}")

        nav_options = []
        if has_prev:
            nav_options.append("p) Previous 5")
        if has_next:
            nav_options.append("n) Next 5")
        nav_options.append("c) Cancel (back to menu)")
        console.print("  " + "   ".join(nav_options))

        choice = _prompt("Enter choice: ").lower()
        if choice == "c":
            return None
        if choice == "n" and has_next:
            page += 1
            continue
        if choice == "p" and has_prev:
            page -= 1
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(chunk):
            return chunk[int(choice) - 1]
        console.print("[red]Invalid choice, please try again.[/red]")


def run_interactive(directory: Optional[Path] = None) -> None:
    directory = directory or Path.cwd()
    tools = _tool_registry()

    console.print("[bold]pdf-app[/bold] -- interactive mode. Ctrl+C to quit any time.")

    try:
        while True:
            tool = _select_tool(tools)
            if tool is None:
                console.print("Goodbye!")
                return

            # Retry file selection until the user picks a valid PDF or cancels
            # back to the tool menu.
            while True:
                file_path = _select_file(directory)
                if file_path is None:
                    break  # back to tool menu, no "run another?" prompt needed
                if file_path.suffix.lower() != ".pdf":
                    console.print(f"[red]Error:[/red] '{file_path.name}' is not a PDF file. Please pick a .pdf file.")
                    continue
                break

            if file_path is None:
                continue  # back to tool menu

            try:
                with console.status(f"Running '{tool.label}'..."):
                    output_path = tool.run(file_path)
                console.print(f"[green]Done:[/green] {output_path}")
            except Exception as exc:
                console.print(f"[red]Error:[/red] {exc}")

            if not _confirm("Run another action?", default=True):
                console.print("Goodbye!")
                return
    except (EOFError, KeyboardInterrupt):
        console.print("\nGoodbye!")
