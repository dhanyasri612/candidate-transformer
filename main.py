from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json
from parsers.pdf_parser import parse_pdf

from merger.merge import merge_candidate_list

from projector.projector import project_candidate
from utils.output_writer import write_output
from normalizers.normalize_candidate import normalize_candidate


def main():

    print("Loading Recruiter CSV...")
    csv_candidates = parse_csv("inputs/recruiter.csv")

    print("Loading ATS JSON...")
    json_candidates = parse_json("inputs/ats.json")

    print("Reading Resume PDFs...")
    pdf_candidates = [
        parse_pdf("inputs/resumes/Harshini S - AIML.pdf"),
        parse_pdf("inputs/resumes/Dhanyasri.K_23AM018 (1).pdf"),
        parse_pdf("inputs/resumes/AI_Engineer_23AM011.pdf")
    ]

    all_candidates = (
        csv_candidates +
        json_candidates +
        pdf_candidates
    )

    print("Normalizing candidates...")
    normalized_candidates = []

    for candidate in all_candidates:
        normalized_candidates.append(
            normalize_candidate(candidate)
        )

    print("Merging duplicate candidates...")
    merged_candidates = merge_candidate_list(
        normalized_candidates
    )

    # GitHub Enrichment Step (After Merging)
    try:
        print("\nAvailable Candidates")
        for idx, candidate in enumerate(merged_candidates):
            print(f"{idx + 1}. {candidate.full_name}")
        
        selection = input("\nSelect Candidate Number (or Press Enter to Skip): ").strip()
        if selection:
            try:
                sel_idx = int(selection) - 1
                if 0 <= sel_idx < len(merged_candidates):
                    target_candidate = merged_candidates[sel_idx]
                    
                    github_url = input("Enter GitHub Profile URL (Press Enter to Skip): ").strip()
                    if github_url:
                        from github.github_enricher import enrich_candidate_with_github
                        enrich_candidate_with_github(target_candidate, github_url)
                else:
                    print("Invalid candidate number. Skipping GitHub enrichment.")
            except ValueError:
                print("Invalid input. Skipping GitHub enrichment.")
    except Exception as e:
        print(f"Error during GitHub enrichment: {e}")

    print("Generating output JSON...")
    projected = []

    for candidate in merged_candidates:
        projected.append(
            project_candidate(
                candidate,
                "config/output_config.json"
            )
        )

    write_output(
        projected,
        "output/candidate_output.json"
    )

    print("Project completed successfully!")


if __name__ == "__main__":
    main()