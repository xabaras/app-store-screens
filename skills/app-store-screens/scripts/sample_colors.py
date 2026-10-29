#!/usr/bin/env python3
"""Sample colours from a screenshot at named points in RELATIVE coordinates.

points.json: {"screen_bg": [0.5, 0.02], "card": [0.3, 0.41], ...}   (x, y as 0-1)
Each colour is the per-channel median of a small box around the point.

Usage: sample_colors.py <image> <points.json> [--box 0.006]
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from PIL import Image


def sample(img: Image.Image, points: dict, box: float = 0.006) -> dict[str, str]:
    rgb = np.asarray(img.convert("RGB"))
    h, w = rgb.shape[:2]
    r = max(1, int(round(box * w)))
    out: dict[str, str] = {}
    for name, xy in points.items():
        if not (
            isinstance(xy, (list, tuple))
            and len(xy) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in xy)
        ):
            raise ValueError(f"{name}: a point is [x, y] with two numbers 0-1, got {xy!r}")
        x, y = xy
        if not (0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError(f"{name}: coordinates must be 0-1, got {x}, {y}")
        cx, cy = int(round(x * (w - 1))), int(round(y * (h - 1)))
        patch = rgb[max(0, cy - r) : cy + r + 1, max(0, cx - r) : cx + r + 1].reshape(-1, 3)
        med = np.median(patch, axis=0).round().astype(int)
        out[name] = "#{:02X}{:02X}{:02X}".format(*med)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("points")
    ap.add_argument("--box", type=float, default=0.006, help="half box size, as a fraction of width")
    a = ap.parse_args(argv)
    if not 0 < a.box < 0.5:
        print(f"error: --box must be between 0 and 0.5, got {a.box:g}", file=sys.stderr)
        return 2
    try:
        with open(a.points, encoding="utf-8") as f:
            points = json.load(f)
        if not isinstance(points, dict):
            raise ValueError(f"{a.points} must hold a JSON object of name: [x, y]")
        print(json.dumps(sample(Image.open(a.image), points, a.box), indent=1))
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
