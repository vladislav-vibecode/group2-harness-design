#!/usr/bin/env python3
"""Export an HTML deck (templates/deck.html format) to PDF and/or PNGs with Playwright.

    python scripts/export_pdf.py deck.html out.pdf [--theme bloom] [--png outdir]

Requires: pip install playwright && playwright install chromium (or a preinstalled Chromium).
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html")
ap.add_argument("out", nargs="?")
ap.add_argument("--theme")
ap.add_argument("--png", help="directory for one PNG per slide")
a = ap.parse_args()

url = Path(a.html).resolve().as_uri() + "?print=1" + (f"&theme={a.theme}" if a.theme else "")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5)
    pg.goto(url)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    if a.out:
        pg.pdf(path=a.out, width="1280px", height="720px", print_background=True,
               prefer_css_page_size=True)
        print("pdf:", a.out)
    if a.png:
        Path(a.png).mkdir(parents=True, exist_ok=True)
        for i, el in enumerate(pg.query_selector_all(".slide"), 1):
            el.screenshot(path=f"{a.png}/slide-{i:02d}.png")
        print("png:", a.png)
    b.close()
