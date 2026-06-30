# Candidate Data Transformer

A modular data engineering pipeline that consolidates candidate information from multiple heterogeneous sources — Recruiter CSV, ATS JSON, Resume PDFs, and GitHub profiles — into a single normalized, deduplicated, and configurable JSON output with full provenance and confidence tracking.

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Running the Project](#running-the-project)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Output Configuration](#output-configuration)
- [GitHub Enrichment](#github-enrichment)
- [Provenance and Confidence](#provenance-and-confidence)
- [Running Tests](#running-tests)

---

## Overview

Recruiters often receive candidate data from multiple disconnected systems — spreadsheets, ATS platforms, resume uploads, and external profiles. This project solves that by automatically:

- Parsing candidate data from CSV, JSON, and PDF sources
- Normalizing emails, phone numbers, locations, and skills
- Detecting and merging duplicate candidate records
- Tracking which source provided each field (provenance)
- Scoring confidence per field based on how many sources agree
- Optionally enriching profiles with live GitHub data
- Generating a clean, configurable JSON output

---

## Pipeline Architecture

```
Input Sources
  CSV (Recruiter)  ·  ATS JSON  ·  Resume PDFs  ·  GitHub API
          │
          ▼
     Data Parsing
  csv_parser  ·  json_parser  ·  pdf_parser
          │
          ▼
   Canonical Schema  (Pydantic Candidate model)
          │
          ▼
     Normalization
  email  ·  phone  ·  skills  ·  location
          │
          ▼
  Candidate Matching  (email / phone dedup)
          │
          ▼
    Merge Engine  (source-priority conflict resolution)
          │
          ▼
  GitHub Enrichment  (optional, auto-matched)
          │
          ▼
  Runtime Output Projection  (output_config.json)
          │
          ▼
  Output JSON  (value + source + provenance + confidence per field)
```

---

## Project Structure

```
candidate-transformer/
│
├── config/
│   └── output_config.json        # Controls which fields appear in output
│
├── inputs/
│   ├── Recruiter.csv             # Recruiter spreadsheet
│   ├── ats.json                  # ATS platform export
│   └── resumes/                  # Resume PDFs (one per candidate)
│
├── github/
│   ├── github_client.py          # GitHub REST API integration
│   └── github_enricher.py        # Enriches candidate with GitHub data
│
├── merger/
│   ├── matcher.py                # Duplicate detection (email / phone)
│   ├── merge.py                  # Merge engine with provenance tracking
│   └── rules.py                  # Source priority rules
│
├── models/
│   └── canonical_schema.py       # Pydantic Candidate schema
│
├── normalizers/
│   ├── email.py                  # Email normalization
│   ├── phone.py                  # Phone normalization (+91 format)
│   ├── skills.py                 # Skill alias canonicalization
│   └── normalize_candidate.py    # Orchestrates all normalizers
│
├── output/
│   └── candidate_output.json     # Final generated output
│
├── parsers/
│   ├── csv_parser.py             # Reads Recruiter CSV
│   ├── json_parser.py            # Reads ATS JSON
│   └── pdf_parser.py             # Extracts data from Resume PDFs
│
├── projector/
│   └── projector.py              # Maps canonical fields to output shape
│
├── tests/                        # Pytest test suite
│
├── utils/
│   ├── candidate_builder.py      # Factory for Candidate objects
│   ├── confidence.py             # Confidence score calculator
│   └── output_writer.py          # Writes final JSON to disk
│
├── app.py                        # Streamlit web UI
├── main.py                       # CLI entry point
└── requirements.txt
```

---

## Tech Stack

| Library | Purpose |
|---|---|
| Python 3.9+ | Core language |
| Pandas | CSV parsing |
| pdfplumber | PDF text and hyperlink extraction |
| Pydantic | Canonical candidate schema and validation |
| Requests | GitHub REST API calls |
| Phonenumbers | Phone number normalization |
| Streamlit | Web UI |
| Pytest | Test suite |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/candidate-transformer.git
cd candidate-transformer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

macOS / Linux:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Option A — Command Line (CLI)

```bash
python main.py
```

The CLI will:
1. Load `inputs/Recruiter.csv`, `inputs/ats.json`, and all PDFs in `inputs/resumes/`
2. Normalize and merge all candidates
3. Prompt you to optionally select a candidate for GitHub enrichment
4. Write the output to `output/candidate_output.json`

### Option B — Streamlit Web UI

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

The UI lets you:
- Upload a Recruiter CSV, ATS JSON, and multiple Resume PDFs
- Paste multiple GitHub profile URLs (one per line) for auto-matched enrichment
- Download the generated `candidate_output.json`

---

## Input Format

### Recruiter CSV (`inputs/Recruiter.csv`)

Expected columns:

| Column | Description |
|---|---|
| `name` | Candidate full name |
| `email` | Email address |
| `phone` | Phone number |
| `skills` | Comma-separated skill list |
| `location` | City / region |

### ATS JSON (`inputs/ats.json`)

Expected structure per record:

```json
{
  "firstName": "Jane",
  "lastName": "Doe",
  "primaryEmail": "jane@example.com",
  "mobile": "9876543210",
  "skills": ["Python", "SQL"],
  "location": "Chennai",
  "links": {
    "github": "https://github.com/janedoe"
  }
}
```

### Resume PDFs (`inputs/resumes/`)

Standard resume PDFs. The parser extracts:
- Name (first line of the document)
- Emails and phone numbers via regex
- Sections: Skills, Education, Experience, Projects, Certifications
- Hyperlinks (GitHub, LinkedIn, LeetCode, HackerRank, portfolio)

---

## Output Format

Output is written to `output/candidate_output.json`. With provenance and confidence enabled (default), each field looks like:

```json
{
  "candidate_name": {
    "value": "Harshini S",
    "source": "Resume PDF",
    "provenance": ["Resume PDF", "Recruiter CSV"],
    "confidence": 0.9
  },
  "primary_email": {
    "value": "harshisvc@gmail.com",
    "source": "Resume PDF",
    "provenance": ["Resume PDF", "Recruiter CSV"],
    "confidence": 0.9
  },
  "skills": {
    "value": ["Python", "Machine Learning", "TensorFlow"],
    "source": "Resume PDF",
    "provenance": ["Resume PDF", "Recruiter CSV"],
    "confidence": 0.9
  },
  "education": {
    "value": [
      {
        "institution": "KPR Institute of Engineering and Technology",
        "degree": "B.E.",
        "field": "Computer Science and Engineering (AI & ML)",
        "end_year": 2027
      }
    ],
    "source": "Resume PDF",
    "provenance": ["Resume PDF"],
    "confidence": 0.7
  }
}
```

---

## Output Configuration

`config/output_config.json` controls the output shape at runtime — no code changes needed.

```json
{
  "include_provenance": true,
  "include_confidence": true,
  "fields": [
    { "path": "candidate_name", "from": "full_name",    "provenance_key": "full_name" },
    { "path": "primary_email",  "from": "emails[0]",    "provenance_key": "emails" },
    { "path": "primary_phone",  "from": "phones[0]",    "provenance_key": "phones" },
    { "path": "skills",         "from": "skills",       "provenance_key": "skills" },
    { "path": "location",       "from": "location",     "provenance_key": "location" }
  ]
}
```

| Key | Type | Description |
|---|---|---|
| `include_provenance` | bool | Wrap each field with `source` and `provenance` list |
| `include_confidence` | bool | Wrap each field with a `confidence` score |
| `path` | string | Output key name in the JSON |
| `from` | string | Dot-notation path into the Candidate object (supports indexing e.g. `emails[0]`) |
| `provenance_key` | string | Which canonical field to pull provenance/confidence metadata from |

Set `"include_provenance": false` and `"include_confidence": false` to get flat values with no annotation.

---

## GitHub Enrichment

GitHub enrichment is optional and fetches live profile data from the GitHub REST API.

### CLI

After merging, the CLI lists all candidates and prompts:

```
Available Candidates
1. Harshini S
2. DHANYASRI K
3. BHARANI R

Select Candidate Number (or Press Enter to Skip): 2
Enter GitHub Profile URL (Press Enter to Skip): https://github.com/dhanyasri612
```

### Streamlit UI

In Section 2, paste one GitHub URL per line — one for each candidate you want to enrich:

```
https://github.com/harshinis
https://github.com/dhanyasri612
https://github.com/bharani-10
```

URLs are automatically matched to candidates using three strategies in order:
1. **Resume link match** — if the URL matches a GitHub link already extracted from the resume
2. **GitHub API name match** — GitHub's `name` field is compared against the candidate's full name
3. **Positional fallback** — first unmatched URL is assigned to the first unmatched candidate

Enriched fields added to output: `github_username`, `github_name`, `github_followers`, `github_public_repos`, `github_company`, `github_location`, `github_profile_url`.

---

## Provenance and Confidence

Every field in the output tracks where its value came from.

### Source Priority

When two sources provide conflicting values for the same field, the higher-priority source wins:

| Source | Priority |
|---|---|
| GitHub API | 4 (highest) |
| Resume PDF | 3 |
| ATS JSON | 2 |
| Recruiter CSV | 1 (lowest) |

### Confidence Scoring

Confidence is based on how many distinct sources contributed to a field:

| Sources | Confidence |
|---|---|
| 3 or more | 1.0 |
| 2 | 0.9 |
| 1 | 0.7 |
| 0 | 0.0 |

### Provenance Fields

Each `Candidate` object carries three tracking dicts:

| Field | Type | Description |
|---|---|---|
| `provenance` | `Dict[str, List[str]]` | All sources that contributed to each field |
| `confidence` | `Dict[str, float]` | Confidence score per field |
| `field_source` | `Dict[str, str]` | The single winning source for the current field value |

---

## Running Tests

```bash
pytest tests/
```

To run a specific test file:

```bash
pytest tests/test_merger.py -v
```
