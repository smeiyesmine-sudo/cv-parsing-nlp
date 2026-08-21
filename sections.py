"""Split CV text into sections using bilingual (FR/EN) header detection."""
import re

# Canonical section -> header keywords (lowercase, FR + EN)
SECTION_HEADERS = {
    "profile": [
        "profil", "profile", "summary", "résumé", "resume", "about me",
        "à propos", "a propos", "objectif", "objective",
    ],
    "experience": [
        "expérience professionnelle", "experience professionnelle",
        "expériences professionnelles", "expérience", "experience",
        "work experience", "professional experience", "employment",
        "parcours professionnel", "stages", "internships",
    ],
    "education": [
        "formation", "formations", "education", "éducation", "studies",
        "études", "etudes", "diplômes", "diplomes", "academic background",
        "parcours académique", "parcours academique",
    ],
    "skills": [
        "compétences", "competences", "skills", "technical skills",
        "compétences techniques", "competences techniques", "hard skills",
        "soft skills", "savoir-faire", "expertise",
    ],
    "languages": [
        "langues", "languages", "language skills", "compétences linguistiques",
    ],
    "projects": [
        "projets", "projects", "projets académiques", "academic projects",
        "projets personnels", "personal projects", "réalisations",
    ],
    "certifications": [
        "certifications", "certificats", "certificates", "licences", "licenses",
    ],
    "interests": [
        "centres d'intérêt", "centres d'interet", "loisirs", "interests",
        "hobbies", "activités", "activities", "extracurricular",
    ],
    "contact": [
        "contact", "coordonnées", "coordonnees", "informations personnelles",
        "personal information",
    ],
}

# Flatten to (keyword, canonical) sorted longest-first so
# "compétences techniques" wins over "compétences"
_FLAT = sorted(
    [(kw, canon) for canon, kws in SECTION_HEADERS.items() for kw in kws],
    key=lambda x: -len(x[0]),
)


def _match_header(line: str):
    """Return canonical section name if the line looks like a section header."""
    stripped = line.strip().strip(":•-–—_ ").lower()
    if not stripped or len(stripped) > 60:
        return None
    for kw, canon in _FLAT:
        if stripped == kw or stripped.startswith(kw + " ") or stripped.startswith(kw + ":"):
            return canon
    return None


def split_sections(text: str) -> dict:
    """Split raw CV text into a dict {section_name: text}.

    Text before the first detected header goes into 'header'
    (usually name + contact info at the top of the CV).
    """
    sections = {}
    current = "header"
    buf = []
    for line in text.splitlines():
        canon = _match_header(line)
        if canon:
            if buf:
                sections[current] = sections.get(current, "") + "\n".join(buf) + "\n"
            current = canon
            buf = []
        else:
            buf.append(line)
    if buf:
        sections[current] = sections.get(current, "") + "\n".join(buf) + "\n"
    return sections
