from unittest.mock import patch

from pdfapp.interactive import _tool_registry, list_directory_files, paginate, run_interactive


def test_paginate_first_page_has_next_but_no_prev():
    files = list(range(12))  # stand-ins for Path objects
    chunk, total_pages, has_prev, has_next = paginate(files, page=0, page_size=5)

    assert chunk == [0, 1, 2, 3, 4]
    assert total_pages == 3
    assert has_prev is False
    assert has_next is True


def test_paginate_last_page_has_prev_but_no_next():
    files = list(range(12))
    chunk, total_pages, has_prev, has_next = paginate(files, page=2, page_size=5)

    assert chunk == [10, 11]
    assert total_pages == 3
    assert has_prev is True
    assert has_next is False


def test_paginate_single_short_page():
    files = list(range(3))
    chunk, total_pages, has_prev, has_next = paginate(files, page=0, page_size=5)

    assert chunk == [0, 1, 2]
    assert total_pages == 1
    assert has_prev is False
    assert has_next is False


def test_list_directory_files_excludes_subdirectories(tmp_path):
    (tmp_path / "b.pdf").write_bytes(b"")
    (tmp_path / "a.txt").write_bytes(b"")
    (tmp_path / "subdir").mkdir()

    files = list_directory_files(tmp_path)

    assert [p.name for p in files] == ["a.txt", "b.pdf"]  # sorted, files only


def test_tool_registry_has_expected_tools_and_output_naming(sample_pdf):
    tools = {t.key: t for t in _tool_registry()}
    assert set(tools) == {"compress", "to-doc", "to-jpeg", "to-ppt"}

    output = tools["compress"].run(sample_pdf)
    assert output.name == f"{sample_pdf.stem}-compress.pdf"
    assert output.exists()

    output = tools["to-doc"].run(sample_pdf)
    assert output.name == f"{sample_pdf.stem}-to-doc.docx"
    assert output.exists()

    output = tools["to-jpeg"].run(sample_pdf)
    assert output.name == f"{sample_pdf.stem}-to-jpeg"
    assert output.is_dir()
    assert len(list(output.iterdir())) == 3

    output = tools["to-ppt"].run(sample_pdf)
    assert output.name == f"{sample_pdf.stem}-to-ppt.pptx"
    assert output.exists()


def _run_with_inputs(directory, inputs):
    with patch("builtins.input", side_effect=inputs):
        run_interactive(directory=directory)


def test_full_flow_compress_then_exit(tmp_path, sample_pdf, capsys):
    # sample_pdf lives in a pytest tmp_path already; reuse its parent dir
    # so the file picker has exactly one real file to find.
    directory = sample_pdf.parent
    inputs = [
        "1",  # menu: Compress PDF
        "1",  # file picker: only entry (sample_pdf)
        "n",  # "Run another action?" -> no
    ]

    _run_with_inputs(directory, inputs)

    output = directory / f"{sample_pdf.stem}-compress.pdf"
    assert output.exists()
    assert "Done:" in capsys.readouterr().out


def test_invalid_file_choice_reprompts_then_succeeds(tmp_path, sample_pdf, capsys):
    directory = sample_pdf.parent
    (directory / "notes.txt").write_bytes(b"hello")
    # Directory now has: notes.txt, sample.pdf (alphabetical) -> two entries.
    inputs = [
        "2",  # menu: Convert PDF to DOCX
        "1",  # file picker: notes.txt (wrong format)
        "2",  # file picker retry: sample.pdf
        "n",  # don't run another action
    ]

    _run_with_inputs(directory, inputs)

    out = capsys.readouterr().out
    assert "not a PDF file" in out
    output = directory / f"{sample_pdf.stem}-to-doc.docx"
    assert output.exists()


def test_pagination_next_and_previous_navigate_pages(tmp_path, capsys):
    for name in ["a.pdf", "b.pdf", "c.pdf", "d.pdf", "e.pdf", "f.pdf"]:
        (tmp_path / name).write_bytes(b"")

    inputs = [
        "1",  # menu: Compress PDF
        "n",  # file picker: go to next page (page 2, has f.pdf)
        "c",  # cancel file picker -> back to tool menu
        "0",  # exit
    ]

    _run_with_inputs(tmp_path, inputs)

    out = capsys.readouterr().out
    assert "page 1/2" in out
    assert "page 2/2" in out
    assert "f.pdf" in out


def test_exit_immediately():
    with patch("builtins.input", side_effect=["0"]):
        run_interactive(directory=None)  # should not raise
