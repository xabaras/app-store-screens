# Pipeline commands

`<skill>` = folder that holds this skill's `SKILL.md`.
Use the repo `.venv` Python after `pip install -r requirements.txt` and `playwright install chromium`.

## Scaffold

```bash
python <skill>/scripts/new_project.py --app <slug> --out ~/store-screenshots/<slug>
```

Optional: `--screens /path/to/dir` copies PNG/JPEG into `assets/screens/`.
`--brand /path/to/dir` copies into `assets/brand/`.

Separate platform screens (preferred when UI differs):

```bash
python <skill>/scripts/new_project.py --app <slug> --out DIR --lang it \
  --screens-android /path/android --screens-ios /path/ios
```

Creates `assets/screens/{android,ios}/` and `slides/{iphone,play}/` (iPhone bezel + iOS
shots; Pixel bezel + Android shots). `render.py` / `validate.py` use those folders.

## Research

```bash
python <skill>/scripts/store_assets.py --out <project>/research \
  [--play PACKAGE] [--bundle ID | --app-store-id ID] [--country it] [--lang it]
```

Store screenshots under `research/screens/` are **reference only** when the user supplied product shots.

```bash
python <skill>/scripts/fetch_icon.py --out <project>/assets/brand/icon.png \
  [--file PATH] [--research <project>/research/metadata.json] \
  [--repo /path/to/app] [--play PACKAGE] [--bundle ID | --app-store-id ID]
```

Icon order: `--file` → research/store artwork (App Store and/or Play) → `--repo` source. Not Play-only.

```bash
python <skill>/scripts/sample_colors.py <image> <points.json>
```

## Render

Fill `slides/*.html` (from the template), then:

```bash
python <skill>/scripts/render.py <project>
```

Writes `out/iphone/01.png` … and `out/play/01.png` … for each slide.

## Validate

```bash
python <skill>/scripts/validate.py <project>
```

Exit 0 = OK. Non-zero = fix sizes/alpha/missing files before delivering.
