"""Entity extraction: contact info, dates, language detection."""
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{1,4}\)?[\s.-]?)?\d{2,4}(?:[\s.-]?\d{2,4}){1,4}"
)
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[A-Za-z0-9_-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[A-Za-z0-9_-]+", re.I)

# Bilingual month names for date range extraction
MONTHS = (
    "jan(?:v(?:ier)?|uary)?|f[ée]v(?:rier)?|feb(?:ruary)?|mar(?:s|ch)?|"
    "avr(?:il)?|apr(?:il)?|mai|may|juin|june?|juil(?:let)?|july?|"
    "ao[ûu]t|aug(?:ust)?|sep(?:t(?:embre|ember)?)?|oct(?:obre|ober)?|"
    "nov(?:embre|ember)?|d[ée]c(?:embre|ember)?"
)
DATE_RANGE_RE = re.compile(
    rf"((?:{MONTHS})\.?\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
    rf"\s*(?:-|–|—|to|à|a|au|until|jusqu'[àa])\s*"
    rf"((?:{MONTHS})\.?\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}}|pr[ée]sent|present|"
    rf"aujourd'hui|current|now|actuel(?:lement)?|en cours|ongoing)",
    re.I,
)


def detect_language(text: str) -> str:
    """Detect language of a text block. Returns 'fr', 'en', or 'other'."""
    try:
        from langdetect import detect
        code = detect(text)
        return code if code in ("fr", "en") else "other"
    except Exception:
        return "other"


def extract_contact(text: str) -> dict:
    """Extract contact entities from CV text (usually the header section)."""
    emails = EMAIL_RE.findall(text)
    linkedin = LINKEDIN_RE.findall(text)
    github = GITHUB_RE.findall(text)
    # phone: filter matches that are mostly digits and plausible length
    phones = []
    for m in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", m)
        if 8 <= len(digits) <= 15 and m not in emails:
            phones.append(m.strip())
    return {
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones))[:3],
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
    }


def guess_name(header_text: str) -> str | None:
    """Heuristic: the name is usually the first short line without digits/@."""
    for line in header_text.splitlines():
        s = line.strip()
        if not s or "@" in s or any(ch.isdigit() for ch in s):
            continue
        words = s.split()
        if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
            return s
    return None


def extract_date_ranges(text: str) -> list[dict]:
    """Extract (start, end) date ranges from experience/education text."""
    out = []
    for m in DATE_RANGE_RE.finditer(text):
        out.append({"start": m.group(1), "end": m.group(2), "raw": m.group(0)})
    return out
