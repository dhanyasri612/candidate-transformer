from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json

from merger.matcher import is_same_candidate

csv_candidates = parse_csv("inputs/recruiter.csv")
json_candidates = parse_json("inputs/ats.json")

for csv_candidate in csv_candidates:
    for json_candidate in json_candidates:

        if is_same_candidate(csv_candidate, json_candidate):
            print(
                f"MATCH: {csv_candidate.full_name} <--> {json_candidate.full_name}"
            )