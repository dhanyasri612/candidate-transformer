import pdfplumber
import re

from utils.candidate_builder import build_candidate

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d[\d\s-]{8,}\d)"

ALL_HEADERS = {
    "summary": ["summary", "objective", "professional summary", "about me", "profile"],
    "education": ["education", "academic background", "academic details", "academic profile"],
    "skills": ["skills", "technical skills", "technical proficiencies", "skills & technologies", "skills and technologies", "technologies"],
    "experience": ["experience", "internship experience", "internship", "work experience", "employment", "employment history", "experience & projects"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certifications & courses", "courses", "accomplishments", "training"],
    "publications": ["publications", "patents", "research papers"],
    "achievements": ["achievements", "awards", "honors", "extra-curricular activities", "activities"]
}


def detect_header_type(line):
    # Clean the line: remove leading/trailing non-alphanumeric characters except spaces
    cleaned = re.sub(r'^[^a-zA-Z0-9]+', '', line)
    cleaned = re.sub(r'[^a-zA-Z0-9]+$', '', cleaned)
    cleaned = cleaned.strip().lower()
    
    # Also try removing all spaces
    cleaned_no_spaces = cleaned.replace(" ", "")
    
    for header_type, keywords in ALL_HEADERS.items():
        for kw in keywords:
            kw_clean = kw.lower()
            kw_no_spaces = kw_clean.replace(" ", "")
            if cleaned == kw_clean or cleaned_no_spaces == kw_no_spaces:
                return header_type
    return None


def split_into_sections(lines):
    sections = {}
    current_section = None
    
    for line in lines:
        header_type = detect_header_type(line)
        if header_type:
            current_section = header_type
            sections[current_section] = []
            continue
            
        if current_section:
            sections[current_section].append(line)
            
    return sections


def split_skills(line):
    # Split by comma, but not inside parentheses
    parts = []
    current = []
    paren_depth = 0
    for char in line:
        if char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            paren_depth -= 1
            current.append(char)
        elif char == ',' and paren_depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts


def parse_skills(skills_lines):
    skills = []
    for line in skills_lines:
        # Split by first colon if present to remove category prefix
        parts = line.split(":", 1)
        skills_part = parts[1] if len(parts) > 1 else parts[0]
        
        line_skills = split_skills(skills_part)
        for skill in line_skills:
            skill = skill.strip()
            if skill:
                skills.append(skill)
    return list(dict.fromkeys(skills))


def parse_education(education_lines):
    education = []
    current_institution = None
    current_end_year = None
    
    degree_patterns = {
        "b.e.": "B.E.",
        "b.tech": "B.Tech",
        "b.s.": "B.S.",
        "hsc": "HSC",
        "sslc": "SSLC",
        "bachelor": "Bachelor's Degree",
        "master": "Master's Degree"
    }
    
    institution_keywords = ["institute", "school", "college", "university", "academy", "highersecondary"]
    
    for line in education_lines:
        line_lower = line.lower()
        
        # Skip lines that are just grades
        if "cgpa" in line_lower or "gpa" in line_lower or "percentage" in line_lower or (re.search(r'\d+(\.\d+)?%', line) and not any(dp in line_lower for dp in degree_patterns)):
            continue
            
        # Check if this line introduces a new institution
        is_inst = any(ik in line_lower.replace(" ", "") for ik in institution_keywords)
        
        # Extract years
        years = [int(y) for y in re.findall(r'\b(?:19|20)\d{2}\b', line)]
        end_year = max(years) if years else None
        
        # Clean line of years/date ranges
        clean_line = re.sub(r'\b(?:19|20)\d{2}\b', '', line)
        clean_line = re.sub(r'[\s–\-—]+$', '', clean_line)
        clean_line = re.sub(r'^[\s–\-—]+', '', clean_line)
        clean_line = clean_line.strip()
        
        # Check if there is a degree on this line
        found_degree = None
        found_degree_key = None
        for dp_key, dp_val in degree_patterns.items():
            if dp_key in line_lower:
                found_degree = dp_val
                found_degree_key = dp_key
                break
                
        if is_inst:
            current_institution = clean_line
            current_end_year = end_year
            continue
            
        if found_degree:
            field = None
            match = re.search(rf'{found_degree_key}[\.\s]*:?\s*(.*)', line, re.IGNORECASE)
            if match:
                field = match.group(1).strip()
                field = re.sub(r'\b(?:19|20)\d{2}\b', '', field)
                field = re.sub(r'cgpa.*', '', field, flags=re.IGNORECASE)
                field = re.sub(r'\d+(\.\d+)?%', '', field)
                field = re.sub(r'[\s–\-—,]+$', '', field)
                field = re.sub(r'^[\s–\-—,]+', '', field)
                field = field.strip()
            
            entry_end_year = end_year if end_year else current_end_year
            
            education.append({
                "institution": current_institution or "Unknown Institution",
                "degree": found_degree,
                "field": field if field else None,
                "end_year": entry_end_year
            })
            
    return education


def parse_experience_header(line):
    # Remove date range
    date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})\s*[\-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|Present)'
    line_clean = re.sub(date_pattern, '', line, flags=re.IGNORECASE)
    
    line_clean = re.sub(r'[\s–\-—,\(\)]+$', '', line_clean)
    line_clean = re.sub(r'^[\s–\-—,\(\)]+', '', line_clean)
    line_clean = line_clean.strip()
    
    company_keywords = ["ltd", "pvt", "inc", "corp", "co", "technologies", "solutions", "systems", "labs", "company", "group"]
    title_keywords = ["intern", "developer", "engineer", "analyst", "specialist", "manager", "lead", "consultant", "architect", "programmer"]
    
    parts = []
    paren_parts = re.split(r'[\(\)]', line_clean)
    for p in paren_parts:
        dash_parts = re.split(r'[\-–—]', p)
        for dp in dash_parts:
            dp_clean = dp.strip()
            if dp_clean:
                parts.append(dp_clean)
                
    if len(parts) == 1:
        return parts[0], "Developer"
        
    best_company = None
    best_title = None
    
    company_scores = []
    title_scores = []
    
    for part in parts:
        part_lower = part.lower()
        c_score = sum(1 for kw in company_keywords if kw in part_lower)
        company_scores.append((c_score, part))
        
        t_score = sum(1 for kw in title_keywords if kw in part_lower)
        title_scores.append((t_score, part))
        
    company_scores.sort(key=lambda x: x[0], reverse=True)
    title_scores.sort(key=lambda x: x[0], reverse=True)
    
    if company_scores[0][1] != title_scores[0][1]:
        best_company = company_scores[0][1]
        best_title = title_scores[0][1]
    else:
        if company_scores[0][0] >= title_scores[0][0]:
            best_company = company_scores[0][1]
            other_parts = [p for p in parts if p != best_company]
            best_title = other_parts[0] if other_parts else "Developer"
        else:
            best_title = title_scores[0][1]
            other_parts = [p for p in parts if p != best_title]
            best_company = other_parts[0] if other_parts else "Unknown Company"
            
    return best_company, best_title


