import streamlit as st
import os
import re
import json
import shutil

from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json
from parsers.pdf_parser import parse_pdf
from normalizers.normalize_candidate import normalize_candidate
from merger.merge import merge_candidate_list
from github.github_enricher import enrich_candidate_with_github
from github.github_client import get_github_profile
from projector.projector import project_candidate
from utils.output_writer import write_output

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


# ----------------------------------------------------
# GITHUB MATCHING HELPERS
# ----------------------------------------------------

def extract_github_username(url: str):
    """Extract GitHub username from a URL or bare username string."""
    url = url.strip()
    if not url:
        return None
    if "/" not in url and "." not in url:
        return url.lower()
    match = re.search(r'github\.com/([a-zA-Z0-9_\-]+)', url, re.IGNORECASE)
    return match.group(1).lower() if match else None


def match_github_urls_to_candidates(github_urls, merged_candidates):
    """
    Match each GitHub URL to the best candidate using three strategies:
    1. Candidate already has a matching github link extracted from their PDF/resume.
    2. GitHub API name field matches the candidate's full_name (case-insensitive).
    3. Fallback: assign to the next unmatched candidate in order.

    Returns a list of (candidate, url, match_strategy) tuples.
    """
    assignments = []
    unmatched_urls = list(github_urls)
    unmatched_candidates = list(merged_candidates)

    # --- Strategy 1: link already in candidate's parsed links ---
    still_unmatched_urls = []
    for url in unmatched_urls:
        username = extract_github_username(url)
        matched = False
        for cand in unmatched_candidates:
            existing_github = cand.links.get("github", "")
            existing_username = extract_github_username(existing_github) if existing_github else None
            if username and existing_username and username == existing_username:
                assignments.append((cand, url, "resume link match"))
                unmatched_candidates.remove(cand)
                matched = True
                break
        if not matched:
            still_unmatched_urls.append(url)

    unmatched_urls = still_unmatched_urls

    # --- Strategy 2: GitHub API name matches candidate full_name ---
    still_unmatched_urls = []
    for url in unmatched_urls:
        profile_data = get_github_profile(url)
        if not profile_data:
            still_unmatched_urls.append((url, None))
            continue
        api_name = (profile_data.get("name") or "").strip().lower()
        matched = False
        for cand in unmatched_candidates:
            cand_name = (cand.full_name or "").strip().lower()
            if api_name and cand_name and api_name == cand_name:
                assignments.append((cand, url, f"GitHub name match ({profile_data.get('name')})"))
                unmatched_candidates.remove(cand)
                matched = True
                break
        if not matched:
            still_unmatched_urls.append((url, profile_data))

    # --- Strategy 3: Positional fallback for remaining unmatched ---
    for (url, profile_data), cand in zip(still_unmatched_urls, unmatched_candidates):
        assignments.append((cand, url, "positional fallback"))

    return assignments


# ----------------------------------------------------
# UI LAYOUT
# ----------------------------------------------------

st.title("Candidate Data Transformer")
st.write("Transform candidate information from multiple heterogeneous sources into a unified canonical profile.")

# Section 1: Input Files
st.header("1. Input Files")

col1, col2 = st.columns(2)
with col1:
    uploaded_csv = st.file_uploader("Recruiter CSV", type=["csv"])
    uploaded_json = st.file_uploader("ATS JSON", type=["json"])
with col2:
    uploaded_pdfs = st.file_uploader("Resume PDFs", type=["pdf"], accept_multiple_files=True)
    uploaded_config = st.file_uploader("Output Config JSON", type=["json"])

# Section 2: Optional GitHub Enrichment
st.header("2. Optional GitHub Enrichment")
st.write(
    "Paste one GitHub profile URL per line — one for each candidate you want to enrich. "
    "URLs are automatically matched to candidates using resume links or GitHub name. "
    "If no match is found, they are assigned in order."
)
github_urls_input = st.text_area(
    "GitHub Profile URLs (one per line)",
    placeholder="https://github.com/dhanyasrik612\nhttps://github.com/harshinis\nhttps://github.com/someone",
    height=120,
)

# Section 3: Transform Candidates Button
st.header("3. Transform")
transform_clicked = st.button("Transform Candidates")

