import json
import os


def write_output(candidates, output_file):
    """
    Write projected candidates to a JSON file.
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)

    print(f"Output written to {output_file}")