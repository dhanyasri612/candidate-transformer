import pandas as pd

from utils.candidate_builder import build_candidate


def parse_csv(csv_path: str):
    """
    Read recruiter.csv and convert each row into a Candidate object.
    """

    df = pd.read_csv(csv_path)

    candidates = []

    for _, row in df.iterrows():

        skills = []

        if pd.notna(row.get("skills")):
            skills = [skill.strip() for skill in row["skills"].split(",")]

        candidate = build_candidate(
            full_name=row.get("name"),
            emails=[row.get("email")] if pd.notna(row.get("email")) else [],
            phones=[str(row.get("phone"))] if pd.notna(row.get("phone")) else [],
            skills=skills,
            location=row.get("location"),
            source="Recruiter CSV"
        )

        candidates.append(candidate)

    return candidates