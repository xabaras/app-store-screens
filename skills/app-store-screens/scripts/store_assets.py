#!/usr/bin/env python3
"""Fetch store listing metadata (and optional reference screenshots).

App Store: iTunes lookup → metadata + research screens at full size.
Google Play: public page title/description + known ads/IAP labels.

Product shots for the marketing slides should come from the user. Store
screenshots here are research reference only.

Usage: store_assets.py --out DIR [--app-store-id ID | --bundle ID] [--play PACKAGE]
                       [--country us] [--lang en] [--no-screens]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
FULL_SIZE = "1290x2796bb.png"
_SIZE_SEGMENT = re.compile(r"/\d+x\d+bb\.(png|jpg|jpeg|webp)$")

PLAY_LABELS = {
    "en": {"contains_ads": "Contains ads", "in_app_purchases": "In-app purchases"},
    "it": {"contains_ads": "Contiene annunci", "in_app_purchases": "Acquisti in-app"},
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def full_size_url(url: str) -> str:
    if not _SIZE_SEGMENT.search(url):
        return url
    return _SIZE_SEGMENT.sub("/" + FULL_SIZE, url)


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def lookup_url(app_store_id=None, bundle=None, country="us", lang="en") -> str:
    q = {"country": country, "lang": lang, "entity": "software"}
    q["id" if app_store_id else "bundleId"] = app_store_id or bundle
    return "https://itunes.apple.com/lookup?" + urllib.parse.urlencode(q)


def parse_lookup(doc: dict) -> dict | None:
    if not isinstance(doc, dict) or not doc.get("resultCount"):
        return None
    results = doc.get("results")
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        return None
    r = results[0]
    return {
        "name": r.get("trackName"),
        "seller": r.get("sellerName"),
        "bundle_id": r.get("bundleId"),
        "description": r.get("description"),
        "release_notes": r.get("releaseNotes"),
        "version": r.get("version"),
        "price": r.get("formattedPrice"),
        "genres": r.get("genres"),
        "icon": r.get("artworkUrl512"),
        "screenshots": r.get("screenshotUrls") or [],
        "store_url": r.get("trackViewUrl"),
    }


def download_screenshot(url: str, dest: Path, fetch_fn=fetch) -> Path:
    big = full_size_url(url)
    try:
        data = fetch_fn(big)
    except urllib.error.HTTPError as e:
        if e.code != 404 or big == url:
            raise
        log(f"note: {big} is 404; using {url}")
        data = fetch_fn(url)
        dest = dest.with_suffix(Path(urllib.parse.urlparse(url).path).suffix or ".png")
    dest.write_bytes(data)
    return dest


def _meta(page: str, attr: str, name: str) -> str | None:
    m = re.search(rf'<meta[^>]+{attr}="{re.escape(name)}"[^>]+content="([^"]*)"', page)
    if not m:
        m = re.search(rf'<meta[^>]+content="([^"]*)"[^>]+{attr}="{re.escape(name)}"', page)
    return html.unescape(m.group(1)) if m else None


def strip_store_suffix(title: str) -> str:
    return re.sub(r"\s+[-\u2013\u2014]\s+[^-\u2013\u2014]*Google Play\s*$", "", title)


def parse_play(page: str, lang: str) -> dict:
    out: dict = {}
    for key, attr, name in (("title", "property", "og:title"), ("description", "name", "description")):
        value = _meta(page, attr, name)
        if value is None:
            log(f"note: Play {key} not found; not written")
        else:
            out[key] = strip_store_suffix(value) if key == "title" else value
    labels = PLAY_LABELS.get(lang)
    if labels is None:
        log(f"note: no known Play label strings for lang {lang!r}")
        return out
    for key, text in labels.items():
        if re.search(r">\s*" + re.escape(text) + r"\s*<", page):
            out[key] = True
    return out


class AppStoreError(Exception):
    pass


def app_store(a, out: Path, fetch_fn, download_screens: bool) -> dict:
    url = lookup_url(a.app_store_id, a.bundle, a.country, a.lang)
    try:
        doc = json.loads(fetch_fn(url))
    except (urllib.error.URLError, ValueError) as e:
        raise AppStoreError(f"App Store lookup failed ({e})")
    app = parse_lookup(doc)
    if app is None:
        raise AppStoreError(f"no app for {a.app_store_id or a.bundle} in {a.country}")
    if download_screens and app["screenshots"]:
        shots = out / "screens"
        shots.mkdir(exist_ok=True)
        saved = []
        for i, s in enumerate(app["screenshots"], 1):
            try:
                saved.append(str(download_screenshot(s, shots / f"{i:02d}.png", fetch_fn)))
            except (urllib.error.URLError, OSError, ValueError) as e:
                for part in [*saved, *shots.glob(f"{i:02d}.*")]:
                    Path(part).unlink(missing_ok=True)
                raise AppStoreError(f"screenshot download failed ({s}: {e})")
        app["saved_screenshots"] = saved
    return app


def main(argv: list[str] | None = None, fetch_fn=fetch) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--app-store-id")
    ap.add_argument("--bundle")
    ap.add_argument("--play")
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    ap.add_argument(
        "--no-screens",
        action="store_true",
        help="metadata only; skip downloading App Store reference screenshots",
    )
    a = ap.parse_args(argv)
    if not (a.app_store_id or a.bundle or a.play):
        ap.error("give --app-store-id, --bundle or --play")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metadata.json").unlink(missing_ok=True)
    for old in (out / "screens").glob("[0-9][0-9].*"):
        old.unlink()

    meta: dict = {"country": a.country, "lang": a.lang}
    app_store_error = None
    if a.app_store_id or a.bundle:
        try:
            meta["app_store"] = app_store(a, out, fetch_fn, download_screens=not a.no_screens)
        except AppStoreError as e:
            app_store_error = str(e)
            log(f"error: {e}")

    if a.play:
        q = urllib.parse.urlencode({"id": a.play, "hl": a.lang, "gl": a.country.upper()})
        url = f"https://play.google.com/store/apps/details?{q}"
        try:
            play = parse_play(fetch_fn(url).decode("utf-8", "replace"), a.lang)
            if play or not app_store_error:
                meta["google_play"] = {"package": a.play, **play}
        except (urllib.error.URLError, OSError, ValueError) as e:
            log(f"note: Play fetch failed ({e})")

    if app_store_error:
        if "google_play" not in meta:
            return 2
        meta["app_store_error"] = app_store_error

    (out / "metadata.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out / 'metadata.json'}")
    return 2 if app_store_error else 0


if __name__ == "__main__":
    sys.exit(main())
