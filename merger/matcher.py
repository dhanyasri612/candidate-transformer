from normalizers.email import normalize_email
from normalizers.phone import normalize_phone


def is_same_candidate(candidate1, candidate2):
    """
    Check whether two Candidate objects represent the same person.
    """

    # Match by email
    if candidate1.emails and candidate2.emails:
        email1 = normalize_email(candidate1.emails[0])
        email2 = normalize_email(candidate2.emails[0])

        if email1 == email2:
            return True

    # Match by phone
    if candidate1.phones and candidate2.phones:
        phone1 = normalize_phone(candidate1.phones[0])
        phone2 = normalize_phone(candidate2.phones[0])

        if phone1 == phone2:
            return True

    return False