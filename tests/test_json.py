from parsers.json_parser import parse_json

candidates = parse_json("inputs/ats.json")

for candidate in candidates:
    print(candidate)