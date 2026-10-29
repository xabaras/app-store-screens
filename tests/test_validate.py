from __future__ import annotations

from pathlib import Path

from PIL import Image

import new_project
import validate
from common import SIZES


def test_validate_ok_and_fail(tmp_path: Path):
    screens = tmp_path / "raw"
    screens.mkdir()
    Image.new("RGB", (100, 200), (1, 2, 3)).save(screens / "a.png")
    Image.new("RGB", (100, 200), (4, 5, 6)).save(screens / "b.png")
    Image.new("RGB", (100, 200), (7, 8, 9)).save(screens / "c.png")
    proj = tmp_path / "proj"
    assert new_project.main(["--app", "t", "--out", str(proj), "--screens", str(screens)]) == 0

    # missing outs → fail
    assert validate.main([str(proj)]) == 1

    for target, size in SIZES.items():
        d = proj / "out" / target
        d.mkdir(parents=True, exist_ok=True)
        for slide in (proj / "slides").glob("*.html"):
            Image.new("RGB", size, (40, 40, 40)).save(d / f"{slide.stem}.png")

    assert validate.main([str(proj)]) == 0

    # alpha fails
    bad = proj / "out" / "iphone" / "01.png"
    Image.new("RGBA", SIZES["iphone"], (0, 0, 0, 128)).save(bad)
    assert validate.main([str(proj)]) == 1
