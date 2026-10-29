# app-store-screens

AI agent skill that turns **raw app screenshots** into polished **App Store** and
**Google Play** phone listing images: themed background, short claims, and the
real UI (optionally inside an iPhone or Pixel bezel as part of the graphic).

- Product UI is always the user's PNG/JPEG — never rebuilt in HTML.
- Chrome (type, colour, frame, blobs) is HTML/CSS, exported with Playwright.
- v1 sizes: iPhone **1290×2796**, Play phone **1080×1920**.
- **3–4** slides per project (min 3).
- Generation only — does not upload to the stores.

## How it works

1. **Scaffold** a project folder (`new_project.py`) with `assets/`, `slides/`, and `DESIGN.md`.
2. **Research** listing copy and optional icon (`store_assets.py`, `fetch_icon.py`, `sample_colors.py`).
3. **Compose** HTML slides from sourced claims + user screens (`data-layout` + `theme.css`).
4. **Render** PNGs with Playwright (`render.py`).
5. **Validate** exact pixel size and no alpha (`validate.py`).

Agent instructions live in [`skills/app-store-screens/SKILL.md`](skills/app-store-screens/SKILL.md).
Pipeline details: [`skills/app-store-screens/references/pipeline.md`](skills/app-store-screens/references/pipeline.md).

## What to provide

### Required

| Input | Notes |
|-------|--------|
| **3–6 UI screenshots** | Paths to PNG/JPEG. Optional separate iOS / Android folders. Not captured from simulator in v1 — you supply the files. |
| **Copy language** | e.g. `en`, `it`. Must be stated; the skill does not invent or default it. |
| **App name / project slug** | Used for the output folder and slide titles. |

### Strongly recommended

| Input | Notes |
|-------|--------|
| App Store id and/or Play package (or store URL) | Listing text + optional icon from the store. |
| Website URL | Brand colours / fonts. |
| Slide count | Default **4**, minimum **3**. |

### Optional

| Input | Notes |
|-------|--------|
| **Brand icon / logo** | File or folder. Else: store artwork → app repo launcher/AppIcon via `fetch_icon.py`. `.app-icon` in the claim is **omitted by default**. |
| **Custom graphics** | Illustrations, hero art — see below. |
| **Lifestyle photo** | Only for a full-bleed slide — see below. Never invent or download stock. |
| App source repo path | Read-only, for icon / string research. |
| Output directory | Default `~/store-screenshots/<slug>`. |
| Storefront country | For store metadata fetch (independent of copy language). |

## Custom graphics

You can supply your own brand art (logo, illustrations, marketing graphics):

1. Pass a brand folder to scaffold (`--brand /path/to/dir`) or drop files under `assets/brand/` in the project.
2. Use layout `graphic-hero` on a slide and reference the image (e.g. `.hero-art`).
3. Do **not** invent or generate substitute brand art when none was provided.

The UI on the phone is still always a real screenshot file.

## Lifestyle full-bleed (`lifestyle-bleed`)

A slide that uses a **full-bleed photo** instead of (or without) a device frame:

- **Only** when you ask for it **and** provide a photo path.
- Place the file under `assets/lifestyle/` or `assets/brand/`.
- Set `data-layout="lifestyle-bleed"` and `<img class="bleed-photo" src="…">`.
- Claim typically bottom-left; **no phone by default**.
- Stock photos must not be invented or downloaded by the agent.

## Install

```bash
cd ~/code/app-store-screens   # or your clone path
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

Expose the skill to Cursor:

```bash
ln -sfn /path/to/app-store-screens ~/.cursor/skills/app-store-screens
```

## Quick use

Ask an agent to use **app-store-screens**, and provide the required inputs above.
Or drive the scripts yourself:

```bash
.venv/bin/python skills/app-store-screens/scripts/new_project.py \
  --app my-app --out ~/store-screenshots/my-app --lang en \
  --screens ./my-raw-screens

# Optional separate platforms:
#   --screens-android ./android --screens-ios ./ios
# Optional brand folder:
#   --brand ./brand-assets

# Edit slides (iphone/ + play/ or flat) and DESIGN.md, then:
.venv/bin/python skills/app-store-screens/scripts/render.py ~/store-screenshots/my-app
.venv/bin/python skills/app-store-screens/scripts/validate.py ~/store-screenshots/my-app
```

## Layouts

| `data-layout` | Role |
|---------------|------|
| `claim-top` | Headline above phone |
| `claim-top-flush` | Wider phone |
| `claim-top-blobs` | Claim-top + CSS blobs |
| `claim-bottom` | Phone above; headline below |
| `phones-overlap` | Two tilted phones, heavy overlap; bleed top; claim below |
| `lifestyle-bleed` | Full-bleed **user** photo |
| `graphic-hero` | Brand art + optional phone |

## Repo layout

```
skills/app-store-screens/   # SKILL.md + scripts + template + references
tests/
requirements.txt
```

## Licence

MIT for this repo's code and templates. User app screenshots and brand assets remain theirs.