def parse_date_range(line):
    date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})\s*[\-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|Present)'
    match = re.search(date_pattern, line, re.IGNORECASE)
    if not match:
        return None, None
        
    start_str, end_str = match.group(1), match.group(2)
    
    def to_yyyy_mm(date_s):
        date_s = date_s.strip()
        if date_s.lower() == 'present':
            return 'Present'
        m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', date_s, re.IGNORECASE)
        y = re.search(r'\d{4}', date_s)
        if not m or not y:
            return date_s
            
        month_map = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        month_num = month_map[m.group(1).lower()[:3]]
        return f"{y.group()}-{month_num}"
        
    return to_yyyy_mm(start_str), to_yyyy_mm(end_str)


def parse_experience(experience_lines):
    experience = []
    current_entry = None
    
    date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})\s*[\-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|Present)'
    
    for line in experience_lines:
        if re.search(date_pattern, line, re.IGNORECASE):
            if current_entry:
                current_entry["summary"] = " ".join(current_entry["summary"]).strip()
                experience.append(current_entry)
                
            company, title = parse_experience_header(line)
            start, end = parse_date_range(line)
            current_entry = {
                "company": company,
                "title": title,
                "start": start,
                "end": end,
                "summary": []
            }
        else:
            if current_entry:
                # Clean line of bullet points and trailing spaces
                clean_line = re.sub(r'^[•\-\*§#\s]+', '', line)
                clean_line = clean_line.strip()
                if clean_line:
                    current_entry["summary"].append(clean_line)
                    
    if current_entry:
        current_entry["summary"] = " ".join(current_entry["summary"]).strip()
        experience.append(current_entry)
        
    return experience


