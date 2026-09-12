import pymupdf

from pdfapp.compress import compress_pdf


def _make_scanned_pdf(path, fill_color=(30, 120, 200), size=(1700, 2200)):
    """A single page that is entirely one large embedded image, like a scan."""
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # US Letter
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, *size))
    pix.set_rect(pix.irect, fill_color)
    page.insert_image(page.rect, pixmap=pix)
    doc.save(path)
    doc.close()
    return path


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


def test_compress_does_not_blank_a_full_page_scanned_image(tmp_path):
    fill_color = (30, 120, 200)
    scanned = _make_scanned_pdf(tmp_path / "scan.pdf", fill_color=fill_color)
    output = tmp_path / "scan_out.pdf"

    compress_pdf(scanned, output, level="high")  # most aggressive downsampling

    doc = pymupdf.open(output)
    try:
        page = doc[0]
        assert len(page.get_images(full=True)) == 1

        rendered = page.get_pixmap()
        sampled = rendered.pixel(rendered.width // 2, rendered.height // 2)
        # Allow JPEG re-encoding drift, but it must resemble the original
        # fill color rather than come back white/black (i.e. blank/corrupt).
        assert all(abs(c - e) < 40 for c, e in zip(sampled, fill_color)), sampled
    finally:
        doc.close()


def test_compress_rejects_unknown_level(sample_pdf, tmp_path):
    try:
        compress_pdf(sample_pdf, tmp_path / "out.pdf", level="ultra")
        assert False, "expected ValueError"
    except ValueError:
        pass
