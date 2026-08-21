"""End-to-end CV parsing pipeline.

Usage:
    # single file -> prints JSON
    python -m cv_parser.pipeline path/to/cv.pdf

    # several files
    python -m cv_parser.pipeline cv1.pdf cv2.docx photo_cv.jpg

    # a whole folder -> parses every supported CV inside,
    # writes one JSON per CV into ./output/ and prints a summary
    python -m cv_parser.pipeline samples
"""
import json
import sys
import traceback
from pathlib import Path

from .extract import extract_text
from .sections import split_sections
from .entities import (
    detect_language, extract_contact, guess_name, extract_date_ranges,
)
from .skills import extract_skills, group_by_category

SUPPORTED = {".pdf", ".docx", ".doc", ".pptx", ".ppt",
             ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff",
             ".txt", ".md"}
OUTPUT_DIR = Path("output")


def parse_cv(path: str) -> dict:
    """Parse a CV file into a structured JSON-able dict."""
    raw = extract_text(path)
    sections = split_sections(raw)

    header_text = sections.get("header", "") + sections.get("contact", "")
    contact = extract_contact(header_text or raw)

    # Detect language per section (CVs are often mixed FR/EN)
    section_langs = {
        name: detect_language(txt)
        for name, txt in sections.items() if len(txt.strip()) > 30
    }
    langs = [l for l in section_langs.values() if l != "other"]
    doc_lang = max(set(langs), key=langs.count) if langs else "unknown"

    # Skills: scan the whole document — skills often appear inside
    # experience bullets, not only in the skills section.
    skill_list = extract_skills(raw)

    dates = extract_date_ranges(
        sections.get("experience", "") + sections.get("education", "")
    )

    return {
        "file": str(path),
        "name": guess_name(header_text or raw),
        "contact": contact,
        "document_language": doc_lang,
        "section_languages": section_langs,
        "sections_found": list(sections.keys()),
        "skills": skill_list,
        "skills_by_category": group_by_category(skill_list),
        "date_ranges": dates,
        "extracted_chars": len(raw),
    }


def _expand(paths: list[str]) -> list[Path]:
    """Expand folder arguments into their supported files."""
    files = []
    for arg in paths:
        p = Path(arg)
        if p.is_dir():
            files += sorted(
                f for f in p.iterdir()
                if f.suffix.lower() in SUPPORTED and f.is_file()
            )
        else:
            files.append(p)
    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m cv_parser.pipeline <cv-file-or-folder> [...]")
        sys.exit(1)

    files = _expand(sys.argv[1:])
    if not files:
        print("No supported CV files found.")
        sys.exit(1)

    batch = len(files) > 1
    if batch:
        OUTPUT_DIR.mkdir(exist_ok=True)

    ok, failed = 0, 0
    for f in files:
        try:
            result = parse_cv(str(f))
            ok += 1
            if batch:
                out = OUTPUT_DIR / (f.stem + ".json")
                out.write_text(
                    json.dumps(result, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                n_skills = len(result["skills"])
                print(f"[OK]   {f.name:40s} -> {out}  "
                      f"({n_skills} skills, lang={result['document_language']})")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            failed += 1
            print(f"[FAIL] {f.name}: {e}")
            if not batch:
                traceback.print_exc()

    if batch:
        print(f"\nDone: {ok} parsed, {failed} failed. "
              f"JSON results in '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
