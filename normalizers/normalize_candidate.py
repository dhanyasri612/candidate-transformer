from normalizers.email import normalize_email
from normalizers.phone import normalize_phone
from normalizers.skills import normalize_skills


def normalize_candidate(candidate):
    """
    Normalize all fields of a Candidate object.
    """

    # Normalize emails
    candidate.emails = [
        normalize_email(email)
        for email in candidate.emails
    ]

    # Normalize phones
    candidate.phones = list(
        set(
            normalize_phone(phone)
            for phone in candidate.phones
        )
    )

    # Clean and canonicalize skills
    candidate.skills = normalize_skills(candidate.skills)

    # Normalize location
    if candidate.location:
        candidate.location = candidate.location.strip()

    return candidate