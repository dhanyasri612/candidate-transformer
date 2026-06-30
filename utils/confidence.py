def calculate_confidence(provenance):
    """
    Simple confidence based on number of sources.
    """

    count = len(set(provenance))

    if count >= 3:
        return 1.0

    if count == 2:
        return 0.9

    return 0.7