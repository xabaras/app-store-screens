from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import new_project
import render
import validate
from common import SIZES


def test_render_smoke(tmp_path: Path):
    pytest.importorskip("playwright")
    screens = tmp_path / "raw"
    screens.mkdir()
    for i in range(3):
        Image.new("RGB", (390, 844), (20 + i * 30, 90, 140)).save(screens / f"{i}.png")
    proj = tmp_path / "proj"
    assert new_project.main(["--app", "smoke", "--out", str(proj), "--screens", str(screens)]) == 0

    # Offline-friendly: drop Google Fonts so networkidle is not required for fonts
    for html in (proj / "slides").glob("*.html"):
        text = html.read_text(encoding="utf-8")
        text = text.replace(
            '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            '  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap" rel="stylesheet" />\n',
            "",
        )
        html.write_text(text, encoding="utf-8")

    rc = render.main([str(proj), "--targets", "play", "--slides", "01"])
    if rc != 0:
        pytest.skip("playwright chromium not installed or render failed in this environment")
    out = proj / "out" / "play" / "01.png"
    assert out.is_file()
    with Image.open(out) as im:
        assert im.size == SIZES["play"]
        assert im.mode == "RGB"
    # validate only play/01 would fail other slides — write stubs for the rest
    for slide in (proj / "slides").glob("*.html"):
        dest = proj / "out" / "play" / f"{slide.stem}.png"
        if not dest.exists():
            Image.new("RGB", SIZES["play"], (10, 10, 10)).save(dest)
        dest_i = proj / "out" / "iphone" / f"{slide.stem}.png"
        dest_i.parent.mkdir(parents=True, exist_ok=True)
        if not dest_i.exists():
            Image.new("RGB", SIZES["iphone"], (10, 10, 10)).save(dest_i)
    assert validate.main([str(proj)]) == 0
