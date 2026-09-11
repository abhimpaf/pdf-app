import pymupdf
import pytest


@pytest.fixture
def sample_pdf(tmp_path):
    """A small multi-page PDF with text and one embedded image, built on the fly."""
    path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Test page {i + 1} - Lorem ipsum dolor sit amet.", fontsize=20)
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 400, 300))
        pix.set_rect(pix.irect, (120, 160, 200))
        page.insert_image(pymupdf.Rect(50, 150, 300, 350), pixmap=pix)
    doc.save(path)
    doc.close()
    return path
