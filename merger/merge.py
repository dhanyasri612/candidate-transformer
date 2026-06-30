from merger.matcher import is_same_candidate
from merger.rules import choose_value
from utils.confidence import calculate_confidence


def _merge_provenance(existing_prov, candidate_prov, field):
    """Merge provenance lists for a field, deduplicating sources."""
    return list(set(
        existing_prov.get(field, []) + candidate_prov.get(field, [])
    ))


def merge_candidate_list(candidates):

    merged = []

    for candidate in candidates:

        found = False

        for existing in merged:

            if is_same_candidate(existing, candidate):

                found = True

                # ── Full Name ──────────────────────────────────────────
                chosen_name, chosen_source = choose_value(
                    existing.full_name, existing.field_source.get("full_name") or existing.source,
                    candidate.full_name, candidate.field_source.get("full_name") or candidate.source,
                )
                existing.full_name = chosen_name
                existing.field_source["full_name"] = chosen_source
                existing.provenance["full_name"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "full_name"
                )
                existing.confidence["full_name"] = calculate_confidence(
                    existing.provenance["full_name"]
                )

                # ── Emails ─────────────────────────────────────────────
                existing.emails = list(set(existing.emails + candidate.emails))
                existing.provenance["emails"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "emails"
                )
                existing.confidence["emails"] = calculate_confidence(
                    existing.provenance["emails"]
                )
                # Primary source = highest-priority source in provenance
                existing.field_source["emails"] = _primary_source(existing.provenance["emails"])

                # ── Phones ─────────────────────────────────────────────
                existing.phones = list(set(existing.phones + candidate.phones))
                existing.provenance["phones"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "phones"
                )
                existing.confidence["phones"] = calculate_confidence(
                    existing.provenance["phones"]
                )
                existing.field_source["phones"] = _primary_source(existing.provenance["phones"])

                # ── Skills ─────────────────────────────────────────────
                existing.skills = list(set(existing.skills + candidate.skills))
                existing.provenance["skills"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "skills"
                )
                existing.confidence["skills"] = calculate_confidence(
                    existing.provenance["skills"]
                )
                existing.field_source["skills"] = _primary_source(existing.provenance["skills"])

                # ── Location ───────────────────────────────────────────
                chosen_loc, chosen_loc_src = choose_value(
                    existing.location, existing.field_source.get("location") or existing.source,
                    candidate.location, candidate.field_source.get("location") or candidate.source,
                )
                existing.location = chosen_loc
                existing.field_source["location"] = chosen_loc_src
                existing.provenance["location"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "location"
                )
                existing.confidence["location"] = calculate_confidence(
                    existing.provenance["location"]
                )

                # ── GitHub Profile ─────────────────────────────────────
                if candidate.github_profile and not existing.github_profile:
                    existing.github_profile = candidate.github_profile
                    existing.field_source["github_profile"] = "GitHub API"
                    existing.provenance["github_profile"] = ["GitHub API"]
                    existing.confidence["github_profile"] = 1.0
                elif candidate.github_profile and existing.github_profile:
                    chosen_gh, chosen_gh_src = choose_value(
                        existing.github_profile,
                        existing.field_source.get("github_profile") or existing.source,
                        candidate.github_profile,
                        candidate.field_source.get("github_profile") or candidate.source,
                    )
                    existing.github_profile = chosen_gh
                    existing.field_source["github_profile"] = chosen_gh_src

                # ── Links ──────────────────────────────────────────────
                for key, val in candidate.links.items():
                    if val:
                        if key not in existing.links:
                            existing.links[key] = val
                        else:
                            chosen_val, _ = choose_value(
                                existing.links[key],
                                existing.field_source.get("links") or existing.source,
                                val,
                                candidate.field_source.get("links") or candidate.source,
                            )
                            existing.links[key] = chosen_val

                existing.provenance["links"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "links"
                )
                existing.confidence["links"] = calculate_confidence(
                    existing.provenance["links"]
                )
                existing.field_source["links"] = _primary_source(existing.provenance["links"])

                # ── Education ──────────────────────────────────────────
                for edu in candidate.education:
                    dup = False
                    for ex_edu in existing.education:
                        if (edu.get("degree") and ex_edu.get("degree") and
                                edu["degree"].lower() == ex_edu["degree"].lower()):
                            dup = True
                            for f in ["institution", "field", "end_year"]:
                                ex_val = ex_edu.get(f)
                                new_val = edu.get(f)
                                if new_val and not ex_val:
                                    ex_edu[f] = new_val
                                elif new_val and ex_val:
                                    chosen_val, _ = choose_value(
                                        ex_val,
                                        existing.field_source.get("education") or existing.source,
                                        new_val,
                                        candidate.field_source.get("education") or candidate.source,
                                    )
                                    ex_edu[f] = chosen_val
                            break
                    if not dup:
                        existing.education.append(edu)

                existing.provenance["education"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "education"
                )
                existing.confidence["education"] = calculate_confidence(
                    existing.provenance["education"]
                )
                existing.field_source["education"] = _primary_source(existing.provenance["education"])

                # ── Experience ─────────────────────────────────────────
                for exp in candidate.experience:
                    dup = False
                    for ex_exp in existing.experience:
                        comp1 = exp.get("company", "").lower().replace(" ", "")
                        comp2 = ex_exp.get("company", "").lower().replace(" ", "")
                        if comp1 and comp2 and (comp1 in comp2 or comp2 in comp1):
                            dup = True
                            for f in ["title", "start", "end", "summary"]:
                                ex_val = ex_exp.get(f)
                                new_val = exp.get(f)
                                if new_val and not ex_val:
                                    ex_exp[f] = new_val
                                elif new_val and ex_val:
                                    chosen_val, _ = choose_value(
                                        ex_val,
                                        existing.field_source.get("experience") or existing.source,
                                        new_val,
                                        candidate.field_source.get("experience") or candidate.source,
                                    )
                                    ex_exp[f] = chosen_val
                            break
                    if not dup:
                        existing.experience.append(exp)

                existing.provenance["experience"] = _merge_provenance(
                    existing.provenance, candidate.provenance, "experience"
                )
                existing.confidence["experience"] = calculate_confidence(
                    existing.provenance["experience"]
                )
                existing.field_source["experience"] = _primary_source(existing.provenance["experience"])

                break

        if not found:
            merged.append(candidate)

    return merged


def _primary_source(provenance_list):
    """
    Return the highest-priority source from a provenance list.
    Priority: Resume PDF > ATS JSON > Recruiter CSV > GitHub API
    """
    from merger.rules import SOURCE_PRIORITY
    if not provenance_list:
        return None
    return max(set(provenance_list), key=lambda s: SOURCE_PRIORITY.get(s, 0))


def merge_candidates(list1, list2):
    """Compatibility wrapper to merge two lists of candidates."""
    return merge_candidate_list(list1 + list2)
