from __future__ import annotations

from pathlib import Path

from PIL import Image

import sample_colors


def test_sample_median(tmp_path: Path):
    path = tmp_path / "a.png"
    Image.new("RGB", (100, 100), (10, 20, 30)).save(path)
    points = tmp_path / "p.json"
    points.write_text('{"bg": [0.5, 0.5]}\n', encoding="utf-8")
    out = sample_colors.sample(Image.open(path), {"bg": [0.5, 0.5]})
    assert out["bg"] == "#0A141E"
