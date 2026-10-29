#!/usr/bin/env python3
"""Validate rendered store screenshots.

Checks: expected files exist, exact pixel size, no alpha channel.
Uses ``slides/<target>/`` when present, else flat ``slides/``.

Usage: validate.py <project> [--targets iphone,play]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from common import SIZES, project_slides


def check_png(path: Path, size: tuple[int, int]) -> list[str]:
    errs: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    try:
        with Image.open(path) as im:
            if im.size != size:
                errs.append(f"{path.name}: size {im.size[0]}x{im.size[1]}, expected {size[0]}x{size[1]}")
            if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
                errs.append(f"{path.name}: has alpha/transparency (stores reject this)")
            elif im.mode not in ("RGB", "L"):
                if im.mode != "P":
                    errs.append(f"{path.name}: unexpected mode {im.mode}")
    except OSError as e:
        errs.append(f"{path.name}: cannot open ({e})")
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--targets", default="iphone,play")
    a = ap.parse_args(argv)
    project = a.project.expanduser().resolve()

    targets = [t.strip() for t in a.targets.split(",") if t.strip()]
    all_errs: list[str] = []
    any_slides = False
    for target in targets:
        if target not in SIZES:
            all_errs.append(f"unknown target {target!r}")
            continue
        slides = project_slides(project, target)
        if not slides:
            all_errs.append(f"no slides for target {target!r}")
            continue
        any_slides = True
        size = SIZES[target]
        for slide in slides:
            dest = project / "out" / target / f"{slide.stem}.png"
            all_errs.extend(check_png(dest, size))

    if not any_slides and not all_errs:
        print("error: no slides/*.html", file=sys.stderr)
        return 2

    if all_errs:
        for e in all_errs:
            print(f"error: {e}", file=sys.stderr)
        print(f"{len(all_errs)} problem(s)", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
