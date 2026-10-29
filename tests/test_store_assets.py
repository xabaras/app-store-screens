from __future__ import annotations

import store_assets


def test_parse_lookup_keeps_safe_fields():
    doc = {
        "resultCount": 1,
        "results": [
            {
                "trackName": "Demo",
                "sellerName": "Acme",
                "bundleId": "com.acme.demo",
                "description": "Hello",
                "screenshotUrls": ["https://example.com/1x1bb.png"],
                "trackViewUrl": "https://apps.apple.com/app/id1",
                "averageUserRating": 4.9,
                "userRatingCount": 99999,
            }
        ],
    }
    app = store_assets.parse_lookup(doc)
    assert app["name"] == "Demo"
    assert "averageUserRating" not in app
    assert app["screenshots"] == ["https://example.com/1x1bb.png"]


def test_parse_play_labels_it():
    page = (
        '<meta property="og:title" content="BusDroid - Apps on Google Play"/>'
        '<meta name="description" content="Transit"/>'
        ">Contiene annunci<"
    )
    out = store_assets.parse_play(page, "it")
    assert out["title"] == "BusDroid"
    assert out["contains_ads"] is True


def test_full_size_url():
    u = "https://is1-ssl.mzstatic.com/image/thumb/Purple/x/y/z/123x456bb.png"
    assert store_assets.full_size_url(u).endswith("/1290x2796bb.png")