def parse_location(text, lines):
    location = None
    for line in lines[:5]:
        if "coimbatore" in line.lower() or "india" in line.lower():
            location = line
            break
            
    if not location:
        if "coimbatore, tamil nadu" in text.lower():
            location = "Coimbatore, Tamil Nadu"
        elif "coimbatore, india" in text.lower():
            location = "Coimbatore, India"
        elif "coimbatore" in text.lower():
            location = "Coimbatore"
            
    return location


def parse_pdf(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    # -----------------------
    # Name
    # -----------------------

    full_name = lines[0] if lines else None

    # -----------------------
    # Email
    # -----------------------

    emails = re.findall(EMAIL_REGEX, text)

    # -----------------------
    # Phone
    # -----------------------

    phones = re.findall(PHONE_REGEX, text)

    # -----------------------
    # Split into sections
    # -----------------------
    
    sections = split_into_sections(lines)

    # -----------------------
    # Skills
    # -----------------------

    skills = parse_skills(sections.get("skills", []))

    # -----------------------
    # Education
    # -----------------------

    education = parse_education(sections.get("education", []))

    # -----------------------
    # Experience
    # -----------------------

    experience = parse_experience(sections.get("experience", []))

    # -----------------------
    # Location
    # -----------------------

    location = parse_location(text, lines)

    # -----------------------
    # Links
    # -----------------------

    links = {}

    # 1. Extract from PDF hyperlinks/annotations
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.hyperlinks:
                for hl in page.hyperlinks:
                    uri = hl.get("uri")
                    if uri:
                        if uri.startswith("mailto:") or uri.startswith("tel:"):
                            continue
                        uri_lower = uri.lower()
                        if "github.com" in uri_lower:
                            links["github"] = uri
                        elif "linkedin.com" in uri_lower:
                            links["linkedin"] = uri
                        elif "leetcode.com" in uri_lower:
                            links["leetcode"] = uri
                        elif "hackerrank.com" in uri_lower:
                            links["hackerrank"] = uri
                        else:
                            # Store first non-standard link as portfolio
                            if "portfolio" not in links:
                                links["portfolio"] = uri

    # 2. Fallback to regex on text
    if "github" not in links:
        github = re.search(
            r"(https?://)?(www\.)?github\.com/\S+",
            text,
            re.IGNORECASE
        )
        if github:
            links["github"] = github.group()

    if "linkedin" not in links:
        linkedin = re.search(
            r"(https?://)?(www\.)?linkedin\.com/\S+",
            text,
            re.IGNORECASE
        )
        if linkedin:
            links["linkedin"] = linkedin.group()

    # -----------------------
    # Build Candidate
    # -----------------------

    candidate = build_candidate(
        full_name=full_name,
        emails=emails,
        phones=phones,
        skills=skills,
        education=education,
        experience=experience,
        location=location,
        links=links,
        source="Resume PDF"
    )

    return candidate