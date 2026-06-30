from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json
from parsers.pdf_parser import parse_pdf

from merger.merge import merge_candidate_list


def main():

    csv_candidates = parse_csv("inputs/recruiter.csv")

    json_candidates = parse_json("inputs/ats.json")

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

    merged = merge_candidate_list(all_candidates)

    print("=" * 60)

    print(f"CSV Candidates   : {len(csv_candidates)}")
    print(f"JSON Candidates  : {len(json_candidates)}")
    print(f"PDF Candidates   : {len(pdf_candidates)}")
    print(f"Merged Candidates: {len(merged)}")

    print("=" * 60)

    for candidate in merged:
        print(candidate)
        print("-" * 60)


if __name__ == "__main__":
    main()