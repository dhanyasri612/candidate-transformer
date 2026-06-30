import json
from models.canonical_schema import Candidate


def parse_json(json_path: str):
    """
    Read ats.json and convert each candidate into a Candidate object.
    """

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    candidates = []

    for person in data:

        candidate = Candidate(
            full_name=f"{person['firstName']} {person['lastName']}",
            emails=[person["primaryEmail"]],
            phones=[person["mobile"]],
            skills=person.get("skills", []),
            location=person.get("location"),
            links=person.get("links") or {},
            source="ATS JSON"
        )

        candidates.append(candidate)

    return candidates