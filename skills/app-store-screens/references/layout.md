# Layout

## Composition rule

- **App UI** = user-provided screenshot files only (`<img>`). Never rebuild screens in HTML/CSS.
- **Brand art / icon / lifestyle photo** = user files (or store/repo icon) when provided — never invent.
- **Everything else** (background, type, claims, device bezel, blobs) = HTML/CSS.

## Visual direction

- Bright color-block or soft organic blobs — not muddy dark browns.
- Headlines: **Montserrat 900** (large); sublines 700+ with strong contrast.
- In-bezel UI: `object-fit: cover` + `object-position: top` so there are **no black letterbox bands**.
- Optional `.app-icon` only when placement is clearly good; omit by default even if an icon file exists.
- Lifestyle full-bleed photo **only** if the user asks **and** supplies a photo.

## Safe zones

- `claim-top` / `claim-top-blobs`: upper ~20–22%.
- `claim-bottom` / `lifestyle-bleed`: keep text above the bottom ~6–8%.
- `phones-overlap`: claim in the lower band; phones may clip the top edge.

## Layouts

| `data-layout` | Use when |
|---------------|----------|
| `claim-top` | Default: headline above phone; phone may bleed bottom |
| `claim-top-flush` | Wider phone |
| `claim-top-blobs` | claim-top + CSS blobs (include `.blobs`) |
| `claim-bottom` | Phone above; headline below |
| `phones-overlap` | Two phones, same-direction tilt, heavy overlap; bleed **top**; claim **below** |
| `lifestyle-bleed` | Full-bleed **user** photo; claim bottom-left; no phone unless also requested |
| `graphic-hero` | Brand art + optional phone |

## App icon

Not Play-specific. Resolve in this order (first hit wins), copy to `assets/brand/icon.png`:

1. Path the user gives (file or `--brand` folder containing an icon/logo).
2. Store listing artwork when a store id/package/URL is available — App Store `artworkUrl512` and/or Play icon from the public listing (iOS-only apps still work via App Store).
3. App **source** when a repo path is given: common launcher / AppIcon assets (e.g. `ic_launcher-playstore.png`, `mipmap-xxxhdpi/ic_launcher*.png`, `AppIcon.appiconset` largest PNG, Compose/Android/iOS branded assets). Prefer the highest-res marketing/launcher image, not a tiny notification icon.

If none exist, omit `.app-icon` — do not invent one.

Prefer no icon in the claim. If the user asks for it and placement works, use
`<img class="app-icon" src="../../assets/brand/icon.png" alt="" />` before the `<h1>` on at most 1–2 slides.
