"""Shared paths and constants for app-store-screens."""

from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "template"
REPO_ROOT = SKILL_ROOT.parents[1]

SIZES = {
    "iphone": (1290, 2796),
    "play": (1080, 1920),
}

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def project_slides(project: Path, target: str | None = None) -> list[Path]:
    """HTML slides for a store target.

    Prefer ``slides/<target>/*.html`` when that folder exists and has HTML.
    Otherwise fall back to flat ``slides/*.html`` (legacy single set).
    """
    if target:
        nested = project / "slides" / target
        if nested.is_dir():
            slides = sorted(p for p in nested.glob("*.html") if p.is_file())
            if slides:
                return slides
    slides_dir = project / "slides"
    if not slides_dir.is_dir():
        return []
    return sorted(
        p
        for p in slides_dir.glob("*.html")
        if p.is_file() and p.parent == slides_dir
    )


def project_slide_stems(project: Path, targets: list[str] | None = None) -> list[str]:
    """Unique slide stems across targets (for validation messaging)."""
    targets = targets or list(SIZES)
    stems: set[str] = set()
    for t in targets:
        for p in project_slides(project, t):
            stems.add(p.stem)
    if not stems:
        for p in project_slides(project, None):
            stems.add(p.stem)
    return sorted(stems)
