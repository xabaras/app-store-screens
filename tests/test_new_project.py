from __future__ import annotations

from pathlib import Path

from PIL import Image

import new_project


def _make_png(path: Path, color=(20, 80, 120)) -> None:
    Image.new("RGB", (390, 844), color).save(path)


def test_scaffold_copies_screens_and_writes_slides(tmp_path: Path):
    screens = tmp_path / "raw"
    screens.mkdir()
    for i in range(3):
        _make_png(screens / f"shot{i}.png", (30 + i * 40, 60, 90))

    out = tmp_path / "proj"
    rc = new_project.main(
        ["--app", "demo-app", "--out", str(out), "--screens", str(screens), "--name", "Demo", "--lang", "it"]
    )
    assert rc == 0
    assert (out / "DESIGN.md").is_file()
    assert (out / "slides" / "theme.css").is_file()
    assert (out / "project.json").is_file()
    assert list((out / "assets" / "screens").glob("*.png"))
    htmls = list((out / "slides").glob("*.html"))
    assert len(htmls) == 3
    text = (out / "slides" / "01.html").read_text(encoding="utf-8")
    assert "Demo" in text
    assert "../assets/screens/" in text


def test_scaffold_dual_platform(tmp_path: Path):
    android = tmp_path / "and"
    ios = tmp_path / "ios"
    android.mkdir()
    ios.mkdir()
    for i in range(4):
        _make_png(android / f"a{i}.png", (10, 20, 30 + i))
        _make_png(ios / f"i{i}.png", (40, 50, 60 + i))
    out = tmp_path / "dual"
    rc = new_project.main(
        [
            "--app",
            "bus-demo",
            "--out",
            str(out),
            "--screens-android",
            str(android),
            "--screens-ios",
            str(ios),
            "--lang",
            "it",
        ]
    )
    assert rc == 0
    assert len(list((out / "assets" / "screens" / "android").glob("*.png"))) == 4
    assert len(list((out / "assets" / "screens" / "ios").glob("*.png"))) == 4
    assert (out / "slides" / "iphone" / "01.html").is_file()
    assert (out / "slides" / "play" / "01.html").is_file()
    iphone = (out / "slides" / "iphone" / "01.html").read_text(encoding="utf-8")
    play = (out / "slides" / "play" / "01.html").read_text(encoding="utf-8")
    assert "screens/ios/" in iphone
    assert 'class="phone iphone"' in iphone
    assert "screens/android/" in play
    assert 'class="phone pixel"' in play


def test_rejects_bad_slug(tmp_path: Path):
    rc = new_project.main(["--app", "Bad_Slug", "--out", str(tmp_path / "x")])
    assert rc == 2
