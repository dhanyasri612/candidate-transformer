from models.canonical_schema import Candidate


def build_candidate(
    full_name=None,
    emails=None,
    phones=None,
    skills=None,
    education=None,
    experience=None,
    location=None,
    links=None,
    source=None,
):
    """
    Creates a Candidate object with initialized provenance, confidence, and source tracking.

    - provenance: dict[field -> list[source_names]] — all sources that contributed to this field
    - confidence: dict[field -> float]              — confidence score based on source count
    - field_source: dict[field -> str]              — the primary (winning) source for this field
    """

    candidate = Candidate(
        full_name=full_name,
        emails=emails or [],
        phones=phones or [],
        skills=skills or [],
        education=education or [],
        experience=experience or [],
        location=location,
        links=links or {},
        source=source,
    )

    # --- Provenance: which sources contributed to each field ---
    candidate.provenance = {
        "full_name":  [source] if full_name  else [],
        "emails":     [source] if emails     else [],
        "phones":     [source] if phones     else [],
        "skills":     [source] if skills     else [],
        "education":  [source] if education  else [],
        "experience": [source] if experience else [],
        "location":   [source] if location   else [],
        "links":      [source] if links      else [],
        "github_profile": [],
    }

    # --- Confidence: based on how many distinct sources provided the field ---
    candidate.confidence = {
        "full_name":      1.0 if full_name  else 0.0,
        "emails":         1.0 if emails     else 0.0,
        "phones":         1.0 if phones     else 0.0,
        "skills":         0.9 if skills     else 0.0,
        "education":      0.9 if education  else 0.0,
        "experience":     0.9 if experience else 0.0,
        "location":       0.8 if location   else 0.0,
        "links":          1.0 if links      else 0.0,
        "github_profile": 0.0,
    }

    # --- Field source: the single primary source for each field value ---
    candidate.field_source = {
        "full_name":      source if full_name  else None,
        "emails":         source if emails     else None,
        "phones":         source if phones     else None,
        "skills":         source if skills     else None,
        "education":      source if education  else None,
        "experience":     source if experience else None,
        "location":       source if location   else None,
        "links":          source if links      else None,
        "github_profile": None,
    }

    return candidate
