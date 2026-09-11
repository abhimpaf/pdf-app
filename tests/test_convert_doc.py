import zipfile

from pdfapp.convert_doc import pdf_to_docx


def test_pdf_to_docx_creates_valid_docx(sample_pdf, tmp_path):
    output = tmp_path / "out.docx"
    result = pdf_to_docx(sample_pdf, output)

    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0

    # A .docx is a zip archive; confirm it's structurally valid and has the
    # expected main document part.
    with zipfile.ZipFile(output) as zf:
        assert "word/document.xml" in zf.namelist()
