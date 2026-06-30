from parsers.csv_parser import parse_csv
from projector.projector import project_candidate

candidate = parse_csv("inputs/recruiter.csv")[0]

result = project_candidate(
    candidate,
    "config/output_config.json"
)

print(result)