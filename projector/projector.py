import json
import re


def get_part_value(obj, part):
    if obj is None:
        return None

    # Match name and optional index, e.g., "emails[0]" or "education[0]"
    match = re.match(r'^([^\[]+)(?:\[(\d+)\])?$', part)
    if not match:
        return None

    name, index = match.groups()

    if isinstance(obj, dict):
        val = obj.get(name)
    else:
        val = getattr(obj, name, None)

    if index is not None and val is not None:
        idx = int(index)
        try:
            if idx < len(val):
                return val[idx]
        except (TypeError, IndexError, KeyError):
            return None
        return None

    return val


def get_value(candidate, expression):
    """
    Get a value from a Candidate using dot-notation + index expressions, e.g.:
      full_name
      emails[0]
      links.github
      github_profile.followers
    """
    if not expression:
        return None

    parts = expression.split(".")
    current = candidate

    for part in parts:
        current = get_part_value(current, part)
        if current is None:
            return None

    return current


def project_candidate(candidate, config_path):
    """
    Project a Candidate into a flat output dict based on output_config.json.

    When include_provenance / include_confidence are true in the config, each
    field is wrapped as:
        {
            "value":      <the field value>,
            "source":     <primary source that provided this value>,
            "provenance": [<all sources that contributed>],
            "confidence": <float 0.0–1.0>
        }
    """

    with open(config_path, "r") as f:
        config = json.load(f)

    include_provenance = config.get("include_provenance", False)
    include_confidence = config.get("include_confidence", False)
    annotate = include_provenance or include_confidence

    output = {}

    for field_cfg in config["fields"]:
        path = field_cfg["path"]
        from_expr = field_cfg["from"]
        provenance_key = field_cfg.get("provenance_key")

        value = get_value(candidate, from_expr)

        if not annotate:
            output[path] = value
            continue

        # Build the annotated wrapper
        annotation = {"value": value}

        if provenance_key:
            prov_list = candidate.provenance.get(provenance_key, [])
            field_src  = candidate.field_source.get(provenance_key)
            conf_score = candidate.confidence.get(provenance_key, 0.0)
        else:
            prov_list  = []
            field_src  = getattr(candidate, "source", None)
            conf_score = 0.0

        if include_provenance:
            annotation["source"]     = field_src
            annotation["provenance"] = prov_list

        if include_confidence:
            annotation["confidence"] = round(conf_score, 2)

        output[path] = annotation

    return output
