from parsers.pdf_parser import parse_pdf
from parsers.json_parser import parse_json
from merger.merge import merge_candidate_list
from projector.projector import get_value, project_candidate
from models.canonical_schema import Candidate
import os
import json

def test_link_extraction():
    print("Testing PDF link extraction...")
    # Parse a resume PDF
    candidate = parse_pdf("inputs/resumes/AI_Engineer_23AM011.pdf")
    assert "github" in candidate.links, "GitHub link should be extracted"
    assert "linkedin" in candidate.links, "LinkedIn link should be extracted"
    print("PDF link extraction: SUCCESS")
    print(f"Extracted links: {candidate.links}")

def test_link_merging():
    print("Testing link merging...")
    # Source 1 (CSV, priority 1)
    c1 = Candidate(
        full_name="John Doe",
        emails=["john@example.com"],
        links={},
        source="Recruiter CSV"
    )
    # Source 2 (ATS, priority 2)
    c2 = Candidate(
        full_name="John Doe",
        emails=["john@example.com"],
        links={"github": "https://github.com/john-ats"},
        source="ATS JSON"
    )
    # Source 3 (PDF, priority 3)
    c3 = Candidate(
        full_name="John Doe",
        emails=["john@example.com"],
        links={"linkedin": "https://linkedin.com/in/john-pdf", "github": "https://github.com/john-pdf"},
        source="Resume PDF"
    )
    
    # Merge them
    # Ensure they match (same email)
    c1.provenance = {"emails": ["Recruiter CSV"]}
    c2.provenance = {"emails": ["ATS JSON"]}
    c3.provenance = {"emails": ["Resume PDF"]}
    
    c1.confidence = {"emails": 1.0}
    c2.confidence = {"emails": 1.0}
    c3.confidence = {"emails": 1.0}
    
    merged = merge_candidate_list([c1, c2, c3])
    assert len(merged) == 1, "Should merge into 1 candidate"
    
    merged_candidate = merged[0]
    # github should be from Resume PDF because it has higher priority than ATS JSON
    assert merged_candidate.links.get("github") == "https://github.com/john-pdf", "Should keep higher priority link"
    assert merged_candidate.links.get("linkedin") == "https://linkedin.com/in/john-pdf", "Should preserve linkedin link"
    print("Link merging: SUCCESS")
    print(f"Merged links: {merged_candidate.links}")

def test_configurable_output():
    print("Testing configurable output of links...")
    candidate = Candidate(
        full_name="John Doe",
        links={"github": "https://github.com/john", "linkedin": "https://linkedin.com/in/john"}
    )
    
    # Verify get_value
    assert get_value(candidate, "links.github") == "https://github.com/john"
    assert get_value(candidate, "links.linkedin") == "https://linkedin.com/in/john"
    
    # Verify project_candidate with a temp config
    config_data = {
        "fields": [
            {"path": "candidate_name", "from": "full_name"},
            {"path": "github", "from": "links.github"},
            {"path": "linkedin", "from": "links.linkedin"}
        ]
    }
    
    temp_config_path = "config/temp_test_config.json"
    os.makedirs("config", exist_ok=True)
    with open(temp_config_path, "w") as f:
        json.dump(config_data, f)
        
    try:
        projected = project_candidate(candidate, temp_config_path)
        assert projected["candidate_name"] == "John Doe"
        assert projected["github"] == "https://github.com/john"
        assert projected["linkedin"] == "https://linkedin.com/in/john"
        print("Configurable output: SUCCESS")
        print(f"Projected output: {projected}")
    finally:
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

if __name__ == "__main__":
    test_link_extraction()
    print("-" * 40)
    test_link_merging()
    print("-" * 40)
    test_configurable_output()
    print("-" * 40)
    print("All tests passed successfully!")
