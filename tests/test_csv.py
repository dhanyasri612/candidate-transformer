from parsers.csv_parser import parse_csv

candidates = parse_csv("inputs/Recruiter.csv")

for candidate in candidates:
    print(candidate)