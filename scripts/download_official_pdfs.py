"""This project already bundles the three user-provided PDF dataset files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "pdfs"
EXPECTED = {
    "prospectus_post_graduate.pdf",
    "prospectus_under_graduate.pdf",
    "rules_and_regulations.pdf",
}

missing = sorted(name for name in EXPECTED if not (PDF_DIR / name).exists())
if missing:
    raise SystemExit(
        "Missing bundled dataset files: " + ", ".join(missing) +
        ". Copy the supplied PDFs into data/pdfs/."
    )
print("All three supplied PDF dataset files are already present; no download is required.")
