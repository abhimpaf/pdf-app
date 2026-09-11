import pymupdf

from pdfapp.compress import compress_pdf


def test_compress_reduces_size_and_preserves_pages(sample_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = compress_pdf(sample_pdf, output, level="high")

    assert output.exists()
    assert result.output_size <= result.input_size

    doc = pymupdf.open(output)
    try:
        assert doc.page_count == 3
        assert "Test page 1" in doc[0].get_text()
    finally:
        doc.close()


def test_compress_rejects_unknown_level(sample_pdf, tmp_path):
    try:
        compress_pdf(sample_pdf, tmp_path / "out.pdf", level="ultra")
        assert False, "expected ValueError"
    except ValueError:
        pass
