from normalizers.phone import normalize_phone
from normalizers.email import normalize_email
from normalizers.skills import normalize_skills

print(normalize_phone("+91-88259-38529"))
print(normalize_phone("88259 38529"))

print(normalize_email(" DhanyaSri@GMAIL.COM "))

print(normalize_skills([
    "React.js",
    "React",
    "ML",
    "Machine Learning",
    "NodeJS",
    "REST APIs"
]))