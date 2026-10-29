---
name: app-store-screens
description: >-
  Create polished App Store and Google Play phone screenshots — marketing slides
  with headlines, themed graphics, and the user's real UI screenshots (optionally
  inside an iPhone or Pixel bezel as part of the theme). Use when the user asks
  for store screenshots, listing creatives, framed app screenshots, or something
  like ScreenshotWhale / store mockups. Generation only; never uploads.
---

# app-store-screens

Version: **1.1**

Input: an app + **3–6 user-provided UI screenshots** (+ optional brand art).  
Output: **3–4** store-ready PNGs for **iPhone (1290×2796)** and **Play phone (1080×1920)**.  
Nothing is uploaded.

`<skill>` = folder that holds this `SKILL.md`. Run scripts with the repo `.venv`
(`pip install -r requirements.txt` then `playwright install chromium`).

## CRITICAL — composition

1. **App UI is always the user's screenshot file** (`<img src="…">`). Never rebuild
   screens in HTML/CSS.
2. Logo / illustrations from the user stay as image files too.
3. **Everything else** (background, type, claims, device bezel, shadows) is HTML/CSS.
4. Device frames are part of the **graphic theme**, not a bare wrap of a raw capture.

## CRITICAL — truthfulness

See `references/copy-rules.md`. Every claim needs a source in `DESIGN.md`. No invented
ratings, #1, testimonials, or features the app does not have.

## Inputs (ask for what is missing)

- App name; website URL; App Store id and/or Google Play package; storefront country.
- **Copy language** (optional; may differ from storefront). **Default: English (`en`)**.
  If the user does not mention a language, proceed in English — do not ask and wait.
  If they name a language, use it. If they ask for **multiple language variants**, create one
  project folder per locale under `~/store-screenshots/<slug>/<lang>/` (e.g. `…/en`, `…/it`);
  reuse the same screens/brand; translate claims faithfully from DESIGN sources; deliver each locale.
- Path to **3–6** raw screenshots (optional separate iOS / Android folders).
- Optional brand / app icon — **not** tied to Play. Resolve: user file → store listing icon
  (App Store and/or Play when available) → repo source (AppIcon / launcher). See
  `references/layout.md`. Copy to `assets/brand/icon.png`. Omit `.app-icon` by default
     unless there is a clear, non-intrusive placement the user likes.
  iOS-only or no Play asset is fine.
- Optional lifestyle photo path — **only** if the user asks for a full-bleed photo slide; never
  invent or download stock. Put the file under `assets/brand/` or `assets/lifestyle/`.
- N slides (default 4, min 3); output folder default
  `~/store-screenshots/<slug>/<lang>` (lang = user choice or `en`).

Do **not** capture from simulator/device in v1 — ask the user for PNGs.

## Workflow

Commands: `references/pipeline.md`. Sizes: `references/sizes.md`. Layouts: `references/layout.md`.

1. **Scaffold.**  
   `new_project.py --app <slug> --out ~/store-screenshots/<slug>/<lang> --lang <lang> [--name "…"]`  
   `--lang` defaults to `en` if the user did not choose another. Never leave slides at `<slug>/` root —
   always nest under `<lang>`. For extra locales, scaffold again into `…/<slug>/<other-lang>`.  
   Screens: `--screens DIR`, or `--screens-android DIR --screens-ios DIR` (creates
   `slides/iphone/` + `slides/play/` with matching assets).
2. **Research, then DESIGN.md.**  
   - `store_assets.py` for listing text (and optional reference store screens — not product shots if the user supplied UI).  
   - Website colours/fonts; repo strings read-only if a path is given.  
   - `sample_colors.py` on user screens / logo.  
   - Fill `DESIGN.md`: angle, sourced claims, palette, storyboard (3–4 rows).
3. **Compose slides.** Edit `slides/iphone/0N.html` and `slides/play/0N.html` (or flat `slides/0N.html`) + theme.css:
   - Style like store templates (ScreenshotWhale / ShotPass): bright color-block, benefit headline, not dark muddy washes.
   - Set `--bg` / `--bg-deep` / `--fg` / `--accent` (white on vivid, or dark ink on pastel).
   - Headline + optional subline from sourced claims.
   - Typography: Montserrat 900, large headlines (see `theme.css`).
   - `data-layout`: `claim-top` | `claim-top-flush` | `claim-top-blobs` | `claim-bottom` |
     `phones-overlap` | `lifestyle-bleed` | `graphic-hero`. Mix so slides are not identical.
   - `phones-overlap`: two `.phone.back` / `.phone.front` with real screens.
   - `claim-top-blobs`: include `.blobs` spans.
   - `lifestyle-bleed`: only if asked + user photo → `.bleed-photo`; no phone by default.
   - Optional `<img class="app-icon">` in the claim when `assets/brand/icon.png` exists
     (`fetch_icon.py`: user file → store → repo).
   - `phones-overlap`: same-direction tilt, heavy overlap; bleed **top**; claim **below**.
   - Phone class: `iphone` | `pixel` | `bare`. Screens use cover/top in-bezel (no black bands).

4. **Render.** `render.py <project>` → `out/iphone/*.png` and `out/play/*.png`.
5. **Validate.** `validate.py <project>` until OK (exact size, no alpha).
6. **Deliver.** List output paths + one-line rationale per slide. Stop. No store upload.

## Out of scope (v1)

Device capture guidance, tablets/iPad, feature graphic, store upload.
(Multi-language variants via `~/store-screenshots/<slug>/<lang>/` are in scope.)
