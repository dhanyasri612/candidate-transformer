from github.github_client import get_github_profile


def enrich_candidate_with_github(candidate, github_url):
    """
    Fetch GitHub profile info and enrich the candidate's github_profile field.
    Also updates field_source, provenance, and confidence for the github_profile field.
    """
    profile_data = get_github_profile(github_url)

    if not profile_data:
        candidate.github_profile = {}
        return candidate

    candidate.github_profile = {
        "username":    profile_data.get("login"),
        "name":        profile_data.get("name"),
        "bio":         profile_data.get("bio"),
        "company":     profile_data.get("company"),
        "location":    profile_data.get("location"),
        "public_repos": profile_data.get("public_repos"),
        "followers":   profile_data.get("followers"),
        "following":   profile_data.get("following"),
        "profile_url": profile_data.get("html_url"),
        "avatar_url":  profile_data.get("avatar_url"),
    }

    # Track provenance, confidence, and source for the github_profile field
    candidate.provenance["github_profile"] = ["GitHub API"]
    candidate.confidence["github_profile"] = 1.0
    candidate.field_source["github_profile"] = "GitHub API"

    print(f"GitHub enrichment applied to candidate: {candidate.full_name}")
    return candidate
