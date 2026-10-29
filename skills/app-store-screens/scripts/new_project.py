#!/usr/bin/env python3
"""Scaffold a store-screenshots project folder.

Usage:
  new_project.py --app <slug> --out DIR
                 [--screens DIR]
                 [--screens-android DIR] [--screens-ios DIR]
                 [--brand DIR] [--name "App Name"] [--lang it]
                 [--dual]

With ``--screens-android`` / ``--screens-ios`` (or ``--dual`` after a single
``--screens``), creates ``slides/iphone/`` and ``slides/play/`` with platform
bezels and screen paths under ``assets/screens/{ios,android}/``.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from common import IMAGE_SUFFIXES, TEMPLATE_DIR

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def copy_images(src: Path, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    files = sorted(
        p for p in src.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )
    for i, p in enumerate(files, 1):
        target = dest / f"{i:02d}{p.suffix.lower()}"
        shutil.copy2(p, target)
        saved.append(target)
    return saved


def fill_template(text: str, mapping: dict[str, str]) -> str:
    out = text
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def write_slide(
    dest: Path,
    *,
    tmpl: str,
    lang: str,
    slide_id: str,
    name: str,
    frame: str,
    screen_src: str,
    layout: str = "claim-top",
) -> None:
    html = fill_template(
        tmpl,
        {
            "LANG": lang,
            "SLIDE_ID": slide_id,
            "APP_NAME": name,
            "BG": "#ff7a2f",
            "BG2": "#ff6a1a",
            "FG": "#ffffff",
            "ACCENT": "#ffe566",
            "MUTED": "rgba(255, 255, 255, 0.92)",
            "LAYOUT": layout,
            "FRAME": frame,
            "HEADLINE": f"Headline {slide_id}",
            "SUBLINE": "Replace with a sourced claim",
            "SCREEN_SRC": screen_src,
            "SCREEN_ALT": f"{name} screen {slide_id}",
        },
    )
    dest.write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", required=True, help="slug, e.g. busdroid-genova")
    ap.add_argument("--out", required=True, help="project directory to create")
    ap.add_argument("--name", default="", help="display name (default: slug)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--screens", type=Path, help="single folder of screens (flat or with --dual)")
    ap.add_argument("--screens-android", type=Path, help="Android screens → assets/screens/android")
    ap.add_argument("--screens-ios", type=Path, help="iOS screens → assets/screens/ios")
    ap.add_argument(
        "--dual",
        action="store_true",
        help="create slides/iphone and slides/play (implied by --screens-android/--screens-ios)",
    )
    ap.add_argument("--brand", type=Path, help="folder of logos / art to copy")
    a = ap.parse_args(argv)

    if not SLUG_RE.match(a.app):
        print(f"error: --app must be a lowercase slug, got {a.app!r}", file=sys.stderr)
        return 2

    dual = a.dual or bool(a.screens_android or a.screens_ios)

    out = Path(a.out).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        print(f"error: {out} already exists and is not empty", file=sys.stderr)
        return 2

    subs = [
        "assets/screens",
        "assets/brand",
        "assets/fonts",
        "slides",
        "research",
        "out/iphone",
        "out/play",
    ]
    if dual:
        subs.extend(["assets/screens/android", "assets/screens/ios", "slides/iphone", "slides/play"])
    for sub in subs:
        (out / sub).mkdir(parents=True, exist_ok=True)

    name = a.name or a.app.replace("-", " ").title()
    design = (TEMPLATE_DIR / "DESIGN.md.tmpl").read_text(encoding="utf-8")
    (out / "DESIGN.md").write_text(
        fill_template(design, {"APP_NAME": name}),
        encoding="utf-8",
    )

    shutil.copy2(TEMPLATE_DIR / "theme.css", out / "slides" / "theme.css")
    if dual:
        shutil.copy2(TEMPLATE_DIR / "theme.css", out / "slides" / "iphone" / "theme.css")
        shutil.copy2(TEMPLATE_DIR / "theme.css", out / "slides" / "play" / "theme.css")

    android_files: list[Path] = []
    ios_files: list[Path] = []
    flat_files: list[Path] = []

    if a.screens_android:
        if not a.screens_android.is_dir():
            print(f"error: --screens-android is not a directory: {a.screens_android}", file=sys.stderr)
            return 2
        android_files = copy_images(a.screens_android, out / "assets" / "screens" / "android")
    if a.screens_ios:
        if not a.screens_ios.is_dir():
            print(f"error: --screens-ios is not a directory: {a.screens_ios}", file=sys.stderr)
            return 2
        ios_files = copy_images(a.screens_ios, out / "assets" / "screens" / "ios")

    if a.screens:
        if not a.screens.is_dir():
            print(f"error: --screens is not a directory: {a.screens}", file=sys.stderr)
            return 2
        if dual and not android_files and not ios_files:
            # Same set copied to both platform folders
            android_files = copy_images(a.screens, out / "assets" / "screens" / "android")
            ios_files = copy_images(a.screens, out / "assets" / "screens" / "ios")
        elif not dual:
            flat_files = copy_images(a.screens, out / "assets" / "screens")

    if a.brand:
        if not a.brand.is_dir():
            print(f"error: --brand is not a directory: {a.brand}", file=sys.stderr)
            return 2
        copy_images(a.brand, out / "assets" / "brand")

    tmpl = (TEMPLATE_DIR / "slide.html.tmpl").read_text(encoding="utf-8")

    if dual:
        n = max(
            3,
            min(
                4,
                max(len(android_files), len(ios_files), 4),
            ),
        )
        # Prefer count from whichever set we have
        counts = [c for c in (len(android_files), len(ios_files)) if c]
        if counts:
            n = max(3, min(4, max(counts)))
        for i in range(1, n + 1):
            sid = f"{i:02d}"
            if ios_files and i <= len(ios_files):
                ios_src = f"../../assets/screens/ios/{ios_files[i - 1].name}"
            else:
                ios_src = f"../../assets/screens/ios/{sid}.png"
            if android_files and i <= len(android_files):
                and_src = f"../../assets/screens/android/{android_files[i - 1].name}"
            else:
                and_src = f"../../assets/screens/android/{sid}.png"
            write_slide(
                out / "slides" / "iphone" / f"{sid}.html",
                tmpl=tmpl,
                lang=a.lang,
                slide_id=sid,
                name=name,
                frame="iphone",
                screen_src=ios_src,
            )
            write_slide(
                out / "slides" / "play" / f"{sid}.html",
                tmpl=tmpl,
                lang=a.lang,
                slide_id=sid,
                name=name,
                frame="pixel",
                screen_src=and_src,
            )
    else:
        n = max(3, min(4, len(flat_files) or 4))
        for i in range(1, n + 1):
            sid = f"{i:02d}"
            src = f"../assets/screens/{sid}.png"
            if flat_files and i <= len(flat_files):
                src = f"../assets/screens/{flat_files[i - 1].name}"
            write_slide(
                out / "slides" / f"{sid}.html",
                tmpl=tmpl,
                lang=a.lang,
                slide_id=sid,
                name=name,
                frame="iphone",
                screen_src=src,
            )

    (out / "project.json").write_text(
        json.dumps(
            {
                "app": a.app,
                "name": name,
                "lang": a.lang,
                "dual": dual,
                "screens_android": len(android_files),
                "screens_ios": len(ios_files),
                "screens_copied": len(flat_files),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
