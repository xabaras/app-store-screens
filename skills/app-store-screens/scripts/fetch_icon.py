#!/usr/bin/env python3
"""Resolve an app icon into assets/brand/icon.png.

Order: --file, then App Store / Play via research metadata or live lookup, then --repo.

Usage:
  fetch_icon.py --out PROJECT/assets/brand/icon.png [--file PATH]
                [--research PROJECT/research/metadata.json]
                [--repo /path/to/app]
                [--app-store-id ID | --bundle ID] [--play PACKAGE]
                [--country us] [--lang en]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)

# Prefer marketing / high-res launchers over tiny notification icons
REPO_GLOBS = [
    "**/ic_launcher-playstore.png",
    "**/ic_launcher-web.png",
    "**/AppIcon.appiconset/*.png",
    "**/mipmap-xxxhdpi/ic_launcher.png",
    "**/mipmap-xxxhdpi/ic_launcher.webp",
    "**/mipmap-xxhdpi/ic_launcher.png",
    "**/Assets.xcassets/AppIcon.appiconset/*.png",
    "**/app_icon*.png",
    "**/ic_launcher.png",
]


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def save_bytes(data: bytes, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def from_file(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    log(f"icon from file: {src}")
    return True


def from_metadata(meta_path: Path, dest: Path) -> bool:
    if not meta_path.is_file():
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    url = None
    store = meta.get("app_store") if isinstance(meta.get("app_store"), dict) else None
    if store and store.get("icon"):
        url = store["icon"]
    play = meta.get("google_play") if isinstance(meta.get("google_play"), dict) else None
    if not url and play and play.get("icon"):
        url = play["icon"]
    if not url:
        return False
    try:
        save_bytes(fetch(url), dest)
        log(f"icon from research metadata: {url}")
        return True
    except (urllib.error.URLError, OSError, ValueError) as e:
        log(f"note: metadata icon download failed ({e})")
        return False


def itunes_icon(app_store_id=None, bundle=None, country="us", lang="en") -> str | None:
    q = {"country": country, "lang": lang, "entity": "software"}
    q["id" if app_store_id else "bundleId"] = app_store_id or bundle
    url = "https://itunes.apple.com/lookup?" + urllib.parse.urlencode(q)
    try:
        doc = json.loads(fetch(url))
    except (urllib.error.URLError, ValueError, json.JSONDecodeError):
        return None
    if not doc.get("resultCount"):
        return None
    r = doc["results"][0]
    return r.get("artworkUrl512") or r.get("artworkUrl100")


def play_icon(package: str, lang: str, country: str) -> str | None:
    """Best-effort: og:image on the Play details page."""
    q = urllib.parse.urlencode({"id": package, "hl": lang, "gl": country.upper()})
    url = f"https://play.google.com/store/apps/details?{q}"
    try:
        page = fetch(url).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None
    import re

    m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', page)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"', page)
    return m.group(1) if m else None


def from_repo(repo: Path, dest: Path) -> bool:
    if not repo.is_dir():
        return False
    candidates: list[Path] = []
    for pattern in REPO_GLOBS:
        candidates.extend(p for p in repo.glob(pattern) if p.is_file())
    if not candidates:
        return False

    def score(p: Path) -> tuple:
        # larger files first; prefer png over webp; prefer playstore/web names
        name = p.name.lower()
        boost = 0
        if "playstore" in name or "appicon" in name or "web" in name:
            boost = 10**9
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        return (boost + size,)

    best = max(candidates, key=score)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, dest)
    log(f"icon from repo: {best}")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path, help="destination icon path")
    ap.add_argument("--file", type=Path, help="explicit icon/logo file")
    ap.add_argument("--research", type=Path, help="metadata.json from store_assets")
    ap.add_argument("--repo", type=Path, help="app source tree (read-only)")
    ap.add_argument("--app-store-id")
    ap.add_argument("--bundle")
    ap.add_argument("--play")
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args(argv)
    dest = a.out.expanduser().resolve()

    if a.file and from_file(a.file.expanduser().resolve(), dest):
        print(dest)
        return 0
    if a.research and from_metadata(a.research.expanduser().resolve(), dest):
        print(dest)
        return 0

    # Live store lookups (App Store first — works for iOS-only)
    url = None
    if a.app_store_id or a.bundle:
        url = itunes_icon(a.app_store_id, a.bundle, a.country, a.lang)
        if url:
            try:
                save_bytes(fetch(url), dest)
                log(f"icon from App Store: {url}")
                print(dest)
                return 0
            except (urllib.error.URLError, OSError, ValueError) as e:
                log(f"note: App Store icon failed ({e})")
    if a.play:
        url = play_icon(a.play, a.lang, a.country)
        if url:
            try:
                save_bytes(fetch(url), dest)
                log(f"icon from Play og:image: {url}")
                print(dest)
                return 0
            except (urllib.error.URLError, OSError, ValueError) as e:
                log(f"note: Play icon failed ({e})")

    if a.repo and from_repo(a.repo.expanduser().resolve(), dest):
        print(dest)
        return 0

    log("error: no icon found (give --file, store ids, research metadata, or --repo)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