if transform_clicked:
    if not uploaded_csv and not uploaded_json and not uploaded_pdfs:
        st.error("Please upload at least one candidate source file (CSV, JSON, or PDF).")
    else:
        # 1. Save uploaded files temporarily
        csv_path = None
        if uploaded_csv:
            csv_path = os.path.join(TEMP_DIR, uploaded_csv.name)
            with open(csv_path, "wb") as f:
                f.write(uploaded_csv.getbuffer())

        json_path = None
        if uploaded_json:
            json_path = os.path.join(TEMP_DIR, uploaded_json.name)
            with open(json_path, "wb") as f:
                f.write(uploaded_json.getbuffer())

        pdf_paths = []
        if uploaded_pdfs:
            for pdf_file in uploaded_pdfs:
                pdf_path = os.path.join(TEMP_DIR, pdf_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                pdf_paths.append(pdf_path)

        config_path = "config/output_config.json"
        if uploaded_config:
            config_path = os.path.join(TEMP_DIR, uploaded_config.name)
            with open(config_path, "wb") as f:
                f.write(uploaded_config.getbuffer())

        # 2. Execute existing backend pipeline
        try:
            csv_candidates = []
            if csv_path:
                csv_candidates = parse_csv(csv_path)

            json_candidates = []
            if json_path:
                json_candidates = parse_json(json_path)

            pdf_candidates = []
            if pdf_paths:
                for path in pdf_paths:
                    pdf_candidates.append(parse_pdf(path))

            total_parsed = len(csv_candidates) + len(json_candidates) + len(pdf_candidates)

            # Normalize
            all_candidates = csv_candidates + json_candidates + pdf_candidates
            normalized = [normalize_candidate(c) for c in all_candidates]

            # Merge
            merged = merge_candidate_list(normalized)

            # 3. GitHub Enrichment — multi-URL, auto-matched
            github_urls = [
                url.strip()
                for url in github_urls_input.splitlines()
                if url.strip()
            ]

            enrichment_log = []
            if github_urls:
                with st.spinner("Matching and fetching GitHub profiles..."):
                    assignments = match_github_urls_to_candidates(github_urls, merged)
                    for cand, url, strategy in assignments:
                        try:
                            enrich_candidate_with_github(cand, url)
                            enrichment_log.append(
                                (cand.full_name, url, strategy, "success")
                            )
                        except Exception as e:
                            enrichment_log.append(
                                (cand.full_name, url, strategy, f"failed: {e}")
                            )

            # 4. Save merged candidates to session state
            st.session_state.merged_candidates = merged

            # 5. Runtime Output Projection
            projected = [project_candidate(c, config_path) for c in merged]

            # 6. Write output JSON
            write_output(projected, "output/candidate_output.json")

            # ----------------------------------------------------
            # RESULTS
            # ----------------------------------------------------
            st.subheader("Transformation Results")
            st.write(f"**Parsed Candidates:** {total_parsed}")
            st.write(f"**Merged Candidates:** {len(merged)}")
            st.success("Candidates transformed and merged successfully!")

            # GitHub enrichment summary
            if enrichment_log:
                st.write("#### GitHub Enrichment Summary")
                for name, url, strategy, status in enrichment_log:
                    icon = "✅" if status == "success" else "⚠️"
                    st.write(f"{icon} **{name}** ← `{url}`  \n&nbsp;&nbsp;&nbsp;&nbsp;Match: *{strategy}* | Status: *{status}*")

            # Merged candidate cards
            st.write("### Merged Candidate Profiles")
            for c in merged:
                with st.expander(f"👤 {c.full_name or 'Unknown'}", expanded=True):

                    def field_meta(field_key):
                        """Return a formatted provenance/confidence badge string."""
                        src   = c.field_source.get(field_key)
                        prov  = c.provenance.get(field_key, [])
                        conf  = c.confidence.get(field_key, 0.0)
                        parts = []
                        if src:
                            parts.append(f"source: **{src}**")
                        if prov:
                            parts.append(f"provenance: {', '.join(prov)}")
                        parts.append(f"confidence: **{round(conf * 100)}%**")
                        return " | ".join(parts)

                    st.write(f"**Name:** {c.full_name or 'None'}")
                    st.caption(field_meta("full_name"))

                    st.write(f"**Email:** {', '.join(c.emails) if c.emails else 'None'}")
                    st.caption(field_meta("emails"))

                    st.write(f"**Phone:** {', '.join(c.phones) if c.phones else 'None'}")
                    st.caption(field_meta("phones"))

                    st.write(f"**Location:** {c.location if c.location else 'None'}")
                    st.caption(field_meta("location"))

                    st.write(f"**Skills ({len(c.skills)}):** {', '.join(c.skills) if c.skills else 'None'}")
                    st.caption(field_meta("skills"))

                    if c.education:
                        st.write("**Education:**")
                        for edu in c.education:
                            st.write(
                                f"  - {edu.get('degree', '')} in {edu.get('field', 'N/A')} "
                                f"@ {edu.get('institution', 'Unknown')} ({edu.get('end_year', '')})"
                            )
                        st.caption(field_meta("education"))

                    if c.experience:
                        st.write("**Experience:**")
                        for exp in c.experience:
                            st.write(
                                f"  - {exp.get('title', '')} @ {exp.get('company', '')} "
                                f"({exp.get('start', '')} – {exp.get('end', '')})"
                            )
                        st.caption(field_meta("experience"))

                    if c.github_profile:
                        gh = c.github_profile
                        st.write(
                            f"**GitHub:** [{gh.get('username')}]({gh.get('profile_url')}) "
                            f"— {gh.get('public_repos', 0)} repos, {gh.get('followers', 0)} followers"
                        )
                        st.caption(field_meta("github_profile"))

                    st.markdown("---")

            # Download output
            with open("output/candidate_output.json", "r", encoding="utf-8") as f:
                output_data = f.read()

            st.download_button(
                label="Download candidate_output.json",
                data=output_data,
                file_name="candidate_output.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"Transformation failed: {e}")

        finally:
            # Clean up temp files
            if os.path.exists(TEMP_DIR):
                shutil.rmtree(TEMP_DIR)
                os.makedirs(TEMP_DIR, exist_ok=True)
