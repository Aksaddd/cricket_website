#!/usr/bin/env python3
"""Generate web-optimized cover images (WebP + JPEG) into assets/.

The source cover/studio photos are 7-8 MB each and far too heavy to ship.
This downscales them to a sensible web width and re-encodes them. Run after
replacing any of the source images:

    pip install Pillow
    python3 optimize_images.py
"""
import os
from PIL import Image, ImageOps

OUT = "assets"

# source file -> (output basename, target width in px)
COVERS = {
    "03_front_wi_test_matches_cover.png":      ("wi-front",  1000),
    "04_back_wi_test_matches_cover.png":       ("wi-back",   1000),
    "01_front_test_cricket_records_cover.png": ("tcr-front", 1000),
    "02_back_test_cricket_records_cover.png":  ("tcr-back",  1000),
    "03_front_wi_test_matches_studio.jpg":     ("wi-studio",  1200),
    "01_front_test_cricket_records_studio.jpg":("tcr-studio", 1200),
}


def resize(im, width):
    if im.width <= width:
        return im
    height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def to_rgb(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for src, (base, width) in COVERS.items():
        if not os.path.exists(src):
            print(f"  skip (missing): {src}")
            continue
        im = resize(to_rgb(Image.open(src)), width)
        jpg = os.path.join(OUT, base + ".jpg")
        webp = os.path.join(OUT, base + ".webp")
        im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
        im.save(webp, "WEBP", quality=80, method=6)
        for f in (jpg, webp):
            kb = os.path.getsize(f) / 1024
            total += kb
            print(f"  {kb:7.1f} KB  {f}")
    print(f"\nTotal: {total/1024:.2f} MB")


if __name__ == "__main__":
    main()
