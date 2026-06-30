SOURCE_PRIORITY = {
    "Resume PDF":   3,
    "ATS JSON":     2,
    "Recruiter CSV": 1,
    "GitHub API":   4,   # GitHub data is directly from the candidate's live profile
}


def choose_value(current_value, current_source, new_value, new_source):
    """
    Choose the better value based on source priority.
    """

    if not new_value:
        return current_value, current_source

    if not current_value:
        return new_value, new_source

    if SOURCE_PRIORITY[new_source] > SOURCE_PRIORITY[current_source]:
        return new_value, new_source

    return current_value, current_source