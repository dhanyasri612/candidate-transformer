from parsers.csv_parser import parse_csv
from parsers.json_parser import parse_json

from merger.merge import merge_candidates

csv_candidates = parse_csv("inputs/recruiter.csv")

json_candidates = parse_json("inputs/ats.json")

merged = merge_candidates(csv_candidates, json_candidates)

for candidate in merged:
    print(candidate)