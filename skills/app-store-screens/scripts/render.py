#!/usr/bin/env python3
"""Render project slides to store-sized PNGs with Playwright.

Looks for ``slides/<target>/*.html`` first (iphone / play). If missing, uses
flat ``slides/*.html`` for every requested target.

Usage: render.py <project> [--targets iphone,play] [--slides 01,02]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from common import SIZES, project_slides


def flatten_no_alpha(path: Path) -> None:
    """Ensure 24-bit RGB PNG (stores reject alpha)."""
    with Image.open(path) as im:
        if im.mode == "RGB":
            return
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if im.mode in ("RGBA", "LA"):
            rgba = im.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
        else:
            bg.paste(im.convert("RGB"))
        bg.save(path, format="PNG")


def theme_path_for(slide: Path, project: Path) -> Path | None:
    """theme.css next to the slide, else slides/theme.css."""
    local = slide.parent / "theme.css"
    if local.is_file():
        return local
    shared = project / "slides" / "theme.css"
    return shared if shared.is_file() else None


def render_project(project: Path, targets: list[str], only: set[str] | None) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "error: playwright is not installed. "
            "pip install -r requirements.txt && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    errors = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for target in targets:
                if target not in SIZES:
                    print(f"error: unknown target {target!r}", file=sys.stderr)
                    errors += 1
                    continue
                slides = project_slides(project, target)
                if only:
                    slides = [s for s in slides if s.stem in only]
                if not slides:
                    print(f"error: no slides for target {target!r}", file=sys.stderr)
                    errors += 1
                    continue
                if theme_path_for(slides[0], project) is None:
                    print(f"error: missing theme.css for {target}", file=sys.stderr)
                    errors += 1
                    continue

                w, h = SIZES[target]
                out_dir = project / "out" / target
                out_dir.mkdir(parents=True, exist_ok=True)
                for slide in slides:
                    dest = out_dir / f"{slide.stem}.png"
                    page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
                    try:
                        page.goto(slide.resolve().as_uri(), wait_until="load", timeout=60_000)
                        page.evaluate("() => document.fonts ? document.fonts.ready : null")
                        page.wait_for_timeout(400)
                        page.screenshot(path=str(dest), type="png", omit_background=False)
                    except Exception as e:
                        print(f"error: {slide} → {target}: {e}", file=sys.stderr)
                        errors += 1
                        continue
                    finally:
                        page.close()
                    flatten_no_alpha(dest)
                    print(dest)
        finally:
            browser.close()
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--targets", default="iphone,play", help="comma list: iphone,play")
    ap.add_argument("--slides", default="", help="optional comma list of stems, e.g. 01,02")
    a = ap.parse_args(argv)
    project = a.project.expanduser().resolve()
    if not project.is_dir():
        print(f"error: not a directory: {project}", file=sys.stderr)
        return 2
    targets = [t.strip() for t in a.targets.split(",") if t.strip()]
    only = {s.strip() for s in a.slides.split(",") if s.strip()} or None
    return render_project(project, targets, only)


if __name__ == "__main__":
    sys.exit(main())
