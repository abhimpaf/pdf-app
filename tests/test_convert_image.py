from PIL import Image

from pdfapp.convert_image import pdf_to_jpeg


def test_pdf_to_jpeg_creates_one_image_per_page(sample_pdf, tmp_path):
    out_dir = tmp_path / "images"
    paths = pdf_to_jpeg(sample_pdf, out_dir, dpi=100, quality=80)

    assert len(paths) == 3
    for p in paths:
        assert p.exists()
        assert p.suffix == ".jpg"
        with Image.open(p) as im:
            im.verify()  # raises if not a valid image
