"""Skills identification, normalization and classification.

Two-pass matching against a bilingual skills database:
  1. Exact substring match (word-boundary aware) on aliases.
  2. Fuzzy match (RapidFuzz) on token n-grams to catch typos/variants.

Each matched skill is normalized to a canonical name and classified
into its predefined category from the database.
"""
import json
import re
from pathlib import Path

from rapidfuzz import fuzz

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_db.json"
FUZZY_THRESHOLD = 90  # conservative: avoids false positives


def load_db(path=DB_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _alias_index(db: dict):
    """Build [(alias, canonical, category)] sorted longest alias first."""
    idx = []
    for cat, catdata in db["categories"].items():
        for canonical, aliases in catdata["skills"].items():
            for alias in aliases:
                idx.append((alias.lower().strip(), canonical, cat))
    return sorted(idx, key=lambda x: -len(x[0]))


def _exact_matches(text_lower: str, index) -> dict:
    found = {}
    for alias, canonical, cat in index:
        # word-boundary match; escape regex chars in aliases like "c++"
        pattern = r"(?<![a-z0-9])" + re.escape(alias.strip()) + r"(?![a-z0-9+#])"
        if re.search(pattern, text_lower):
            if canonical not in found:
                found[canonical] = {"category": cat, "match": alias, "method": "exact"}
    return found


def _fuzzy_matches(text_lower: str, index, already: set) -> dict:
    """Fuzzy pass over 1-3 word n-grams for aliases >= 5 chars."""
    tokens = re.findall(r"[a-zà-ÿ0-9+#.'-]+", text_lower)
    ngrams = set()
    for n in (1, 2, 3):
        for i in range(len(tokens) - n + 1):
            ngrams.add(" ".join(tokens[i:i + n]))
    found = {}
    for alias, canonical, cat in index:
        if canonical in already or canonical in found or len(alias.strip()) < 5:
            continue
        for ng in ngrams:
            if abs(len(ng) - len(alias)) <= 3 and fuzz.ratio(ng, alias.strip()) >= FUZZY_THRESHOLD:
                found[canonical] = {"category": cat, "match": ng, "method": "fuzzy"}
                break
    return found


def extract_skills(text: str, db: dict | None = None) -> list[dict]:
    """Extract, normalize and classify skills from CV text.

    Returns a list of dicts:
      {"skill": canonical, "category": cat, "category_label": ...,
       "matched_text": ..., "method": "exact"|"fuzzy"}
    """
    db = db or load_db()
    index = _alias_index(db)
    text_lower = text.lower()

    matches = _exact_matches(text_lower, index)
    matches.update(_fuzzy_matches(text_lower, index, set(matches)))

    results = []
    for canonical, info in matches.items():
        cat = info["category"]
        results.append({
            "skill": canonical,
            "category": cat,
            "category_label_en": db["categories"][cat]["label_en"],
            "category_label_fr": db["categories"][cat]["label_fr"],
            "matched_text": info["match"],
            "method": info["method"],
        })
    return sorted(results, key=lambda r: (r["category"], r["skill"]))


def group_by_category(skill_list: list[dict]) -> dict:
    """Group extracted skills into {category: [skill names]}."""
    grouped = {}
    for s in skill_list:
        grouped.setdefault(s["category"], []).append(s["skill"])
    return grouped
