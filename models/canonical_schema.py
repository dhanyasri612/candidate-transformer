from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Candidate(BaseModel):

    full_name: Optional[str] = None

    emails: List[str] = Field(default_factory=list)

    phones: List[str] = Field(default_factory=list)

    skills: List[str] = Field(default_factory=list)

    education: List[Dict] = Field(default_factory=list)

    experience: List[Dict] = Field(default_factory=list)

    location: Optional[str] = None

    links: Dict[str, str] = Field(default_factory=dict)

    source: Optional[str] = None

    # All sources that contributed to each field  e.g. {"emails": ["ATS JSON", "Resume PDF"]}
    provenance: Dict[str, List[str]] = Field(default_factory=dict)

    # Confidence score per field  e.g. {"emails": 0.9}
    confidence: Dict[str, float] = Field(default_factory=dict)

    # Primary (winning) source for each field value  e.g. {"location": "Resume PDF"}
    field_source: Dict[str, Optional[str]] = Field(default_factory=dict)

    github_profile: dict = Field(default_factory=dict)
