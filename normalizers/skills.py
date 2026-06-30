SKILL_MAP = {
    "react.js": "React",
    "react": "React",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "rest apis": "REST API",
    "rest api": "REST API",
    "javascript(es6+)": "JavaScript",
    "javascript": "JavaScript",
    "next.js": "Next.js",
    "bootstrap5": "Bootstrap",
    "recharts": "Recharts",
    "fastapi": "FastAPI",
    "restapis": "REST API",
    "machinelearningfundamentals": "Machine Learning",
    "machine learning fundamentals": "Machine Learning",
    "llms": "LLM",
    "llm": "LLM",
    "langchain": "LangChain",
    "faiss": "FAISS",
    "groq": "Groq",
    "transformers": "Transformers",
    "nlp": "NLP",
    "speecht5": "SpeechT5",
    "pypdf2": "PyPDF2",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "django": "Django",
    "flask": "Flask",
    "vscode": "VS Code",
    "vs code": "VS Code",
    "streamlit": "Streamlit",
    "render": "Render",
    "git": "Git",
    "github": "GitHub",
    "figma": "Figma",
    "cnn": "CNN",
    "rag": "RAG",
    "hugging face": "Hugging Face",
    "tensorflow": "TensorFlow",
    "python": "Python",
    "sql": "SQL",
    "java": "Java",
}


def normalize_skills(skills):
    normalized = []

    for skill in skills:
        # First remove any category prefixes if they slipped through
        skill_clean = skill.strip()
        if ":" in skill_clean:
            parts = skill_clean.split(":", 1)
            skill_clean = parts[1].strip()

        key = skill_clean.lower()
        normalized.append(SKILL_MAP.get(key, skill_clean))

    return list(dict.fromkeys(normalized))