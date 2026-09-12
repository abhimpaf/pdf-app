from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz

# Target max dimension (px) and JPEG quality per compression level.
# Lower level = smaller file, more aggressive image downsampling.
_LEVELS = {
    "low": {"dpi_cap": 200, "jpeg_quality": 85},
    "medium": {"dpi_cap": 150, "jpeg_quality": 70},
    "high": {"dpi_cap": 100, "jpeg_quality": 50},
}


@dataclass
class CompressResult:
    input_size: int
    output_size: int

    @property
    def ratio(self) -> float:
        if self.input_size == 0:
            return 0.0
        return 1 - (self.output_size / self.input_size)


def _downsample_images(doc: fitz.Document, dpi_cap: int, jpeg_quality: int) -> None:
    """Re-encode embedded raster images that exceed the DPI cap as smaller JPEGs."""
    target_dim = max(dpi_cap * 11, 400)  # rough px budget for a ~8.5in-wide page
    seen_xrefs = set()

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                original_len = len(doc.xref_stream_raw(xref) or b"")

                pixmap = fitz.Pixmap(doc, xref)
                if pixmap.colorspace is None:
                    continue  # image mask / stencil, not a color image
                if pixmap.alpha:
                    pixmap = fitz.Pixmap(pixmap, 0)
                if pixmap.colorspace.n not in (1, 3):
                    pixmap = fitz.Pixmap(fitz.csRGB, pixmap)

                max_dim = max(pixmap.width, pixmap.height)
                shrink_factor = 0
                while max_dim > target_dim and shrink_factor < 4:
                    max_dim //= 2
                    shrink_factor += 1
                if shrink_factor:
                    pixmap.shrink(shrink_factor)

                jpeg_bytes = pixmap.tobytes("jpeg", jpg_quality=jpeg_quality)
                if original_len and len(jpeg_bytes) >= original_len:
                    continue  # re-encoding didn't help; keep the original stream

                # compress=0: the bytes are already JPEG-compressed, so the
                # default zlib-deflate pass would wrap them a second time
                # while we mark Filter as plain DCTDecode below, corrupting
                # the image (viewers try to JPEG-decode zlib-compressed data).
                doc.update_stream(xref, jpeg_bytes, compress=0)
                # The image dict's own metadata must match the new stream exactly,
                # or viewers decode the JPEG bytes against stale dimensions/filters
                # and the image renders blank or garbled.
                doc.xref_set_key(xref, "Filter", "/DCTDecode")
                doc.xref_set_key(xref, "DecodeParms", "null")
                doc.xref_set_key(xref, "Decode", "null")
                doc.xref_set_key(xref, "SMask", "null")
                doc.xref_set_key(xref, "Mask", "null")
                doc.xref_set_key(xref, "Width", str(pixmap.width))
                doc.xref_set_key(xref, "Height", str(pixmap.height))
                doc.xref_set_key(xref, "BitsPerComponent", "8")
                doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB" if pixmap.colorspace.n == 3 else "/DeviceGray")
            except Exception:
                continue  # leave this image untouched rather than fail the whole run


def compress_pdf(input_path: Path, output_path: Path, level: str = "medium") -> CompressResult:
    if level not in _LEVELS:
        raise ValueError(f"Unknown level '{level}'. Choose one of: {', '.join(_LEVELS)}")

    settings = _LEVELS[level]
    input_size = input_path.stat().st_size

    doc = fitz.open(input_path)
    try:
        _downsample_images(doc, settings["dpi_cap"], settings["jpeg_quality"])
        doc.save(
            output_path,
            garbage=4,      # remove unused/duplicate objects
            deflate=True,   # compress streams
            clean=True,     # sanitize/rewrite content streams
        )
    finally:
        doc.close()

    output_size = output_path.stat().st_size
    return CompressResult(input_size=input_size, output_size=output_size)
